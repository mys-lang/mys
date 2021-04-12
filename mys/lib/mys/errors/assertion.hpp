#pragma once

#include "base.hpp"

namespace mys {

class AssertionError : public Error {
public:
    String m_message;
    AssertionError()
    {
    }
    AssertionError(const String& message) : m_message(message)
    {
    }
    virtual ~AssertionError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __AssertionError final : public __Error {
public:
    __AssertionError(const mys::shared_ptr<AssertionError>& error)
        : __Error(static_cast<mys::shared_ptr<Error>>(error))
    {
    }
};

}
