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

class __ZeroDivisionError final : public std::exception {
public:
    std::shared_ptr<ZeroDivisionError> m_error;
    __ZeroDivisionError(const std::shared_ptr<ZeroDivisionError>& error)
        : m_error(error)
    {
    }
};


#endif