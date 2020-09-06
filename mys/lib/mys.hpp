#pragma once

#include <iostream>
#include <cstdint>
#include <cmath>
#include <tuple>
#include <utility>
#include <vector>
#include <string>
#include <iterator>
#include <algorithm>
#include <memory>
#include <unordered_map>
#include <cassert>
#include <functional>
#include "iter.hpp"

class Exception : public std::exception {

public:
    const char *m_name_p;
    const char *m_message_p;

    Exception() : Exception("Exception")
    {
    }

    Exception(const char *name_p) : Exception(name_p, "")
    {
    }

    Exception(const char *name_p, const char *message_p) :
        m_name_p(name_p),
        m_message_p(message_p)
    {
    }

    virtual const char *what() const noexcept
    {
        return m_message_p;
    }
};

std::ostream& operator<<(std::ostream& os, const Exception& e);

class TypeError : public Exception {

public:
    TypeError() : TypeError("")
    {
    }

    TypeError(const char *message_p) :
        Exception("TypeError", message_p)
    {
    }
};

class ValueError : public Exception {

public:
    ValueError() : ValueError("")
    {
    }

    ValueError(const char *message_p) :
        Exception("ValueError", message_p)
    {
    }
};

class NotImplementedError : public Exception {

public:
    NotImplementedError() : NotImplementedError("")
    {
    }

    NotImplementedError(const char *message_p) :
        Exception("NotImplementedError", message_p)
    {
    }
};

class ZeroDivisionError : public Exception {

public:
    ZeroDivisionError() : ZeroDivisionError("")
    {
    }

    ZeroDivisionError(const char *message_p) :
        Exception("ZeroDivisionError", message_p)
    {
    }
};

class AssertionError : public Exception {

public:
    AssertionError() : AssertionError("")
    {
    }

    AssertionError(const char *message_p) :
        Exception("AssertionError", message_p)
    {
    }
};

// Tuples.
template<class T, size_t... I> std::ostream&
print_tuple(std::ostream& os,
            const T& tup,
            std::index_sequence<I...>)
{
    os << "(";
    (..., (os << (I == 0 ? "" : ", ") << std::get<I>(tup)));
    os << ")";

    return os;
}

template<class... T> std::ostream&
operator<<(std::ostream& os, const std::tuple<T...>& tup)
{
    return print_tuple(os, tup, std::make_index_sequence<sizeof...(T)>());
}

template<class... T>
class Tuple {
public:
    std::shared_ptr<std::tuple<T...>> m_tuple;

    Tuple(const T&... args) : m_tuple(std::make_shared<std::tuple<T...>>(args...))
    {
    }
};

template<class... T>
std::ostream&
operator<<(std::ostream& os, const Tuple<T...>& obj)
{
    os << *obj.m_tuple;

    return os;
}

// Lists.
template <typename T> std::ostream&
operator<<(std::ostream& os, const std::vector<T>& vec)
{
    const char *delim_p;

    os << "[";
    delim_p = "";

    for (auto item = vec.begin(); item != vec.end(); item++, delim_p = ", ") {
        os << delim_p << *item;
    }

    os << "]";

    return os;
}

template<typename T>
class List
{
public:
    std::shared_ptr<std::vector<T>> m_list;

    List() : m_list(std::make_shared<std::vector<T>>())
    {
    }

    List(std::initializer_list<T> il) : m_list(std::make_shared<std::vector<T>>(il))
    {
    }

    void push_back(const T& item)
    {
        m_list->push_back(item);
    }

    T operator[](size_t pos) const
    {
        return m_list->at(pos);
    }

    T& operator[](size_t pos)
    {
        return m_list->at(pos);
    }

    List<T> operator*(int value) const
    {
        List<T> res;
        int i;

        for (i = 0; i < value; i++) {
            for (auto item: (*m_list)) {
                res.append(item);
            }
        }

        return res;
    }

    bool operator==(const List<T>& other) const
    {
        size_t i;

        if (m_list->size() != other.m_list->size()) {
            return false;
        }

        for (i = 0; i < m_list->size(); i++) {
            if ((*m_list)[i] != (*other.m_list)[i]) {
                return false;
            }
        }

        return true;
    }

    typename std::vector<T>::iterator begin()
    {
        return m_list->begin();
    }

    typename std::vector<T>::iterator end()
    {
        return m_list->end();
    }

    typename std::vector<T>::reverse_iterator rbegin()
    {
        return m_list->rbegin();
    }

    typename std::vector<T>::reverse_iterator rend()
    {
        return m_list->rend();
    }

    bool operator!=(const List<T>& other) const
    {
        return !(*this == other);
    }

    void append(const T& item)
    {
        push_back(item);
    }

    int __len__() const
    {
        return m_list->size();
    }

    T __min__() const
    {
        T minimum;

        if (m_list->size() == 0) {
            throw ValueError("min() arg is an empty sequence");
        }

        minimum = (*m_list)[0];

        for (auto item: *m_list) {
            if (item < minimum) {
                minimum = item;
            }
        }

        return minimum;
    }

    T __max__() const
    {
        T maximum;

        if (m_list->size() == 0) {
            throw ValueError("max() arg is an empty sequence");
        }

        maximum = (*m_list)[0];

        for (auto item: *m_list) {
            if (item > maximum) {
                maximum = item;
            }
        }

        return maximum;
    }

    T __sum__() const
    {
        T sum = 0;

        for (auto item: *m_list) {
            sum += item;
        }

        return sum;
    }

    bool __contains__(const T& value) const
    {
        for (auto item: *m_list) {
            if (item == value) {
                return true;
            }
        }

        return false;
    }
};

template<typename T>
std::ostream&
operator<<(std::ostream& os, const List<T>& obj)
{
    os << *obj.m_list;

    return os;
}

// Dicts.
template<typename TK, typename TV> using Dict = std::shared_ptr<std::unordered_map<TK, TV>>;

template<class TK, class TV> std::ostream&
operator<<(std::ostream& os, const std::unordered_map<TK, TV>& map)
{
    const char *delim_p;

    os << "{";
    delim_p = "";

    for (auto item = map.begin(); item != map.end(); item++, delim_p = ", ") {
        os << delim_p << item->first << ": " << item->second;
    }

    os << "}";

    return os;
}

template<class TK, class TV> Dict<TK, TV>
MakeDict(std::initializer_list<typename std::unordered_map<TK, TV>::value_type> il)
{
    return std::make_shared<std::unordered_map<TK, TV>>(il);
}

// Integer power (a ** b).
template <typename TB, typename TE>
TB ipow(TB base, TE exp)
{
    TB result = 1;

    while (exp != 0) {
        if ((exp & 1) == 1) {
            result *= base;
        }

        exp >>= 1;
        base *= base;
    }

    return result;
}

// Exception output.
std::ostream& operator<<(std::ostream& os, const std::exception& e);

#define ASSERT(cond)                            \
    if (!(cond)) {                              \
        throw AssertionError(#cond);            \
    }

template <typename T>
auto len(T obj)
{
    if constexpr (std::is_class<T>::value) {
        return obj.__len__();
    } else {
        if constexpr (std::is_same<T, int>::value) {
            static_assert(!sizeof(T *), "Object of type 'int' has no len().");
        } else if constexpr (std::is_same<T, float>::value) {
            static_assert(!sizeof(T *), "Object of type 'float' has no len().");
        } else {
            static_assert(!sizeof(T *), "Object of unknown type has no len().");
        }

        return 0;
    }
}

class String {

public:
    std::shared_ptr<std::string> m_string;

    String() : m_string(std::make_shared<std::string>())
    {
    }

    String(const char *str) : m_string(std::make_shared<std::string>(str))
    {
    }

    String(int value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    String(float value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    String(const String &other) : m_string(other.m_string)
    {
    }

    void operator+=(const String& other)
    {
        *m_string += *other.m_string;
    }

    String operator+(const String& other)
    {
        String res(this->m_string->c_str());

        res += other;

        return res;
    }

    String operator*(int value) const
    {
        String res;
        int i;

        for (i = 0; i < value; i++) {
            res += *this;
        }

        return res;
    }

    bool operator==(const String& other) const
    {
        return *m_string == *other.m_string;
    }

    bool operator!=(const String& other) const
    {
        return *m_string != *other.m_string;
    }

    const char *c_str() const
    {
        return m_string->c_str();
    }

    int __len__() const
    {
        return m_string->size();
    }

    String __str__() const
    {
        return *this;
    }

    int __int__() const
    {
        return atoi(this->m_string->c_str());
    }
};

std::ostream&
operator<<(std::ostream& os, const String& obj);

template <typename T>
auto str(T obj)
{
    if constexpr (std::is_class<T>::value) {
        return obj.__str__();
    } else {
        String res(obj);

        return res;
    }
}

template <typename T>
auto to_int(T obj)
{
    if constexpr (std::is_class<T>::value) {
        return obj.__int__();
    } else {
        return obj;
    }
}

static inline String operator*(int value, const String& string)
{
    return string * value;
}

static inline String operator+(const char *value_p, const String& string)
{
    String res(string.c_str());

    res += value_p;

    return res;
}

template<typename T>
static inline List<T> operator*(int value, const List<T>& list)
{
    return list * value;
}

List<String> create_args(int argc, const char *argv[]);

// A text file.
class TextIO {

public:
    TextIO(const char *path_p, int mode)
    {
        std::cout << "TextIO(" << path_p << ")" << std::endl;
    }

    TextIO(String& path, int mode)
    {
        std::cout << "TextIO(" << path << ")" << std::endl;
    }

    virtual ~TextIO()
    {
        std::cout << "~TextIO()" << std::endl;
    }

    String read(int size = -1)
    {
        return String("1");
    };

    int write(String& string)
    {
        return -1;
    };
};

// A binary file.
class BinaryIO {

public:
    BinaryIO(const char *path_p, int mode)
    {
        std::cout << "BinaryIO(" << path_p << ")" << std::endl;
    }

    BinaryIO(String &path, int mode)
    {
        std::cout << "BinaryIO(" << path << ")" << std::endl;
    }

    virtual ~BinaryIO()
    {
        std::cout << "~BinaryIO()" << std::endl;
    }

    String read(int size = -1)
    {
        return String("\x01");
    }

    int write(String& string)
    {
        return -1;
    }
};

template <typename T1, typename T2, typename... Tail>
auto vmin(T1&& v1, T2&& v2, Tail&&... tail)
{
    if constexpr (sizeof...(tail) == 0) {
        return v1 < v2 ? v1 : v2;
    } else {
        return vmin(vmin(v1, v2), tail...);
    }
}

template <typename T, typename... Tail>
auto min(T&& obj, Tail&&... tail)
{
    if constexpr (sizeof...(tail) == 0) {
        return obj.__min__();
    } else {
        return vmin(obj, tail...);
    }
}

template <typename T1, typename T2, typename... Tail>
auto vmax(T1&& v1, T2&& v2, Tail&&... tail)
{
    if constexpr (sizeof...(tail) == 0) {
        return v1 > v2 ? v1 : v2;
    } else {
        return vmax(vmax(v1, v2), tail...);
    }
}

template <typename T, typename... Tail>
auto max(T&& obj, Tail&&... tail)
{
    if constexpr (sizeof...(tail) == 0) {
        return obj.__max__();
    } else {
        return vmax(obj, tail...);
    }
}

template <typename T>
auto sum(T obj)
{
    return obj.__sum__();
}

template <typename TI, typename TC>
bool contains(const TI& item, const TC& container)
{
    return container.__contains__(item);
}

using std::abs;

// A text file.
class StringIO {

public:
    String m_string;
    ssize_t m_pos;

    StringIO() : m_string(""), m_pos(0)
    {
    }

    StringIO(String& string) : m_string(string.m_string->c_str()), m_pos(0)
    {
    }

    virtual ~StringIO()
    {
    }

    String read(ssize_t size)
    {
        String res;
        ssize_t i;

        for (i = 0; i < size && m_pos < len(m_string); i++) {
            char a[2] = {(*m_string.m_string)[m_pos], '\0'};
            res += a;
            m_pos++;
        }

        return res;
    }
};

static inline String chr(int value)
{
    char buf[2] = {(char)value, '\0'};

    return String(buf);
}

template <typename T>
void assert_eq(T v1, T v2)
{
    if (!(v1 == v2)) {
        throw AssertionError("assert_eq failed");
    }
}

template <typename T>
void assert_ne(T v1, T v2)
{
    if (!(v1 != v2)) {
        throw AssertionError("assert_ne failed");
    }
}

template <typename T>
void assert_gt(T v1, T v2)
{
    if (!(v1 > v2)) {
        throw AssertionError("assert_gt failed");
    }
}

template <typename T>
void assert_ge(T v1, T v2)
{
    if (!(v1 >= v2)) {
        throw AssertionError("assert_ge failed");
    }
}

template <typename T>
void assert_lt(T v1, T v2)
{
    if (!(v1 < v2)) {
        throw AssertionError("assert_lt failed");
    }
}

template <typename T>
void assert_le(T v1, T v2)
{
    if (!(v1 <= v2)) {
        throw AssertionError("assert_le failed");
    }
}

class Test;

extern Test *tests_p;

typedef void (*test_func_t)(void);

class Test {

public:
    const char *m_name_p;
    test_func_t m_func;
    Test *m_next_p;

    Test(const char *name_p, test_func_t func) {
        m_name_p = name_p;
        m_func = func;
        m_next_p = tests_p;
        tests_p = this;
    }
};
