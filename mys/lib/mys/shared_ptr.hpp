#pragma once

#include "common.hpp"

namespace mys {

namespace shared_ptr {

// A shared pointer class for single threaded applications made
// specifically for Mys.
template<typename T>
class shared_ptr final
{
public:
    void *m_buf_p;

    shared_ptr() noexcept
        : m_buf_p(nullptr)
    {
    }

    shared_ptr(const shared_ptr<T> &other) noexcept
        : m_buf_p(other.m_buf_p)
    {
        if (m_buf_p != nullptr) {
            count() += 1;
        }
    }

    ~shared_ptr()
    {
        if (m_buf_p != nullptr) {
            decrement();
        }
    }

    void decrement()
    {
        count() -= 1;

        if (count() == 0) {
            std::destroy_at(data());
            std::free(m_buf_p);
        }
    }

    int& count() const noexcept
    {
        return *(int *)m_buf_p;
    }

    T *data() const noexcept
    {
        return (T *)((int *)m_buf_p) + 1;
    }

    T *operator->() const noexcept
    {
        return data();
    }

    bool operator==(const shared_ptr<T> &other) const noexcept
    {
        return m_buf_p == other.m_buf_p;
    }

    shared_ptr& operator=(const shared_ptr& other) noexcept
    {
        m_buf_p = other.m_buf_p;

        if (m_buf_p != nullptr) {
            count() += 1;
        }

        return *this;
    }

    shared_ptr& operator=(nullptr_t)
    {
        if (m_buf_p != nullptr) {
            decrement();
            m_buf_p = nullptr;
        }

        return *this;
    }

    bool operator==(nullptr_t) const noexcept
    {
        return m_buf_p == nullptr;
    }
};

template<typename T, typename... Args>
shared_ptr<T> make_shared(Args&&... args)
{
    shared_ptr<T> p;

    p.m_buf_p = std::malloc(sizeof(int) + sizeof(T));
    p.count() = 1;
    new(p.data()) T(std::forward<Args>(args)...);

    return p;
}

}

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
