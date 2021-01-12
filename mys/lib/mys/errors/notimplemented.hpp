#ifndef __MYSERRORSNOTIMPLEMENTEDHPP
#define __MYSERRORSNOTIMPLEMENTEDHPP

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

class __NotImplementedError final : public std::exception {
public:
    std::shared_ptr<NotImplementedError> m_error;
    __NotImplementedError(const std::shared_ptr<NotImplementedError>& error)
        : m_error(error)
    {
    }
};


#endif