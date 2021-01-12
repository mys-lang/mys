#ifndef __MYSERRORSGENERALHPP
#define __MYSERRORSGENERALHPP

#include "base.hpp"

class GeneralError : public Error, public std::enable_shared_from_this<GeneralError> {
public:
    String m_message;
    GeneralError()
    {
    }
    GeneralError(const String& message) : m_message(message)
    {
    }
    virtual ~GeneralError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __GeneralError final : public std::exception {
public:
    std::shared_ptr<GeneralError> m_error;
    __GeneralError(const std::shared_ptr<GeneralError>& error) : m_error(error)
    {
    }
};

#endif