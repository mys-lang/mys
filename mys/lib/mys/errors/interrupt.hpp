#pragma once

#include "base.hpp"

namespace mys {

class InterruptError : public Error {
public:
    String m_message;
    InterruptError()
    {
    }
    InterruptError(const String& message) : m_message(message)
    {
    }
    virtual ~InterruptError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __InterruptError final : public __Error {
public:
    __InterruptError(const mys::shared_ptr<InterruptError>& error)
        : __Error(static_cast<mys::shared_ptr<Error>>(error))
    {
    }
};

}
