#ifndef __MYSERRORSBASEHPP
#define __MYSERRORSBASEHPP

#include "../types/object.hpp"

// The Error trait that all errors must implement.
class Error : public Object {
public:
    // Throw the C++ exception. Needed when re-raising the exception.
    [[ noreturn ]] virtual void __throw() = 0;
};

#endif
