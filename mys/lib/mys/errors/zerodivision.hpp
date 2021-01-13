#ifndef __MYSERRORSZERODIVISIONHPP
#define __MYSERRORSZERODIVISIONHPP

#include "base.hpp"

class ZeroDivisionError
    : public Error, public std::enable_shared_from_this<ZeroDivisionError> {
public:
    String m_message;
    ZeroDivisionError()
    {
    }
    ZeroDivisionError(const String& message) : m_message(message)
    {
    }
    virtual ~ZeroDivisionError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __ZeroDivisionError final : public __Error {
public:
    __ZeroDivisionError(const std::shared_ptr<ZeroDivisionError>& error)
        : __Error(static_cast<std::shared_ptr<Error>>(error))
    {
    }
};

#endif
