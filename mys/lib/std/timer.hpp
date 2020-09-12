#pragma once

#include "mys.hpp"

namespace mys::timer
{

class Timer : public Object {

public:
    Timer();

    virtual void start(float timeout);
    
    virtual void on_timeout();
};
    
}
