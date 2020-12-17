#pragma once

#include <iostream>
#include <vector>
#include <memory>
#include <sstream>
#include <cstring>
#include "robin_hood.hpp"

typedef int8_t i8;
typedef int16_t i16;
typedef int32_t i32;
typedef int64_t i64;
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef float f32;
typedef double f64;

class String {

public:
    std::shared_ptr<std::string> m_string;

    String() : m_string(std::make_shared<std::string>())
    {
    }

    String(const char *str) : m_string(std::make_shared<std::string>(str))
    {
    }

    String(i8 value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    String(i16 value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    String(i32 value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    String(i64 value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    String(u8 value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    String(u16 value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    String(u32 value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    String(u64 value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    String(f32 value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    String(f64 value) :
        m_string(std::make_shared<std::string>(std::to_string(value)))
    {
    }

    void operator+=(const String& other) const
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

namespace std
{
    template<> struct hash<String>
    {
        std::size_t operator()(String const& s) const noexcept
        {
            return std::hash<std::string>{}(*s.m_string);
        }
    };
}

class Exception : public std::exception {

public:
    const char *m_name_p;
    String m_message;

    Exception() : Exception("Exception")
    {
    }

    Exception(const char *name_p) : Exception(name_p, "")
    {
    }

    Exception(const char *name_p, String message) :
        m_name_p(name_p),
        m_message(message)
    {
    }

    virtual ~Exception()
    {
    }

    virtual const char *what() const noexcept
    {
        return m_message.c_str();
    }
};

std::ostream& operator<<(std::ostream& os, const Exception& e);

class TypeError : public Exception {

public:
    TypeError() : TypeError("")
    {
    }

    TypeError(String message) :
        Exception("TypeError", message)
    {
    }
};

class ValueError : public Exception {

public:

    ValueError() : ValueError("")
    {
    }

    ValueError(String message) :
        Exception("ValueError", message)
    {
    }
};

class KeyError : public Exception {

public:

    KeyError() : KeyError("")
    {
    }

    KeyError(String message) :
        Exception("KeyError", message)
    {
    }
};

class IndexError : public Exception {

public:

    IndexError() : IndexError("")
    {
    }

    IndexError(String message) :
        Exception("IndexError", message)
    {
    }
};

class NotImplementedError : public Exception {

public:
    NotImplementedError() : NotImplementedError("")
    {
    }

    NotImplementedError(String message) :
        Exception("NotImplementedError", message)
    {
    }
};

class ZeroDivisionError : public Exception {

public:
    ZeroDivisionError() : ZeroDivisionError("")
    {
    }

    ZeroDivisionError(String message) :
        Exception("ZeroDivisionError", message)
    {
    }
};

class AssertionError : public Exception {

public:
    AssertionError() : AssertionError("")
    {
    }

    AssertionError(String message) :
        Exception("AssertionError", message)
    {
    }
};

template <typename T>
std::ostream& operator<<(std::ostream& os, const std::shared_ptr<T>& obj)
{
    if (obj) {
        os << *obj;
    } else {
        os << "None";
    }

    return os;
}

template <typename T>
std::ostream& operator<<(std::ostream& os, const std::vector<T>& obj)
{
    const char *delim_p;

    os << "[";
    delim_p = "";

    for (auto item = obj.begin(); item != obj.end(); item++, delim_p = ", ") {
        os << delim_p << *item;
    }

    os << "]";

    return os;
}

struct Bool {
    bool m_value;

    Bool() : m_value(false)
    {
    }

    Bool(bool value) : m_value(value)
    {
    }

    operator bool() const
    {
        return m_value;
    }
};

std::ostream& operator<<(std::ostream& os, const Bool& obj);

// Tuples.
template<class T, size_t... I> std::ostream&
format_tuple(std::ostream& os,
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
    return format_tuple(os, tup, std::make_index_sequence<sizeof...(T)>());
}

template<class... T>
class Tuple {
public:
    std::tuple<T...> m_tuple;

    Tuple(const T&... args) : m_tuple(std::tuple<T...>(args...))
    {
    }
};

template<class... T>
std::ostream&
operator<<(std::ostream& os, const Tuple<T...>& obj)
{
    os << obj.m_tuple;

    return os;
}

// Lists.
template<typename T>
class List
{
public:
    std::vector<T> m_list;

    List() : m_list(std::vector<T>())
    {
    }

    List(std::initializer_list<T> il) : m_list(std::vector<T>(il))
    {
    }

    T get(size_t pos) const
    {
        try {
            return m_list.at(pos);
        } catch (const std::out_of_range& e) {
            throw IndexError("out of range");
        }
    }

    T& get(size_t pos)
    {
        try {
            return m_list.at(pos);
        } catch (const std::out_of_range& e) {
            throw IndexError("out of range");
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

    bool operator==(const List<T>& other) const
    {
        size_t i;

        if (m_list.size() != other.m_list.size()) {
            return false;
        }

        for (i = 0; i < m_list.size(); i++) {
            if (m_list[i] != other.m_list[i]) {
                return false;
            }
        }

        return true;
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
        T minimum;

        if (m_list.size() == 0) {
            throw ValueError("min() arg is an empty sequence");
        }

        minimum = m_list[0];

        for (auto item: m_list) {
            if (item < minimum) {
                minimum = item;
            }
        }

        return minimum;
    }

    T __max__() const
    {
        T maximum;

        if (m_list.size() == 0) {
            throw ValueError("max() arg is an empty sequence");
        }

        maximum = m_list[0];

        for (auto item: m_list) {
            if (item > maximum) {
                maximum = item;
            }
        }

        return maximum;
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
};

template <typename T> std::ostream&
operator<<(std::ostream& os, const std::shared_ptr<List<T>>& vec)
{
    const char *delim_p;

    if (vec == nullptr) {
        os << "None";
    } else {
        os << "[";
        delim_p = "";

        for (auto item = vec->begin(); item != vec->end(); item++, delim_p = ", ") {
            os << delim_p << *item;
        }

        os << "]";
    }

    return os;
}

template<typename T> std::ostream&
operator<<(std::ostream& os, const List<T>& obj)
{
    os << *obj.m_list;

    return os;
}

// Dicts.
template<typename TK, typename TV>
class Dict
{
public:
    robin_hood::unordered_map<TK, TV> m_map;

    Dict() : m_map(robin_hood::unordered_map<TK, TV>())
    {
    }

    Dict(std::initializer_list<robin_hood::pair<TK, TV>> il) :
        m_map(robin_hood::unordered_map<TK, TV>(il))
    {
    }

    // Only used to get an item, not set.
    // ToDo: Throw KeyError if missing.
    TV& operator[](const TK& key)
    {
        return m_map[key];
    }

    // Only used to get an item, not set.
    // ToDo: Throw KeyError if missing.
    TV& operator[](TK& key)
    {
        return m_map[key];
    }

    void set(const TK& key, const TV& value)
    {
        m_map[key] = value;
    }

    const TV& get(const TK& key, const TV& value)
    {
        auto it = m_map.find(key);

        if (it != m_map.end()) {
            return it->second;
        } else {
            return value;
        }
    }

    int __len__() const
    {
        return m_map.size();
    }

    bool __contains__(const TK& key) const
    {
        return m_map.count(key) > 0;
    }
};

template<class TK, class TV> std::ostream&
operator<<(std::ostream& os, const std::shared_ptr<Dict<TK, TV>>& dict)
{
    const char *delim_p;

    os << "{";
    delim_p = "";

    for (auto item = dict->m_map.begin();
         item != dict->m_map.end();
         item++, delim_p = ", ") {
        os << delim_p << item->first << ": " << item->second;
    }

    os << "}";

    return os;
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

std::ostream&
operator<<(std::ostream& os, const String& obj);

static inline String operator*(int value, const String& string)
{
    return string * value;
}

static inline String operator+(const char *value_p, const String& string)
{
    String res(value_p);

    res += string;

    return res;
}

template<typename T>
static inline List<T> operator*(int value, const List<T>& list)
{
    return list * value;
}

std::shared_ptr<List<String>> create_args(int argc, const char *argv[]);

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
        return obj->__min__();
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
        return obj->__max__();
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
    return container->__contains__(item);
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

        for (i = 0; i < size && m_pos < m_string.__len__(); i++) {
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

#define assert_eq(v1, v2)                                               \
    if (!((v1) == (v2))) {                                              \
        std::cout << "Assert: " << (v1) << " != " << (v2) << std::endl; \
                                                                        \
        throw AssertionError("assert_eq failed");                       \
    }

#define assert_ne(v1, v2)                                               \
    if (!((v1) != (v2))) {                                              \
        std::cout << "Assert: " << (v1) << " == " << (v2) << std::endl; \
                                                                        \
        throw AssertionError("assert_ne failed");                       \
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

class Object {

public:

    virtual String __str__() const
    {
        return String("Object()");
    }

    friend std::ostream&
    operator<<(std::ostream& os, const Object& obj)
    {
        os << obj.__str__();

        return os;
    }

};

/* slice(), enumerate() and range() used in for loops. */

struct Slice {
    i64 m_begin;
    i64 m_end;
    i64 m_step;

    Slice(i64 begin, i64 end, i64 step, i64 length) {
        if (step == 0) {
            throw ValueError("slice step can't be zero");
        }

        if (begin < 0) {
            begin += length;

            if (begin < 0) {
                begin = 0;
            }
        }

        if (end < 0) {
            end += length;

            if (end < 0) {
                end = 0;
            }
        }

        if (((begin < end) && (step < 0))
            || ((begin > end) && (step > 0))
            || (begin == end)) {
            begin = 0;
            end = 0;
            step = 1;
        }

        m_begin = begin;
        m_end = end;
        m_step = step;
    }

    i64 length() {
        if (m_begin <= m_end) {
            return (m_end - m_begin + m_step - 1) / m_step;
        } else {
            return (m_end - m_begin + m_step + 1) / m_step;
        }
    }
};

class OpenSlice {

public:
    i64 m_begin;

    OpenSlice(i64 begin) {
        if (begin < 0) {
            begin = 0;
        }

        m_begin = begin;
    }
};

template <typename T>
class Range {

public:
    T m_begin;
    T m_end;
    T m_step;
    T m_next;

    Range(T end) : m_begin(0), m_end(end), m_step(1) {
    }

    Range(T begin, T end) : m_begin(begin), m_end(end), m_step(1) {
    }

    Range(T begin, T end, T step) : m_begin(begin), m_end(end), m_step(step) {
    }

    void iter() {
        m_next = m_begin;
    }

    T next() {
        T next = m_next;
        m_next += m_step;
        return next;
    }

    void slice(Slice& slice) {
        T begin = (m_begin + slice.m_begin * m_step);

        if (begin > m_end) {
            begin = m_end;
        }

        m_begin = begin;
        T end = m_begin + slice.length() * slice.m_step;

        if (end > m_end) {
            end = m_end;
        }

        m_end = end;
        m_step *= slice.m_step;
    }

    void slice(OpenSlice& slice) {
        m_begin += (slice.m_begin * m_step);
    }

    void reversed() {
        T begin;
        T l;

        begin = m_begin;
        l = length();
        m_begin = begin + (l - 1) * m_step;
        m_end = m_begin - (l - 1) * m_step;

        if (m_step > 0) {
            m_end--;
        } else {
            m_end++;
        }

        m_step *= -1;
    }

    i64 length() {
        if (m_step > 0) {
            return (m_end - m_begin + m_step - 1) / m_step;
        } else {
            return (m_end - m_begin + m_step + 1) / m_step;
        }
    }
};

template <typename T>
class Enumerate {

public:
    T m_begin;
    T m_end;
    T m_step;
    T m_next;

    Enumerate(T begin, T end) {
        m_begin = begin;
        m_end = begin + end;
        m_step = 1;
    }

    void iter() {
        m_next = m_begin;
    }

    T next() {
        T next = m_next;
        m_next += m_step;
        return next;
    }

    void slice(Slice& slice) {
        T begin = (m_begin + slice.m_begin * m_step);

        if (begin > m_end) {
            begin = m_end;
        }

        m_begin = begin;
        T end = m_begin + slice.length() * slice.m_step;

        if (end > m_end) {
            end = m_end;
        }

        m_end = end;
        m_step *= slice.m_step;
    }

    void slice(OpenSlice& slice) {
        m_begin += slice.m_begin;
    }

    void reversed() {
        T begin;
        T l;

        begin = m_begin;
        l = length();
        m_begin = begin + (l - 1) * m_step;
        m_end = m_begin - (l - 1) * m_step;

        if (m_step > 0) {
            m_end--;
        } else {
            m_end++;
        }

        m_step *= -1;
    }

    i64 length() {
        if (m_step > 0) {
            return (m_end - m_begin + m_step - 1) / m_step;
        } else {
            return (m_end - m_begin + m_step + 1) / m_step;
        }
    }
};

template <typename T>
class Data {

public:
    T m_begin;
    T m_end;
    T m_step;
    T m_next;

    Data(T end) : m_begin(0), m_end(end), m_step(1) {
    }

    void iter() {
        m_next = m_begin;
    }

    T next() {
        T next = m_next;
        m_next += m_step;
        return next;
    }

    void slice(Slice& slice) {
        T begin = (m_begin + slice.m_begin * m_step);

        if (begin > m_end) {
            begin = m_end;
        }

        m_begin = begin;
        T end = m_begin + slice.length() * slice.m_step;

        if (end > m_end) {
            end = m_end;
        }

        m_end = end;
        m_step *= slice.m_step;
    }

    void slice(OpenSlice& slice) {
        m_begin += slice.m_begin;
    }

    void reversed() {
        T begin;
        T l;

        begin = m_begin;
        l = length();
        m_begin = begin + (l - 1) * m_step;
        m_end = m_begin - (l - 1) * m_step;

        if (m_step > 0) {
            m_end--;
        } else {
            m_end++;
        }

        m_step *= -1;
    }

    i64 length() {
        if (m_step > 0) {
            return (m_end - m_begin + m_step - 1) / m_step;
        } else {
            return (m_end - m_begin + m_step + 1) / m_step;
        }
    }
};
