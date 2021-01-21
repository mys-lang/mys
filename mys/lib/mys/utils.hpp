#pragma once

#include "common.hpp"
#include "types/number.hpp"

template <typename T> const std::shared_ptr<T>&
shared_ptr_not_none(const std::shared_ptr<T>& obj);

size_t encode_utf8(char *dst_p, i32 ch);

// Exception output.
std::ostream& operator<<(std::ostream& os, const std::exception& e);

template <typename T>
std::ostream& operator<<(std::ostream& os, const std::shared_ptr<T>& obj)
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
