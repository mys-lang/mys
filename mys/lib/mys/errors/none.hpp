#pragma once

#include "base.hpp"

class NoneError : public Error, public std::enable_shared_from_this<NoneError> {
public:
    String m_message;
    NoneError()
    {
    }
    NoneError(const String& message) : m_message(message)
    {
    }
    virtual ~NoneError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __NoneError final : public __Error {
public:
    __NoneError(const std::shared_ptr<NoneError>& error)
        : __Error(static_cast<std::shared_ptr<Error>>(error))
    {
    }
};
