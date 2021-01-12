#ifndef __MYSERRORSSYSTEMEXITHPP
#define __MYSERRORSSYSTEMEXITHPP

#include "base.hpp"

class SystemExitError
    : public Error, public std::enable_shared_from_this<SystemExitError> {
public:
    String m_message;
    SystemExitError()
    {
    }
    SystemExitError(const String& message) : m_message(message)
    {
    }
    virtual ~SystemExitError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __SystemExitError final : public std::exception {
public:
    std::shared_ptr<SystemExitError> m_error;
    __SystemExitError(const std::shared_ptr<SystemExitError>& error)
        : m_error(error)
    {
    }
};

#endif
