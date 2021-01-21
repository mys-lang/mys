#pragma once

#include "../common.hpp"
#include "string.hpp"
#include "../errors/index.hpp"
#include "../errors/value.hpp"

// Lists.
template<typename T>
class List final
{
public:
    std::vector<T> m_list;

    List() : m_list(std::vector<T>())
    {
    }

    List(const std::vector<T>& list) : m_list(list)
    {
    }

    List(std::initializer_list<T> il) : m_list(std::vector<T>(il))
    {
    }

    T get(i64 pos) const
    {
        if (pos < 0) {
            pos = m_list.size() + pos;
        }

        try {
            return m_list.at(pos);
        } catch (const std::out_of_range& e) {
            std::make_shared<IndexError>("list index out of range")->__throw();
        }
    }

    T& get(i64 pos)
    {
        if (pos < 0) {
            pos = m_list.size() + pos;
        }

        try {
            return m_list.at(pos);
        } catch (const std::out_of_range& e) {
            std::make_shared<IndexError>("list index out of range")->__throw();
        }
    }

    std::shared_ptr<List<T>> operator*(int value) const
    {
        auto res = std::make_shared<List<T>>();
        int i;

        for (i = 0; i < value; i++) {
            for (auto item: m_list) {
                res->append(item);
            }
        }

        return res;
    }

    bool operator<(const List<T>& other) const
    {
        return m_list < other.m_list;
    }

    bool operator==(const List<T>& other) const
    {
        return m_list == other.m_list;
    }

    void sort()
    {
        std::sort(m_list.begin(), m_list.end());
    }

    void reverse()
    {
        std::reverse(m_list.begin(), m_list.end());
    }

    void extend(const std::shared_ptr<List<T>>& other)
    {
        m_list.reserve(m_list.size() + other->m_list.size());
        m_list.insert(m_list.end(), other->m_list.begin(), other->m_list.end());
    }

    void clear()
    {
        m_list.clear();
    }

    void insert(i64 index, const T& element)
    {
        m_list.insert(m_list.begin() + index, element);
    }

    void remove(const T& element)
    {
        auto i = std::find(m_list.begin(), m_list.end(), element);
        if (i == m_list.end()) {
            std::make_shared<ValueError>("remove argument not in list")->__throw();
        }
        m_list.erase(i);
    }

    i64 count(const T& element) const
    {
        return std::count(m_list.begin(), m_list.end(), element);
    }

    T pop(std::optional<i64> _index)
    {
        i64 index = _index.value_or(m_list.size() - 1);
        if (index < 0) {
            index += m_list.size();
        }
        if (index < 0 || index >= m_list.size()) {
            std::make_shared<IndexError>("pop index out of range")->__throw();
        }

        auto v = *(m_list.begin() + index);
        m_list.erase(m_list.begin() + index);
        return v;
    }

    typename std::vector<T>::iterator begin() const
    {
        return m_list.begin();
    }

    typename std::vector<T>::iterator end() const
    {
        return m_list.end();
    }

    typename std::vector<T>::iterator begin()
    {
        return m_list.begin();
    }

    typename std::vector<T>::iterator end()
    {
        return m_list.end();
    }

    typename std::vector<T>::reverse_iterator rbegin() const
    {
        return m_list.rbegin();
    }

    typename std::vector<T>::reverse_iterator rend() const
    {
        return m_list.rend();
    }

    typename std::vector<T>::reverse_iterator rbegin()
    {
        return m_list.rbegin();
    }

    typename std::vector<T>::reverse_iterator rend()
    {
        return m_list.rend();
    }

    bool operator!=(const List<T>& other) const
    {
        return !(*this == other);
    }

    void append(const T& item)
    {
        m_list.push_back(item);
    }

    int __len__() const
    {
        return m_list.size();
    }

    T __min__() const
    {
        if (m_list.size() == 0) {
            std::make_shared<ValueError>("min() arg is an empty sequence")->__throw();
        }

        return *std::min_element(m_list.begin(), m_list.end());
    }

    T __max__() const
    {
        if (m_list.size() == 0) {
            std::make_shared<ValueError>("max() arg is an empty sequence")->__throw();
        }

        return *std::max_element(m_list.begin(), m_list.end());
    }

    T __sum__() const
    {
        T sum = 0;

        for (auto item: m_list) {
            sum += item;
        }

        return sum;
    }

    bool __contains__(const T& value) const
    {
        for (auto item: m_list) {
            if (item == value) {
                return true;
            }
        }

        return false;
    }

    String __str__()
    {
        std::stringstream ss;
        ss << m_list;
        return String(ss.str().c_str());
    }
};

template<typename T> std::ostream&
operator<<(std::ostream& os, const List<T>& obj)
{
    os << obj.m_list;

    return os;
}

template<typename T> bool
operator==(const std::shared_ptr<List<T>>& a,
           const std::shared_ptr<List<T>>& b)
{
    if (!a && !b) {
        return true;
    } else {
        return shared_ptr_not_none(a)->m_list == shared_ptr_not_none(b)->m_list;
    }
}

template<typename T> bool
operator!=(const std::shared_ptr<List<T>>& a,
           const std::shared_ptr<List<T>>& b)
{
    return !(a == b);
}

template<typename T> std::shared_ptr<List<T>>
operator+(const std::shared_ptr<List<T>>& a,
          const std::shared_ptr<List<T>>& b)
{
    auto list = std::make_shared<List<T>>();
    auto aa = shared_ptr_not_none(a);
    auto bb = shared_ptr_not_none(b);
    list->m_list.reserve(distance(aa->m_list.begin(), aa->m_list.end())
                         + distance(bb->m_list.begin(), bb->m_list.end()));
    list->m_list.insert(list->m_list.end(), aa->m_list.begin(), aa->m_list.end());
    list->m_list.insert(list->m_list.end(), bb->m_list.begin(), bb->m_list.end());
    return list;
}

template<typename T>
bool operator<(const std::shared_ptr<List<T>>& a,
               const std::shared_ptr<List<T>>& b)
{
    return a->m_list < b->m_list;
}

template<typename T>
static inline List<T> operator*(int value, const List<T>& list)
{
    return list * value;
}

std::shared_ptr<List<String>> create_args(int argc, const char *argv[]);

template <typename T>
using SharedList = std::shared_ptr<List<T>>;
