#pragma once

#include "common.hpp"
#include "errors/none.hpp"

template <typename T> const std::shared_ptr<T>&
shared_ptr_not_none(const std::shared_ptr<T>& obj)
{
    if (!obj) {
        std::make_shared<NoneError>("object is None")->__throw();
    }

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
