#pragma once

#include "common.hpp"

namespace mys {

template <typename T> const std::shared_ptr<T>&
shared_ptr_not_none(const std::shared_ptr<T>& obj)
{
#if !defined(MYS_UNSAFE)
    if (!obj) {
        abort_is_none();
    }
#endif

    return obj;
}

template <typename T> std::shared_ptr<T>&
shared_ptr_not_none(std::shared_ptr<T>& obj)
{
#if !defined(MYS_UNSAFE)
    if (!obj) {
        abort_is_none();
    }
#endif

    return obj;
}

template<typename T> bool
is(const std::shared_ptr<T>& a, const std::shared_ptr<T>& b)
{
    return a.get() == b.get();
}

template<typename T> bool
is(const std::shared_ptr<T>& a, void *b)
{
    return a.get() == nullptr;
}

template<typename T> bool
is(void *a, const std::shared_ptr<T>& b)
{
    return b.get() == nullptr;
}

// For nullptr == nullptr
static inline bool is(void *a, void *b)
{
    return a == b;
}

}
