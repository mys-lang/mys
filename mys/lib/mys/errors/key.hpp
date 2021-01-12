#ifndef __MYSERRORSKEYHPP
#define __MYSERRORSKEYHPP

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

class __KeyError final : public std::exception {
public:
    std::shared_ptr<KeyError> m_error;
    __KeyError(const std::shared_ptr<KeyError>& error) : m_error(error)
    {
    }
};


#endif