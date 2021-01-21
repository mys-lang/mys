#pragma once

#include "uv.h"

namespace fiber {

class Fiber {
public:
    void *data_p;

    Fiber();

    virtual void run() = 0;
};

std::shared_ptr<Fiber> current();

void suspend();

void resume(const std::shared_ptr<Fiber>& fiber);

void yield();

void spawn(const std::shared_ptr<Fiber>& fiber);

void sleep(f64 delay);

void init();

};
