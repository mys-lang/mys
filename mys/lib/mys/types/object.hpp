#pragma once

#include "../common.hpp"
#include "string.hpp"

namespace mys {

class Object {
public:
    virtual void __format__(std::ostream& os) const;
    virtual String __str__();
    virtual bool __eq__(const mys::shared_ptr<Object>& other);
    virtual i64 __hash__();
};

std::ostream& operator<<(std::ostream& os, Object& obj);

}
