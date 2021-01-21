#pragma once

#include "base.hpp"

class KeyError : public Error, public std::enable_shared_from_this<KeyError> {
public:
    String m_message;
    KeyError()
    {
    }
    KeyError(const String& message) : m_message(message)
    {
    }
    virtual ~KeyError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __KeyError final : public __Error {
public:
    __KeyError(const std::shared_ptr<KeyError>& error)
        : __Error(static_cast<std::shared_ptr<Error>>(error))
    {
    }
};
