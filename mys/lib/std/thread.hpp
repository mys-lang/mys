#pragma once

#include "mys.hpp"

namespace mys::thread
{

class Stop : public Object {

public:
    Stop(const char *reason);
};

class Thread : public Object {

public:
    Thread();

    virtual void start();
    
    virtual void stop();

    static void send_stop(std::shared_ptr<Stop> message);

    virtual void handle_stop(std::shared_ptr<Stop> message);

    static void join();
};
    
}
