#pragma once

#include "base.hpp"

namespace mys {

class SystemExitError : public Error {
public:
    String m_message;
    SystemExitError()
    {
    }
    SystemExitError(const String& message) : m_message(message)
    {
    }
    virtual ~SystemExitError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __SystemExitError final : public __Error {
public:
    __SystemExitError(const mys::shared_ptr<SystemExitError>& error)
        : __Error(static_cast<mys::shared_ptr<Error>>(error))
    {
    }
};

}
