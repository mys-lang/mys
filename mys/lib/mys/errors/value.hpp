#ifndef __MYSERRORSVALUEHPP
#define __MYSERRORSVALUEHPP

#include "base.hpp"

class ValueError : public Error, public std::enable_shared_from_this<ValueError> {
public:
    String m_message;
    ValueError()
    {
    }
    ValueError(const String& message) : m_message(message)
    {
    }
    virtual ~ValueError()
    {
    }
    [[ noreturn ]] void __throw();
    String __str__();
};

class __ValueError final : public std::exception {
public:
    std::shared_ptr<ValueError> m_error;
    __ValueError(const std::shared_ptr<ValueError>& error) : m_error(error)
    {
    }
};

#endif