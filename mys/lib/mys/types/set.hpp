#pragma once

#include "../common.hpp"
#include "../errors/value.hpp"
#include "../errors/key.hpp"

template<typename T>
class Set final
{
public:
    robin_hood::unordered_set<T> m_set;

    Set() {}
    Set(const Set<T>& other) : m_set(other.m_set) {}
    Set(std::initializer_list<T> il) : m_set(il) {}
    Set(const std::vector<T>& v) : m_set(v.begin(), v.end()) {}

    bool operator==(const Set<T>& other) const
    {
        return m_set == other.m_set;
    }

    bool operator!=(const Set<T>& other) const
    {
        return m_set != other.m_set;
    }

    void add(const T& elem)
    {
        m_set.insert(elem);
    }

    void clear()
    {
        m_set.clear();
    }

    void discard(const T& elem)
    {
        auto it = m_set.find(elem);

        if (it != m_set.end()) {
            m_set.erase(it);
        }
    }

    void remove(const T& elem)
    {
        auto it = m_set.find(elem);

        if (it != m_set.end()) {
            m_set.erase(it);
        } else {
            std::make_shared<KeyError>("element does not exist")->__throw();
        }
    }


    std::shared_ptr<Set<T>> operator&(const Set<T>& other) const
    {
        std::vector<T> res(std::max(m_set.size(), other.m_set.size()));
        auto i = std::set_intersection(m_set.begin(), m_set.end(),
                                       other.m_set.begin(), other.m_set.end(),
                                       res.begin());
        res.resize(i - res.begin());
        return std::make_shared<Set<T>>(res);
    }

    std::shared_ptr<Set<T>> operator-(const Set<T>& other) const
    {
        std::vector<T> res(m_set.size());
        auto i = std::set_difference(m_set.begin(), m_set.end(),
                                     other.m_set.begin(), other.m_set.end(),
                                     res.begin());
        res.resize(i - res.begin());
        return std::make_shared<Set<T>>(res);
    }

    std::shared_ptr<Set<T>> operator|(const Set<T>& other) const
    {
        std::vector<T> res(m_set.size() + other.m_set.size());
        auto i = std::set_union(m_set.begin(), m_set.end(),
                                     other.m_set.begin(), other.m_set.end(),
                                     res.begin());
        res.resize(i - res.begin());
        return std::make_shared<Set<T>>(res);
    }

    std::shared_ptr<Set<T>> operator^(const Set<T>& other) const
    {
        std::vector<T> res(m_set.size() + other.m_set.size());
        auto i = std::set_symmetric_difference(m_set.begin(), m_set.end(),
                                               other.m_set.begin(), other.m_set.end(),
                                               res.begin());
        res.resize(i - res.begin());
        return std::make_shared<Set<T>>(res);
    }

    bool operator<(const Set<T>& other) const
    {
        if (m_set.size() >= other.m_set.size()) {
            return false;
        }
        if (*this == other) {
            return false;
        }
        std::shared_ptr<Set<T>> s = *this & other;
        if (*s != *this) {
            return false;
        }
        return true;
    }

    int __len__() const
    {
        return m_set.size();
    }

    bool __contains__(const T& value) const
    {
        return m_set.contains(value);
    }

    String __str__()
    {
        std::stringstream ss;
        ss << *this;
        return String(ss.str().c_str());
    }

    T __min__() const
    {
        if (m_set.size() == 0) {
            std::make_shared<ValueError>("min() arg is an empty sequence")->__throw();
        }

        return *std::min_element(m_set.begin(), m_set.end());
    }

    T __max__() const
    {
        if (m_set.size() == 0) {
            std::make_shared<ValueError>("max() arg is an empty sequence")->__throw();
        }

        return *std::max_element(m_set.begin(), m_set.end());
    }
};

template<typename T>
std::ostream& operator<<(std::ostream& os, const Set<T>& obj)
{
    const char *delim_p;

    os << "{";
    delim_p = "";

    for (auto item = obj.m_set.begin(); item != obj.m_set.end(); item++, delim_p = ", ") {
        os << delim_p << *item;
    }

    os << "}";

    return os;
}

template<typename T>
bool operator==(const std::shared_ptr<Set<T>>& a,
                const std::shared_ptr<Set<T>>& b)
{
    if (!a && !b) {
        return true;
    } else {
        return shared_ptr_not_none(a)->m_set == shared_ptr_not_none(b)->m_set;
    }
}

template<typename T>
bool operator<(const std::shared_ptr<Set<T>>& a,
               const std::shared_ptr<Set<T>>& b)
{
    return *shared_ptr_not_none(a) < *shared_ptr_not_none(b);
}

template<typename T>
std::shared_ptr<Set<T>> operator&(const std::shared_ptr<Set<T>>& a,
                                  const std::shared_ptr<Set<T>>& b)
{
    return *shared_ptr_not_none(a) & *shared_ptr_not_none(b);
}

template<typename T>
std::shared_ptr<Set<T>> operator&=(std::shared_ptr<Set<T>>& a,
                                   const std::shared_ptr<Set<T>>& b)
{
    a = *shared_ptr_not_none(b) & *shared_ptr_not_none(a);
    return a;
}

template<typename T>
std::shared_ptr<Set<T>> operator-(const std::shared_ptr<Set<T>>& a,
                                  const std::shared_ptr<Set<T>>& b)
{
    return *shared_ptr_not_none(a) - *shared_ptr_not_none(b);
}

template<typename T>
std::shared_ptr<Set<T>> operator-=(std::shared_ptr<Set<T>>& a,
                                   const std::shared_ptr<Set<T>>& b)
{
    a = *shared_ptr_not_none(a) - *shared_ptr_not_none(b);
    return a;
}

template<typename T>
std::shared_ptr<Set<T>> operator|(const std::shared_ptr<Set<T>>& a,
                                  const std::shared_ptr<Set<T>>& b)
{
    return *shared_ptr_not_none(a) | *shared_ptr_not_none(b);
}

template<typename T>
std::shared_ptr<Set<T>> operator|=(std::shared_ptr<Set<T>>& a,
                                  const std::shared_ptr<Set<T>>& b)
{
    a = *shared_ptr_not_none(a) | *shared_ptr_not_none(b);
    return a;
}

template<typename T>
std::shared_ptr<Set<T>> operator^(const std::shared_ptr<Set<T>>& a,
                                  const std::shared_ptr<Set<T>>& b)
{
    return *shared_ptr_not_none(a) ^ *shared_ptr_not_none(b);
}

template<typename T>
std::shared_ptr<Set<T>> operator^=(std::shared_ptr<Set<T>>& a,
                                   const std::shared_ptr<Set<T>>& b)
{
    a = *shared_ptr_not_none(a) ^ *shared_ptr_not_none(b);
    return a;
}

template <typename T>
using SharedSet = std::shared_ptr<Set<T>>;
