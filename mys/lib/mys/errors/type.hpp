#ifndef __MYSERRORSTYPEHPP
#define __MYSERRORSTYPEHPP

#include "base.hpp"

class TypeError : public Error, public std::enable_shared_from_this<TypeError> {
public:
    String m_message;
    TypeError()
    {
    }
    TypeError(const String& message) : m_message(message)
    {
    }
    virtual ~TypeError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __TypeError final : public std::exception {
public:
    std::shared_ptr<TypeError> m_error;
    __TypeError(const std::shared_ptr<TypeError>& error) : m_error(error)
    {
    }
};


#endif