#pragma once

#include "base.hpp"

namespace mys {

class KeyError : public Error {
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
    __KeyError(const mys::shared_ptr<KeyError>& error)
        : __Error(static_cast<mys::shared_ptr<Error>>(error))
    {
    }
};

}
