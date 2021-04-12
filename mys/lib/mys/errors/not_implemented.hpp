#pragma once

#include "base.hpp"

namespace mys {

class NotImplementedError : public Error {
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
    __NotImplementedError(const mys::shared_ptr<NotImplementedError>& error)
        : __Error(static_cast<mys::shared_ptr<Error>>(error))
    {
    }
};

}
