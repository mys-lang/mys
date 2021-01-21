#pragma once

#include <uv.h>

namespace fiber {

class Fiber {
public:
    enum State {
        CURRENT = 0,
        RESUMED,
        READY,
        SUSPENDED
    };

    uv_thread_t thread;
    uv_cond_t cond;
    int prio;
    State state;
    Fiber *next_p;

    Fiber();

    virtual void run() = 0;
};

Fiber *self();

void suspend();

void resume(Fiber *fiber_p);

void yield();

void spawn(Fiber *fiber_p);

void sleep(int delay);

void init();

};
