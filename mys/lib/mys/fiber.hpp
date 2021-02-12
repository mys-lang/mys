#pragma once

#include "uv.h"

namespace mys {

class Fiber : public Object {
public:
    void *data_p;

    Fiber();

    virtual void run() = 0;

    String __str__();
};

void start(const std::shared_ptr<Fiber>& fiber);

void join(const std::shared_ptr<Fiber>& fiber);

void suspend();

void resume(const std::shared_ptr<Fiber>& fiber);

std::shared_ptr<Fiber> current();

void sleep(f64 seconds);

void init();

}
