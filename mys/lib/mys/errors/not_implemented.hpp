#pragma once

#include "base.hpp"

class NotImplementedError
    : public Error, public std::enable_shared_from_this<NotImplementedError> {
public:
    String m_message;
    NotImplementedError()
    {
    }
    NotImplementedError(const String& message) : m_message(message)
    {
    }
    virtual ~NotImplementedError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __NotImplementedError final : public __Error {
public:
    __NotImplementedError(const std::shared_ptr<NotImplementedError>& error)
        : __Error(static_cast<std::shared_ptr<Error>>(error))
    {
    }
};
