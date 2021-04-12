#pragma once

#include "base.hpp"

namespace mys {

class IndexError : public Error {
public:
    String m_message;
    IndexError()
    {
    }
    IndexError(const String& message) : m_message(message)
    {
    }
    virtual ~IndexError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __IndexError final : public __Error {
public:
    __IndexError(const mys::shared_ptr<IndexError>& error)
        : __Error(static_cast<mys::shared_ptr<Error>>(error))
    {
    }
};

}
