#include "mys.hpp"

namespace core_fiber {

struct SchedulerFiber {
    enum State {
        CURRENT = 0,
        RESUMED,
        READY,
        SUSPENDED
    };

    std::shared_ptr<Fiber> m_fiber;
    uv_thread_t thread;
    uv_cond_t cond;
    SchedulerFiber *next_p;
    int prio;
    State state;

    SchedulerFiber(const std::shared_ptr<Fiber>& fiber)
    {
        m_fiber = fiber;
        uv_cond_init(&cond);
        state = State::SUSPENDED;
        prio = 0;
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

    void swap(SchedulerFiber *in_p, SchedulerFiber *out_p)
    {
        // Signal scheduled fiber to start;
        uv_cond_signal(&in_p->cond);

        // Pause current fiber.
        uv_cond_wait(&out_p->cond, &mutex);
    }

    void reschedule()
    {
        SchedulerFiber *in_p;
        SchedulerFiber *out_p;

        in_p = ready_pop();
        in_p->state = SchedulerFiber::State::CURRENT;
        out_p = current_p;

        if (in_p != out_p) {
            current_p = in_p;
            swap(in_p, out_p);
        }
    }

    void suspend()
    {
        SchedulerFiber *fiber_p;

        fiber_p = current_p;

        if (fiber_p->state == SchedulerFiber::State::RESUMED) {
            fiber_p->state = SchedulerFiber::State::READY;
            ready_push(fiber_p);
        } else {
            fiber_p->state = SchedulerFiber::State::SUSPENDED;
        }

        reschedule();
    }

    void resume(SchedulerFiber *fiber_p)
    {
        if (fiber_p->state == SchedulerFiber::State::SUSPENDED) {
            fiber_p->state = SchedulerFiber::State::READY;
            ready_push(fiber_p);
        } else {
            fiber_p->state = SchedulerFiber::State::RESUMED;
        }
    }
};

Scheduler scheduler;

class Uv : public Fiber {
public:
    Uv()
    {
    }

    void run()
    {
        uv_run(uv_default_loop(), UV_RUN_ONCE);

        while (true) {
            suspend();
            uv_run(uv_default_loop(), UV_RUN_ONCE);
        }
    }
};

static std::shared_ptr<Uv> uv_fiber_p;

void suspend()
{
    scheduler.suspend();
}

void resume(const std::shared_ptr<Fiber>& fiber)
{
    scheduler.resume((SchedulerFiber *)fiber->data_p);
}

void yield()
{
    scheduler.current_p->state = SchedulerFiber::State::READY;
    scheduler.ready_push(scheduler.current_p);
    scheduler.reschedule();
}

std::shared_ptr<Fiber> current()
{
    return scheduler.current_p->m_fiber;
}

// Fiber (currently thread) entry function.
static void spawn_fiber_main(void *arg_p)
{
    SchedulerFiber *fiber_p = (SchedulerFiber *)arg_p;

    uv_mutex_lock(&scheduler.mutex);

    if (fiber_p->state != SchedulerFiber::State::CURRENT) {
        uv_cond_wait(&fiber_p->cond, &scheduler.mutex);
    }

    try {
        fiber_p->m_fiber->run();
    } catch (const std::exception& e) {
    }

    scheduler.reschedule();
}

void spawn(const std::shared_ptr<Fiber>& fiber)
{
    auto fiber_p = new SchedulerFiber(fiber);

    fiber->data_p = fiber_p;

    if (uv_thread_create(&fiber_p->thread, spawn_fiber_main, fiber_p) != 0) {
        throw std::exception();
    }

    scheduler.resume(fiber_p);
}

void spawn_2(SchedulerFiber *fiber_p)
{
    if (uv_thread_create(&fiber_p->thread, spawn_fiber_main, fiber_p) != 0) {
        throw std::exception();
    }

    scheduler.resume(fiber_p);
}

static void sleep_complete(uv_timer_t *handle_p)
{
    scheduler.resume((SchedulerFiber *)(handle_p->data));
}

void sleep(f64 seconds)
{
    uv_timer_t handle;

    uv_timer_init(uv_default_loop(), &handle);
    handle.data = scheduler.current_p;
    uv_timer_start(&handle, sleep_complete, 1000 * seconds, 0);
    scheduler.resume((SchedulerFiber *)uv_fiber_p->data_p);
    suspend();
}

class Main : public Fiber {
public:
    Main()
    {
    }

    void run()
    {
    }
};

void init()
{
    uv_mutex_init(&scheduler.mutex);
    uv_mutex_lock(&scheduler.mutex);

    scheduler.current_p = new SchedulerFiber(std::make_shared<Main>());
    scheduler.current_p->m_fiber->data_p = scheduler.current_p;
    scheduler.ready_head_p = NULL;

    uv_fiber_p = std::make_shared<Uv>();
    auto fiber_p = new SchedulerFiber(uv_fiber_p);
    uv_fiber_p->data_p = fiber_p;
    fiber_p->prio = 127;
    spawn_2(fiber_p);
}

};

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
