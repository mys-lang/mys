#pragma once

#include "base.hpp"

class UnreachableError
    : public Error, public std::enable_shared_from_this<UnreachableError> {
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
    __UnreachableError(const std::shared_ptr<UnreachableError>& error)
        : __Error(static_cast<std::shared_ptr<Error>>(error))
    {
    }
};
