#pragma once

#include "../common.hpp"
#include "string.hpp"

class Object {
public:
    virtual void __format__(std::ostream& os) const;
    virtual String __str__();
};

std::ostream& operator<<(std::ostream& os, Object& obj);
