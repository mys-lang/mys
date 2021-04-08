#pragma once

#include "common.hpp"

namespace mys {

// A shared pointer class for single threaded applications made
// specifically for Mys.
template<typename T>
class shared_ptr final
{
public:
    void *m_buf_p;

    shared_ptr() : m_buf_p(nullptr)
    {
    }

    shared_ptr(const shared_ptr<T> &other)
    {
        m_buf_p = other.m_buf_p;

        if (m_buf_p != nullptr) {
            count() += 1;
        }
    }

    ~shared_ptr()
    {
        if (m_buf_p != nullptr) {
            count() -= 1;

            if (count() == 0) {
                std::destroy_at(data());
                free(m_buf_p);
            }
        }
    }

    int& count() const
    {
        return *(int *)m_buf_p;
    }

    T *data() const
    {
        return (T *)((int *)m_buf_p) + 1;
    }

    T *operator->() const
    {
        return data();
    }

    bool operator==(const shared_ptr<T> &other) const
    {
        return m_buf_p == other.m_buf_p;
    }

    // To comapre to nullptr.
    bool operator==(void *other) const
    {
        return m_buf_p == other;
    }
};

template<typename T, typename... Args>
shared_ptr<T> make_shared(Args&&... args)
{
    shared_ptr<T> p;

    p.m_buf_p = malloc(sizeof(int) + sizeof(T));
    p.count() = 1;
    new(p.data()) T(std::forward<Args>(args)...);

    return p;
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
