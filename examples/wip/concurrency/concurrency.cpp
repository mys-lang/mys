namespace fibers {
    struct Scheduler {
        Fiber *current_p;
        Fiber main;
    };

    Scheduler scheduler;

    class Fiber {
    };

    static void reschedule()
    {
        Fiber *in_p;
        Fiber *out_p;

        in_p = ready_pop();
        in_p->state = CURRENT;
        out_p = self();

        if (in_p != out_p) {
            scheduler.current_p = in_p;
            swap(in_p, out_p);
        }
    }

    void make_fiber()
    {
        scheduler.current_p = &scheduler.main;
    }

    void resume(Fiber *fiber_p)
    {
        ready_push(fiber_p);
    }

    void suspend()
    {
        reschedule();
    }

    static void entry(Fiber *fiber_p)
    {
        try {
            fiber_p->run();
        } catch {
        }
    }

    void spawn(const Fiber& fiber)
    {
        init_context();
        ready_push(fiber);
    }

    Fiber *self()
    {
        return scheduler.current_p;
    }
};

namespace uv {

    static void sleep_complete(uv_timer_t *handle_p)
    {
        fibers::resume(handle_p->data);
    }

    void sleep(u64 delay)
    {
        uv_timer_t handle;

        uv_timer_init(uv_default_loop(), &handle);
        handle.data = self();
        uv_timer_start(&handle, sleep_complete, delay, 0);
        fibers::suspend();
    }

    class File {
    public:
        int fd;

        static void open_complete(uv_fs_t *req_p)
        {
            fibers::resume(req_p->data);
        }

        File(String path)
        {
            uv_fs_t req;
            uv_fs_open(uv_default_loop(), &req, path, open_complete);
            fibers::suspend();

            if (req.result == -1) {
                throw;
            }

            fd = req.result;
        }

        static void read_complete(uv_fs_t *req_p)
        {
            fibers::resume(req_p->data);
        }

        String read(i64 count = -1;)
        {
            uv_fs_read(uv_default_loop(), read_complete);
            fibers::suspend();

            if (req.result == -1) {
            }

            return data;
        }
    };
};

class Sleeper : public fibers::Fiber {
public:
    u64 delay;

    void run()
    {
        std::cout << "Fiber run!\n";

        while (true) {
            uv::sleep(this->delay);
            std::cout << "Fiber awake!\n";
        }
    }
};

class FileReader : public fibers::Fiber {
public:
    void run()
    {
        auto f = file::open();
        std::cout << f.read();
    }
};

void package_main()
{
    std::cout << "Package main!\n";
    auto sleeper = fibers::spawn(new Sleeper(2000));
    fibers::sleep(10000);
    std::cout << "Package main done!\n";
}

void idler()
{
    package_main();
    uv_stop(uv_default_loop());
}

int main()
{
    int res = 0;

    fibers::make_fiber();

    try {
        uv_idle_init(uv_default_loop(), idler);
        uv_run(uv_default_loop(), UV_RUN_DEFAULT);
    } catch {
        res = 1;
    }

    return res;
}
