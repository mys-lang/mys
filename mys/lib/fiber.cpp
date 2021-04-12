#include "mys.hpp"

namespace mys {

struct SchedulerFiber {
    enum State {
        CURRENT = 0,
        RESUMED,
        READY,
        SUSPENDED,
        STOPPED
    };

    mys::shared_ptr<Fiber> m_fiber;
    uv_thread_t thread;
    uv_cond_t cond;
    SchedulerFiber *next_p;
    SchedulerFiber *waiter_p;
    int prio;
    State state;
    uv_timer_t handle;
    TracebackEntry *traceback_top_p;
    TracebackEntry *traceback_bottom_p;
    bool cancelled;

    SchedulerFiber(const mys::shared_ptr<Fiber>& fiber)
    {
        m_fiber = fiber;
        uv_cond_init(&cond);
        state = State::SUSPENDED;
        prio = 0;
        waiter_p = NULL;
        uv_timer_init(uv_default_loop(), &handle);
        handle.data = this;
        cancelled = false;
    }
};

struct Scheduler {
    // To ensure that only one fiber is running at a time.
    uv_mutex_t mutex;
    SchedulerFiber *current_p;
    SchedulerFiber *ready_head_p;

    SchedulerFiber *ready_pop()
    {
        SchedulerFiber *elem_p;

        elem_p = ready_head_p;

        if (elem_p == NULL) {
            std::cout << "error: no ready fiber" << std::endl;
            exit(1);
        }

        ready_head_p = elem_p->next_p;

        return elem_p;
    }

    void ready_push(SchedulerFiber *elem_p)
    {
        SchedulerFiber *curr_p;
        SchedulerFiber *prev_p;
        int prio;

        elem_p->next_p = NULL;

        if (ready_head_p == NULL) {
            /* Empty list. */
            ready_head_p = elem_p;
        } else {
            /* Add in prio order, with highest prio first. */
            curr_p = ready_head_p;
            prev_p = NULL;
            prio = elem_p->prio;

            while (curr_p != NULL) {
                if (prio < curr_p->prio) {
                    /* Insert before the 'curr_p' element. */
                    if (prev_p != NULL) {
                        elem_p->next_p = prev_p->next_p;
                        prev_p->next_p = elem_p;
                    } else {
                        elem_p->next_p = ready_head_p;
                        ready_head_p = elem_p;
                    }

                    return;
                }

                prev_p = curr_p;
                curr_p = curr_p->next_p;
            }

            /* End of the list. */
            prev_p->next_p = elem_p;
        }
    }

    void swap(SchedulerFiber *in_p, SchedulerFiber *out_p, bool end)
    {
        // Signal scheduled fiber to start;
        out_p->traceback_top_p = mys::traceback_top_p;
        out_p->traceback_bottom_p = mys::traceback_bottom_p;
        uv_cond_signal(&in_p->cond);

        if (!end) {
            // Pause current fiber.
            uv_cond_wait(&out_p->cond, &mutex);
        }

        mys::traceback_top_p = out_p->traceback_top_p;
        mys::traceback_bottom_p = out_p->traceback_bottom_p;
    }

    bool reschedule(bool end = false)
    {
        SchedulerFiber *in_p;
        SchedulerFiber *out_p;

        in_p = ready_pop();
        in_p->state = SchedulerFiber::State::CURRENT;
        out_p = current_p;

        if (in_p != out_p) {
            current_p = in_p;
            swap(in_p, out_p, end);
        }

        bool cancelled = current_p->cancelled;
        current_p->cancelled = false;

        return cancelled;
    }

    bool suspend()
    {
        current_p->state = SchedulerFiber::State::SUSPENDED;

        return reschedule();
    }

    void resume(SchedulerFiber *fiber_p)
    {
        if (fiber_p->state == SchedulerFiber::State::SUSPENDED) {
            fiber_p->state = SchedulerFiber::State::READY;
            ready_push(fiber_p);
        } else {
            std::cout
                << "error: trying to resume a fiber that is not suspended"
                << std:: endl;
            exit(1);
        }
    }

    void cancel(SchedulerFiber *fiber_p)
    {
        if (fiber_p->state == SchedulerFiber::State::STOPPED) {
            return;
        }

        fiber_p->cancelled = true;

        if (fiber_p->state != SchedulerFiber::State::READY) {
            fiber_p->state = SchedulerFiber::State::READY;
            ready_push(fiber_p);
        }
    }
};

static Scheduler scheduler;

class Main final : public Fiber {
public:
    Main()
    {
    }

    void run()
    {
    }
};

class Idle final : public Fiber {
public:
    Idle()
    {
    }

    void run()
    {
        int res;

        while (true) {
            res = uv_run(uv_default_loop(), UV_RUN_ONCE);

            if ((res == 0) && (scheduler.ready_head_p == NULL)) {
                std::cout
                    << "error: all fibers suspended and no pending IO"
                    << std::endl;
                exit(1);
            }

            // The idle fiber is always ready to run (at lowest
            // priority).
            scheduler.current_p->state = SchedulerFiber::State::READY;
            scheduler.ready_push(scheduler.current_p);
            scheduler.reschedule();
        }
    }
};

static mys::shared_ptr<Main> main_fiber;
static mys::shared_ptr<Idle> idle_fiber;

bool suspend()
{
    return scheduler.suspend();
}

void resume(const mys::shared_ptr<Fiber>& fiber)
{
    scheduler.resume((SchedulerFiber *)fiber->data_p);
}

void cancel(const mys::shared_ptr<Fiber>& fiber)
{
    scheduler.cancel((SchedulerFiber *)fiber->data_p);
}

bool yield()
{
    scheduler.current_p->state = SchedulerFiber::State::READY;
    scheduler.ready_push(scheduler.current_p);

    return scheduler.reschedule();
}

mys::shared_ptr<Fiber> current()
{
    return scheduler.current_p->m_fiber;
}

// Fiber (currently thread) entry function.
static void start_fiber_main(void *arg_p)
{
    SchedulerFiber *fiber_p = (SchedulerFiber *)arg_p;

    uv_mutex_lock(&scheduler.mutex);

    if (fiber_p->state != SchedulerFiber::State::CURRENT) {
        uv_cond_wait(&fiber_p->cond, &scheduler.mutex);
    }

    __MYS_TRACEBACK_INIT();
    fiber_p->traceback_top_p = traceback_top_p;
    fiber_p->traceback_bottom_p = traceback_bottom_p;

    try {
        fiber_p->m_fiber->run();
    } catch (const __Error &e) {
        __MYS_TRACEBACK_RESTORE();
        print_error_traceback(e.m_error, std::cerr);
        std::cerr << PrintString(e.m_error->__str__()) << std::endl;
        abort();
    }

    fiber_p->state = SchedulerFiber::State::STOPPED;
    SchedulerFiber *waiter_p = fiber_p->waiter_p;

    while (waiter_p != NULL) {
        scheduler.resume(waiter_p);
        waiter_p = waiter_p->waiter_p;
    }

    fiber_p->waiter_p = NULL;
    scheduler.reschedule(true);
    uv_mutex_unlock(&scheduler.mutex);
}

static void start_detailed(SchedulerFiber *fiber_p)
{
    if (uv_thread_create(&fiber_p->thread, start_fiber_main, fiber_p) != 0) {
        throw std::exception();
    }

    scheduler.resume(fiber_p);
}

void start(const mys::shared_ptr<Fiber>& fiber)
{
    if (fiber->data_p != NULL) {
        return;
    }

    auto fiber_p = new SchedulerFiber(fiber);

    fiber->data_p = fiber_p;
    start_detailed(fiber_p);
}

bool join(const mys::shared_ptr<Fiber>& fiber)
{
    SchedulerFiber *fiber_p = (SchedulerFiber *)fiber->data_p;
    bool cancelled = false;

    if (fiber_p->state != SchedulerFiber::State::STOPPED) {
        scheduler.current_p->waiter_p = fiber_p->waiter_p;
        fiber_p->waiter_p = scheduler.current_p;
        cancelled = suspend();

        if (cancelled) {
            std::cout << "ToDo: Remove ourselves for wait list" << std::endl;
        }
    }

    return cancelled;
}

static void sleep_complete(uv_timer_t *handle_p)
{
    scheduler.resume((SchedulerFiber *)(handle_p->data));
}

bool sleep(f64 seconds)
{
    uv_timer_start(&scheduler.current_p->handle,
                   sleep_complete,
                   1000 * seconds,
                   0);

    bool cancelled = suspend();

    if (uv_is_active((uv_handle_t *)&scheduler.current_p->handle)) {
        uv_timer_stop(&scheduler.current_p->handle);
    }

    return cancelled;
}

void init()
{
    uv_mutex_init(&scheduler.mutex);
    uv_mutex_lock(&scheduler.mutex);
    scheduler.ready_head_p = NULL;

    main_fiber = mys::make_shared<Main>();
    main_fiber->data_p = new SchedulerFiber(main_fiber);
    scheduler.current_p = (SchedulerFiber *)main_fiber->data_p;
    scheduler.current_p->state = SchedulerFiber::State::CURRENT;
    scheduler.current_p->traceback_top_p = traceback_top_p;
    scheduler.current_p->traceback_bottom_p = traceback_bottom_p;

    idle_fiber = mys::make_shared<Idle>();
    auto fiber_p = new SchedulerFiber(idle_fiber);
    idle_fiber->data_p = fiber_p;
    fiber_p->prio = 127;
    start_detailed(fiber_p);
}

Fiber::Fiber()
{
    data_p = NULL;
}

String Fiber::__str__()
{
    std::stringstream ss;
    ss << "Fiber()";
    return String(ss.str().c_str());
}

}
