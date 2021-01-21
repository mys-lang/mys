#include <iostream>
#include "fiber.hpp"

namespace fiber {

struct Scheduler {
    // To ensure that only one fiber is running at a time.
    uv_mutex_t mutex;
    Fiber *current_p;
    Fiber *ready_head_p;

    Fiber *ready_pop()
    {
        Fiber *elem_p;

        elem_p = ready_head_p;

        if (elem_p == NULL) {
            std::cout << "ready_pop() NULL\n";
            exit(1);
        }

        ready_head_p = elem_p->next_p;

        return elem_p;
    }

    void ready_push(Fiber *elem_p)
    {
        Fiber *curr_p;
        Fiber *prev_p;
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

    void swap(Fiber *in_p, Fiber *out_p)
    {
        // Signal scheduled fiber to start;
        uv_cond_signal(&in_p->cond);

        // Pause current fiber.
        uv_cond_wait(&out_p->cond, &mutex);
    }

    void reschedule()
    {
        Fiber *in_p;
        Fiber *out_p;

        in_p = ready_pop();
        in_p->state = Fiber::State::CURRENT;
        out_p = self();

        if (in_p != out_p) {
            current_p = in_p;
            swap(in_p, out_p);
        }
    }
};

Fiber::Fiber()
{
    uv_cond_init(&cond);
    state = State::SUSPENDED;
    prio = 0;
}

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

static Uv *uv_fiber_p;

void suspend()
{
    Fiber *fiber_p;

    fiber_p = self();

    if (fiber_p->state == Fiber::State::RESUMED) {
        fiber_p->state = Fiber::State::READY;
        scheduler.ready_push(fiber_p);
    } else {
        fiber_p->state = Fiber::State::SUSPENDED;
    }

    scheduler.reschedule();
}

void resume(Fiber *fiber_p)
{
    if (fiber_p->state == Fiber::State::SUSPENDED) {
        fiber_p->state = Fiber::State::READY;
        scheduler.ready_push(fiber_p);
    } else {
        fiber_p->state = Fiber::State::RESUMED;
    }
}

Fiber *self()
{
    return scheduler.current_p;
}

// Fiber (currently thread) entry function.
static void spawn_fiber_main(void *arg_p)
{
    Fiber *fiber_p = (Fiber *)arg_p;

    uv_mutex_lock(&scheduler.mutex);

    if (fiber_p->state != Fiber::State::CURRENT) {
        uv_cond_wait(&fiber_p->cond, &scheduler.mutex);
    }

    try {
        fiber_p->run();
    } catch (const std::exception& e) {
        std::cout << "Fiber exited.\n";
    }

    scheduler.reschedule();
}

void spawn(Fiber *fiber_p)
{
    if (uv_thread_create(&fiber_p->thread, spawn_fiber_main, fiber_p) != 0) {
        throw std::exception();
    }

    resume(fiber_p);
}

static void sleep_complete(uv_timer_t *handle_p)
{
    resume((Fiber *)(handle_p->data));
}

void sleep(int delay)
{
    uv_timer_t handle;

    uv_timer_init(uv_default_loop(), &handle);
    handle.data = self();
    uv_timer_start(&handle, sleep_complete, delay, 0);
    resume(uv_fiber_p);
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

    scheduler.current_p = new Main();
    scheduler.ready_head_p = NULL;

    uv_fiber_p = new Uv();
    uv_fiber_p->prio = 127;
    spawn(uv_fiber_p);
}

};
