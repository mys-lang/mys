#pragma once

#include "../types/object.hpp"

namespace mys {

// The Error trait that all errors must implement.
class Error : public Object {
public:
    std::vector<TracebackEntry> m_traceback;

    Error();

    virtual ~Error() {}

    // Throw the C++ exception. Needed when re-raising the exception.
    [[ noreturn ]] virtual void __throw() = 0;
};

class __Error : public std::exception {
public:
    mys::shared_ptr<Error> m_error;

    __Error(const mys::shared_ptr<Error>& error) : m_error(error)
    {
    }
};

}
