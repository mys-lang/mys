#pragma once

#include "base.hpp"

namespace mys {

class UnreachableError : public Error {
public:
    String m_message;
    UnreachableError()
    {
    }
    UnreachableError(const String& message) : m_message(message)
    {
    }
    virtual ~UnreachableError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __UnreachableError final : public __Error {
public:
    __UnreachableError(const mys::shared_ptr<UnreachableError>& error)
        : __Error(static_cast<mys::shared_ptr<Error>>(error))
    {
    }
};

}
