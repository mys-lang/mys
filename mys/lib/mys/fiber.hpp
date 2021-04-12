#pragma once

#include "uv.h"

namespace mys {

class Fiber : public Object {
public:
    void *data_p;

    Fiber();

    virtual ~Fiber() {}

    virtual void run() = 0;

    String __str__();
};

void start(const mys::shared_ptr<Fiber>& fiber);

bool join(const mys::shared_ptr<Fiber>& fiber);

bool suspend();

void resume(const mys::shared_ptr<Fiber>& fiber);

void cancel(const mys::shared_ptr<Fiber>& fiber);

mys::shared_ptr<Fiber> current();

bool sleep(f64 seconds);

void init();

}
