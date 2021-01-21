#pragma once

#include "base.hpp"

class SystemExitError
    : public Error, public std::enable_shared_from_this<SystemExitError> {
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
    __SystemExitError(const std::shared_ptr<SystemExitError>& error)
        : __Error(static_cast<std::shared_ptr<Error>>(error))
    {
    }
};
