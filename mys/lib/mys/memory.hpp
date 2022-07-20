#ifndef MYS_MEMORY_HPP
#define MYS_MEMORY_HPP

#include <memory>
#include <cstdlib>
#include <algorithm>
#include <iostream>

namespace mys {

void abort_is_none(void);
void print_traceback(void);

#ifdef MYS_MEMORY_STATISTICS
extern long long number_of_allocated_objects;
extern long long number_of_object_decrements;
extern long long number_of_object_frees;

#    define INCREMENT_NUMBER_OF_ALLOCATED_OBJECTS number_of_allocated_objects++
#    define DECREMENT_NUMBER_OF_ALLOCATED_OBJECTS number_of_allocated_objects--
#    define INCREMENT_NUMBER_OF_OBJECT_DECREMENTS number_of_object_decrements++
#    define INCREMENT_NUMBER_OF_OBJECT_FREES number_of_object_frees++
#else
#    define INCREMENT_NUMBER_OF_ALLOCATED_OBJECTS
#    define DECREMENT_NUMBER_OF_ALLOCATED_OBJECTS
#    define INCREMENT_NUMBER_OF_OBJECT_DECREMENTS
#    define INCREMENT_NUMBER_OF_OBJECT_FREES
#endif

// A shared pointer class for single threaded applications made
// specifically for Mys.
template<class T>
class shared_ptr final
{
public:
    void *m_buf_p;

    shared_ptr(void) noexcept
        : m_buf_p(nullptr)
    {
    }

    // Shared from this.
    shared_ptr(T *ptr) noexcept
    {
        m_buf_p = (((uint64_t *)ptr) - 1);
        count() += 1;
        object_count() += 1;
    }

    shared_ptr(std::nullptr_t) noexcept
        : m_buf_p(nullptr)
    {
    }

    shared_ptr(const shared_ptr<T> &other) noexcept
        : m_buf_p(other.m_buf_p)
    {
        if (m_buf_p != nullptr) {
            count() += 1;
            object_count() += 1;
        }
    }

    template<class U>
    shared_ptr(const shared_ptr<U>& ptr) noexcept
        : m_buf_p(ptr.m_buf_p)
    {
        count() += 1;
        object_count() += 1;
    }

    ~shared_ptr()
    {
        if (m_buf_p != nullptr) {
            decrement();
        }
    }

    void decrement()
    {
        INCREMENT_NUMBER_OF_OBJECT_DECREMENTS;

        if (object_count() > 0) {
            object_count() -= 1;

            if (object_count() == 0) {
                std::destroy_at(get());
            }
        }

        count() -= 1;

        if (count() == 0) {
            std::free(m_buf_p);
            DECREMENT_NUMBER_OF_ALLOCATED_OBJECTS;
            INCREMENT_NUMBER_OF_OBJECT_FREES;
        }
    }

    uint32_t& count() const noexcept
    {
        return ((uint32_t *)m_buf_p)[0];
    }

    uint32_t& object_count() const noexcept
    {
        return ((uint32_t *)m_buf_p)[1];
    }

    T *get() const noexcept
    {
        return (T *)(((uint64_t *)m_buf_p) + 1);
    }

    T *operator->() const noexcept
    {
#if !defined(MYS_UNSAFE)
        if (m_buf_p == nullptr) {
            abort_is_none();
        }
#endif

        return get();
    }

    T& operator*() const noexcept
    {
        return *get();
    }

    shared_ptr& operator=(shared_ptr other) noexcept
    {
        std::swap(m_buf_p, other.m_buf_p);

        return *this;
    }

    shared_ptr& operator=(std::nullptr_t)
    {
        if (m_buf_p != nullptr) {
            decrement();
            m_buf_p = nullptr;
        }

        return *this;
    }

    operator bool() const
    {
        return m_buf_p != nullptr;
    }

    int use_count(void) const
    {
        if (m_buf_p == nullptr) {
            return 0;
        } else {
            return count();
        }
    }
};

template<class T, class... Args>
shared_ptr<T> make_shared(Args&&... args)
{
    shared_ptr<T> p;

    p.m_buf_p = std::malloc(sizeof(uint64_t) + sizeof(T));

    if (p.m_buf_p == nullptr) {
        print_traceback();
        std::cerr << "\nPanic(message=\"Memory allocation failed.\")\n";
        abort();
    }

    p.count() = 1;
    p.object_count() = 1;

    try {
        new(p.get()) T(std::forward<Args>(args)...);
    } catch (...) {
        std::free(p.m_buf_p);
        p.m_buf_p = nullptr;

        throw;
    }

    INCREMENT_NUMBER_OF_ALLOCATED_OBJECTS;

    return p;
}

template<class T, class U>
shared_ptr<T> dynamic_pointer_cast(const shared_ptr<U>& ptr)
{
    if (ptr.m_buf_p != nullptr) {
        T *casted = dynamic_cast<T *>(ptr.get());

        if (casted != nullptr) {
            return shared_ptr<T>(casted);
        } else {
            return shared_ptr<T>();
        }
    } else {
        return shared_ptr<T>();
    }
}

template<class T>
class weak_ptr final
{
public:
    mys::shared_ptr<T> m_shared;

    weak_ptr(void) noexcept
        : m_shared(nullptr)
    {
    }

    weak_ptr(const mys::shared_ptr<T> &shared) noexcept
        : m_shared(shared)
    {
        if (m_shared) {
            m_shared.object_count() -= 1;
        }
    }

    ~weak_ptr()
    {
        if (m_shared) {
            if (m_shared.object_count() > 0) {
                m_shared.object_count() += 1;
            }
        }
    }

    weak_ptr& operator=(mys::shared_ptr<T> other) noexcept
    {
        m_shared = nullptr;

        if (other) {
            m_shared = other;
            other.object_count() -= 1;
        }

        return *this;
    }

    weak_ptr& operator=(std::nullptr_t)
    {
        if (m_shared) {
            if (m_shared.object_count() > 0) {
                m_shared.object_count() += 1;
            }

            m_shared = nullptr;
        }

        return *this;
    }

    operator bool() const
    {
        return m_shared;
    }

    mys::shared_ptr<T> lock() const noexcept
    {
        if (m_shared && m_shared.object_count() == 0) {
            print_traceback();
            std::cerr
                << "\nPanic(message=\"Cannot lock weak pointer with no object.\")\n";
            abort();
        }

        return m_shared;
    }
};

}

namespace std
{
    template<typename T> struct hash<mys::shared_ptr<T>>
    {
        std::size_t operator()(mys::shared_ptr<T> const& o) const noexcept
        {
            return o->__hash__();
        }
    };
}

namespace mys
{
    template<typename T>
    bool operator==(mys::shared_ptr<T> const& lhs, mys::shared_ptr<T> const& rhs)
    {
        return lhs->__eq__(rhs);
    };
}

namespace mys
{
    template<typename T>
    bool operator<(mys::shared_ptr<T> const& lhs, mys::shared_ptr<T> const& rhs)
    {
        return lhs->__lt__(rhs);
    };
}

#endif
