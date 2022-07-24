#ifndef MYS_OPTIONAL_HPP
#define MYS_OPTIONAL_HPP

#include <cstdlib>

namespace mys {

template<typename T>
class optional {
public:
    bool has_value;
    T value;

    optional()
        : has_value(false)
    {
    }

    optional(T a_value)
        : has_value(true),
          value(a_value)
    {
    }

    optional(std::nullptr_t)
        : has_value(false)
    {
    }

    operator T() const
    {
        if (!has_value) {
            std::abort();
        }
        
        return value;
    }
    
    optional& operator=(std::nullptr_t)
    {
        has_value = false;

        return *this;
    }

    optional& operator=(const optional& other)
    {
        value = other.value;
        has_value = other.has_value;

        return *this;
    }

    optional& operator=(const T& other)
    {
        has_value = true;
        value = other;

        return *this;
    }

    bool operator==(T other_value) const
    {
        if (!has_value) {
            std::abort();
        }

        return value == other_value;
    }

    bool operator==(const optional& other) const
    {
        if (has_value != other.has_value) {
            return false;
        } else if (has_value) {
            return value == other.value;
        } else {
            return true;
        }
    }

    void operator+=(T other_value)
    {
        if (has_value) {
            value += other_value;
        } else {
            std::abort();
        }
    }

    void operator-=(T other_value)
    {
        if (has_value) {
            value -= other_value;
        } else {
            std::abort();
        }
    }

    void operator*=(T other_value)
    {
        if (has_value) {
            value *= other_value;
        } else {
            std::abort();
        }
    }

    void operator/=(T other_value)
    {
        if (has_value) {
            value /= other_value;
        } else {
            std::abort();
        }
    }
};

template<typename T> bool
operator==(const mys::optional<T>& a, void *b)
{
    return a.has_value == (b != nullptr);
}

template<typename T> bool
operator!=(const mys::optional<T>& a, void *b)
{
    return a.has_value != (b != nullptr);
}

template<typename T> bool
is(const mys::optional<T>& a, const mys::optional<T>& b)
{
    return a == b;
}

template<typename T> bool
is(const mys::optional<T>& a, void *b)
{
    return a == b;
}

}

#endif
