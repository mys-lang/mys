#pragma once

#include "common.hpp"
#include "types/number.hpp"

namespace mys {

class Error;

void abort_is_none(void);
void print_traceback(void);
void print_error_traceback(const mys::shared_ptr<Error>& error,
                           std::ostream& os);

template <typename T> const mys::shared_ptr<T>&
shared_ptr_not_none(const mys::shared_ptr<T>& obj);

size_t encode_utf8(char *dst_p, i32 ch);

// Exception output.
std::ostream& operator<<(std::ostream& os, const std::exception& e);

template <typename T>
std::ostream& operator<<(std::ostream& os, const mys::shared_ptr<T>& obj)
{
    if (obj) {
        os << *obj;
    } else {
        os << "None";
    }

    return os;
}

template <typename T>
std::ostream& operator<<(std::ostream& os, const std::vector<T>& obj)
{
    const char *delim_p;

    os << "[";
    delim_p = "";

    for (auto item = obj.begin(); item != obj.end(); item++, delim_p = ", ") {
        os << delim_p << *item;
    }

    os << "]";

    return os;
}

}
