#ifndef __MYSERRORSINDEXHPP
#define __MYSERRORSINDEXHPP

#include "base.hpp"

class IndexError : public Error, public std::enable_shared_from_this<IndexError> {
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

class __IndexError final : public std::exception {
public:
    std::shared_ptr<IndexError> m_error;
    __IndexError(const std::shared_ptr<IndexError>& error) : m_error(error)
    {
    }
};


#endif