#pragma once

#include "../common.hpp"
#include "../errors/value.hpp"
#include "../errors/key.hpp"

namespace mys {

template<typename T> class Set;

template <typename T>
using SharedSet = std::shared_ptr<Set<T>>;

template<typename T>
class Set final
{
public:
    robin_hood::unordered_set<T> m_set;

    Set() {}
    Set(const Set<T>& other) : m_set(other.m_set) {}
    Set(const SharedList<T>& other) : m_set(other->m_list.begin(), other->m_list.end()) {}
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

    SharedSet<T> intersection(const SharedSet<T>& other) const
    {
        std::vector<T> res(std::max(m_set.size(), other->m_set.size()));
        auto i = std::set_intersection(m_set.begin(), m_set.end(),
                                       other->m_set.begin(), other->m_set.end(),
                                       res.begin());
        res.resize(i - res.begin());
        return std::make_shared<Set<T>>(res);
    }

    SharedSet<T> intersection_update(const SharedSet<T>& other)
    {
        auto s = intersection(other);
        m_set = s->m_set;
        return s;
    }

    SharedSet<T> difference(const SharedSet<T>& other) const
    {
        std::vector<T> res(m_set.size());
        auto i = std::set_difference(m_set.begin(), m_set.end(),
                                     other->m_set.begin(), other->m_set.end(),
                                     res.begin());
        res.resize(i - res.begin());
        return std::make_shared<Set<T>>(res);
    }

    SharedSet<T> difference_update(const SharedSet<T>& other)
    {
        auto s = difference(other);
        m_set = s->m_set;
        return s;
    }

    SharedSet<T> _union(const SharedSet<T>& other) const
    {
        std::vector<T> res(m_set.size() + other->m_set.size());
        auto i = std::set_union(m_set.begin(), m_set.end(),
                                     other->m_set.begin(), other->m_set.end(),
                                     res.begin());
        res.resize(i - res.begin());
        return std::make_shared<Set<T>>(res);
    }

    SharedSet<T> update(const SharedSet<T>& other)
    {
        auto s = _union(other);
        m_set = s->m_set;
        return s;
    }

    SharedSet<T> symmetric_difference(const SharedSet<T>& other) const
    {
        std::vector<T> res(m_set.size() + other->m_set.size());
        auto i = std::set_symmetric_difference(m_set.begin(), m_set.end(),
                                               other->m_set.begin(), other->m_set.end(),
                                               res.begin());
        res.resize(i - res.begin());
        return std::make_shared<Set<T>>(res);
    }

    SharedSet<T> symmetric_difference_update(const SharedSet<T>& other)
    {
        auto s = symmetric_difference(other);
        m_set = s->m_set;
        return s;
    }

    bool is_disjoint(const SharedSet<T>& other) const
    {
        return intersection(other)->m_set.size() == 0;
    }

    bool is_superset(const SharedSet<T>& other) const
    {
        if (m_set.size() < other->m_set.size()) {
            return false;
        }
        auto s = intersection(other);
        if (*s != *other) {
            return false;
        }
        return true;
    }

    bool is_subset(const SharedSet<T>& other) const
    {
        if (m_set.size() > other->m_set.size()) {
            return false;
        }
        auto s = intersection(other);
        if (*s != *this) {
            return false;
        }
        return true;
    }

    bool is_proper_subset(const SharedSet<T>& other) const
    {
        if (m_set.size() >= other->m_set.size()) {
            return false;
        }
        if (m_set == other->m_set) {
            return false;
        }
        auto s = intersection(other);
        if (*s != *this) {
            return false;
        }
        return true;
    }

    bool is_proper_superset(const SharedSet<T>& other) const
    {
        if (m_set.size() <= other->m_set.size()) {
            return false;
        }
        if (m_set == other->m_set) {
            return false;
        }
        auto s = intersection(other);
        if (*s != *other) {
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
bool operator==(const SharedSet<T>& a,
                const SharedSet<T>& b)
{
    if (!a && !b) {
        return true;
    } else {
        return shared_ptr_not_none(a)->m_set == shared_ptr_not_none(b)->m_set;
    }
}

template<typename T>
bool operator<(const SharedSet<T>& a,
               const SharedSet<T>& b)
{
    return a->is_proper_subset(b);
}

template<typename T>
bool operator>(const SharedSet<T>& a,
               const SharedSet<T>& b)
{
    return a->is_proper_superset(b);
}

template<typename T>
bool operator<=(const SharedSet<T>& a,
               const SharedSet<T>& b)
{
    return a->is_subset(b);
}

template<typename T>
bool operator>=(const SharedSet<T>& a,
               const SharedSet<T>& b)
{
    return a->is_superset(b);
}

template<typename T>
SharedSet<T> operator&(const SharedSet<T>& a, const SharedSet<T>& b)
{
    return a->intersection(b);
}

template<typename T>
SharedSet<T> operator&=(SharedSet<T>& a, const SharedSet<T>& b)
{
    a = b->intersection(a);
    return a;
}

template<typename T>
SharedSet<T> operator-(const SharedSet<T>& a, const SharedSet<T>& b)
{
    return a->difference(b);
}

template<typename T>
SharedSet<T> operator-=(SharedSet<T>& a, const SharedSet<T>& b)
{
    a = a->difference(b);
    return a;
}

template<typename T>
SharedSet<T> operator|(const SharedSet<T>& a, const SharedSet<T>& b)
{
    return a->_union(b);
}

template<typename T>
SharedSet<T> operator|=(SharedSet<T>& a, const SharedSet<T>& b)
{
    a = a->_union(b);
    return a;
}

template<typename T>
SharedSet<T> operator^(const SharedSet<T>& a, const SharedSet<T>& b)
{
    return a->symmetric_difference(b);
}

template<typename T>
SharedSet<T> operator^=(SharedSet<T>& a, const SharedSet<T>& b)
{
    a = a->symmetric_difference(b);
    return a;
}

}
