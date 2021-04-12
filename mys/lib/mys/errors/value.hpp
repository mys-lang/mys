#pragma once

#include "base.hpp"

namespace mys {

class ValueError : public Error {
public:
    String m_message;
    ValueError()
    {
    }
    ValueError(const String& message) : m_message(message)
    {
    }
    virtual ~ValueError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __ValueError final : public __Error {
public:
    __ValueError(const mys::shared_ptr<ValueError>& error)
        : __Error(static_cast<mys::shared_ptr<Error>>(error))
    {
    }
};

}
