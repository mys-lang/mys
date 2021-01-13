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

class __TypeError final : public __Error {
public:
    __TypeError(const std::shared_ptr<TypeError>& error)
        : __Error(static_cast<std::shared_ptr<Error>>(error))
    {
    }
};

#endif
