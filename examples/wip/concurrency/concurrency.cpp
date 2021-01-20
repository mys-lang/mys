#include <iostream>
#include <uv.h>
#include <pthread.h>

namespace fiber {
class Fiber;

Fiber *uv_fiber();
};

namespace fiber {
    class Fiber {
    public:
        enum State {
            CURRENT = 0,
            RESUMED,
            READY,
            SUSPENDED,
            TERMINATED
        };

        pthread_t pthread;
        pthread_cond_t cond;
        int prio;
        State state;
        Fiber *next_p;

        Fiber()
        {
            pthread_cond_init(&cond, NULL);
            state = State::SUSPENDED;
            prio = 0;
        }

        virtual void run() = 0;
    };

    struct Scheduler {
        pthread_mutex_t mutex;
        Fiber *current_p;
        Fiber *head_p;
    };

    static Scheduler scheduler;

    static Fiber *ready_pop()
    {
        Fiber *elem_p;

        elem_p = scheduler.head_p;

        if (elem_p == NULL) {
            std::cout << "ready_pop() NULL\n";
            exit(1);
        }

        scheduler.head_p = elem_p->next_p;

        //std::cout << "ready_pop " << elem_p << "\n";

        return elem_p;
    }

    static void ready_push(Fiber *elem_p)
    {
        Fiber *curr_p;
        Fiber *prev_p;
        int prio;

        //std::cout << "ready_push " << elem_p << "\n";

        elem_p->next_p = NULL;

        if (scheduler.head_p == NULL) {
            /* Empty list. */
            scheduler.head_p = elem_p;
        } else {
            /* Add in prio order, with highest prio first. */
            curr_p = scheduler.head_p;
            prev_p = NULL;
            prio = elem_p->prio;

            while (curr_p != NULL) {
                if (prio < curr_p->prio) {
                    /* Insert before the 'curr_p' element. */
                    if (prev_p != NULL) {
                        elem_p->next_p = prev_p->next_p;
                        prev_p->next_p = elem_p;
                    } else {
                        elem_p->next_p = scheduler.head_p;
                        scheduler.head_p = elem_p;
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

    static void swap(Fiber *in_p, Fiber *out_p)
    {
        // Signal scheduled fiber to start;
        // pthread_mutex_lock(&scheduler.mutex);
        pthread_cond_signal(&in_p->cond);
        // pthread_mutex_unlock(&scheduler.mutex);

        // Pause current fiber.
        // pthread_mutex_lock(&scheduler.mutex);
        pthread_cond_wait(&out_p->cond, &scheduler.mutex);
        // pthread_mutex_unlock(&scheduler.mutex);
    }

    Fiber *self()
    {
        return scheduler.current_p;
    }

    static void reschedule()
    {
        Fiber *in_p;
        Fiber *out_p;

        in_p = ready_pop();
        in_p->state = Fiber::State::CURRENT;
        out_p = self();

        if (in_p != out_p) {
            scheduler.current_p = in_p;
            swap(in_p, out_p);
        }
    }

    void suspend()
    {
        Fiber *fiber_p;

        fiber_p = self();

        if (fiber_p->state == Fiber::State::RESUMED) {
            fiber_p->state = Fiber::State::READY;
            ready_push(fiber_p);
        } else {
            fiber_p->state = Fiber::State::SUSPENDED;
        }

        reschedule();
    }

    void resume(Fiber *fiber_p)
    {
        if (fiber_p->state == Fiber::State::SUSPENDED) {
            fiber_p->state = Fiber::State::READY;
            ready_push(fiber_p);
        } else if (fiber_p->state != Fiber::State::TERMINATED) {
            fiber_p->state = Fiber::State::RESUMED;
        }
    }

    static void sleep_complete(uv_timer_t *handle_p)
    {
        //std::cout << "sleep_complete\n";
        resume((Fiber *)(handle_p->data));
    }

    // Fiber (pthread) entry function.
    void *spawn_fiber_main(void *arg_p)
    {
        Fiber *fiber_p = (Fiber *)arg_p;

        pthread_mutex_lock(&scheduler.mutex);

        if (fiber_p->state != Fiber::State::CURRENT) {
            pthread_cond_wait(&fiber_p->cond, &scheduler.mutex);
        }

        try {
            fiber_p->run();
        } catch (const std::exception& e) {
            std::cout << "Fiber exited.\n";
        }

        reschedule();

        return NULL;
    }

    void spawn(Fiber *fiber_p)
    {
        if (pthread_create(&fiber_p->pthread,
                           NULL,
                           spawn_fiber_main,
                           fiber_p) != 0) {
            throw std::exception();
        }

        ready_push(fiber_p);
    }

    void sleep(int delay)
    {
        uv_timer_t handle;

        uv_timer_init(uv_default_loop(), &handle);
        handle.data = fiber::self();
        uv_timer_start(&handle, sleep_complete, delay, 0);
        resume(uv_fiber());
        suspend();
    }
};

class Sleeper : public fiber::Fiber {
public:
    int m_delay;
    const char *m_message_p;

    Sleeper(int delay, const char *message_p)
    {
        m_delay = delay;
        m_message_p = message_p;
    }

    void run()
    {
        while (true) {
            fiber::sleep(m_delay);
            std::cout << "Sleeper awake! " << m_message_p << "\n";
        }
    }
};

void package_main()
{
    std::cout << "Package main!\n";
    fiber::spawn(new Sleeper(1000, "1000"));
    fiber::spawn(new Sleeper(2000, "2000"));
    fiber::spawn(new Sleeper(3000, "3000"));
    fiber::sleep(10000);
    std::cout << "Package main done!\n";
}

class Main : public fiber::Fiber {
public:
    Main()
    {
    }

    void run()
    {
    }
};

class Uv : public fiber::Fiber {
public:
    Uv()
    {
    }

    void run()
    {
        //std::cout << "uv_run() 1\n";
        uv_run(uv_default_loop(), UV_RUN_ONCE);
        //std::cout << "uv_run() 2\n";

        while (true) {
            fiber::suspend();
            //std::cout << "uv_run()\n";
            uv_run(uv_default_loop(), UV_RUN_ONCE);
        }
    }
};

static Uv *uv;

namespace fiber {
    Fiber *uv_fiber()
    {
        return uv;
    }
};

int main()
{
    int res = 0;

    pthread_mutex_init(&fiber::scheduler.mutex, NULL);
    pthread_mutex_lock(&fiber::scheduler.mutex);

    fiber::scheduler.current_p = new Main();
    fiber::scheduler.head_p = NULL;

    uv = new Uv();
    uv->prio = 127;
    fiber::spawn(uv);

    package_main();

    return res;
}
