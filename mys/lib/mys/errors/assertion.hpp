#pragma once

#include "base.hpp"

class AssertionError
    : public Error, public std::enable_shared_from_this<AssertionError> {
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
    __AssertionError(const std::shared_ptr<AssertionError>& error)
        : __Error(static_cast<std::shared_ptr<Error>>(error))
    {
    }
};
