#ifndef __MYSHPP
#define __MYSHPP

#include <iostream>
#include <vector>
#include <memory>
#include <sstream>
#include <optional>

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

template <typename T> class List;

template <typename T> const std::shared_ptr<T>&
shared_ptr_not_none(const std::shared_ptr<T>& obj);

size_t encode_utf8(char *dst_p, i32 ch);

// To make str(bool) and print(bool) show True and False.
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

struct Char {
    i32 m_value;

    Char() : m_value(-1)
    {
    }

    Char(i32 value) : m_value(value)
    {
    }

    operator i32() const
    {
        return m_value;
    }

    bool operator==(const Char& other) const
    {
        return m_value == other.m_value;
    }

    bool operator!=(const Char& other) const
    {
        return m_value != other.m_value;
    }

    bool operator<(const Char& other) const
    {
        return m_value < other.m_value;
    }
};

std::ostream& operator<<(std::ostream& os, const Char& obj);

// A bytes.
class Bytes final {

public:
    std::shared_ptr<std::vector<u8>> m_bytes;

    Bytes() : m_bytes(nullptr)
    {
    }

    Bytes(char *data) : m_bytes(nullptr)
    {
    }

    Bytes(std::initializer_list<u8> il) :
        m_bytes(std::make_shared<std::vector<u8>>(il))
    {
    }

    u8& operator[](i64 index) const;

    bool operator==(const Bytes& other) const
    {
        if (m_bytes && other.m_bytes) {
            return *m_bytes == *other.m_bytes;
        } else {
            return (!m_bytes && !other.m_bytes);
        }
    }

    bool operator!=(const Bytes& other) const
    {
        return *m_bytes != *other.m_bytes;
    }

    void operator+=(const Bytes& other) const
    {
        m_bytes->insert(m_bytes->end(),
                        other.m_bytes->begin(),
                        other.m_bytes->end());
    }

    void operator+=(u8 other) const
    {
        m_bytes->push_back(other);
    }

    int __len__() const
    {
        return shared_ptr_not_none(m_bytes)->size();
    }
};

// A string.
class String final {
private:
    void strip_left_right(std::optional<const String> chars, bool left, bool right) const;
    void lower(bool capitalize) const;
    i64 find(const String& sub, std::optional<i64> start, std::optional<i64> end,
             bool reverse) const;

    enum class CaseMode { LOWER, UPPER, FOLD, CAPITALIZE };
    void set_case(CaseMode mode) const;

public:
    std::shared_ptr<std::vector<Char>> m_string;

    String() : m_string(nullptr)
    {
    }

    String(const char *str);

    String(const std::string& str) : String(str.c_str())
    {
    }

    String(std::initializer_list<Char> il) :
        m_string(std::make_shared<std::vector<Char>>(il))
    {
    }

    String(const Bytes& bytes) : m_string(nullptr)
    {
    }

    String(i8 value) : String(std::to_string(value))
    {
    }

    String(i16 value) : String(std::to_string(value))
    {
    }

    String(i32 value) : String(std::to_string(value))
    {
    }

    String(i64 value) : String(std::to_string(value))
    {
    }

    String(u8 value) : String(std::to_string(value))
    {
    }

    String(u16 value) : String(std::to_string(value))
    {
    }

    String(u32 value) : String(std::to_string(value))
    {
    }

    String(u64 value) : String(std::to_string(value))
    {
    }

    String(f32 value) : String(std::to_string(value))
    {
    }

    String(f64 value) : String(std::to_string(value))
    {
    }

    String(Bool value) : String(value ? "True" : "False")
    {
    }

    String(const Char& value) : String(std::initializer_list<Char>{value})
    {
    }

    void operator+=(const String& other) const
    {
        m_string->insert(m_string->end(),
                         other.m_string->begin(),
                         other.m_string->end());
    }

    void operator+=(const Char& other) const
    {
        m_string->push_back(other);
    }

    String operator+(const String& other);

    String operator*(int value) const;

    bool operator==(const String& other) const
    {
        if (m_string && other.m_string) {
            return *m_string == *other.m_string;
        } else {
            return (!m_string && !other.m_string);
        }
    }

    bool operator!=(const String& other) const
    {
        return !(*this == other);
    }

    bool operator<(const String& other) const
    {
        return *m_string < *other.m_string;
    }

    Bytes to_utf8() const;
    Char& get(i64 index) const;
    String get(std::optional<i64> start, std::optional<i64> end,
               i64 step) const;

    String to_lower() const;
    String to_upper() const;
    String to_casefold() const;
    String to_capitalize() const;
    Bool starts_with(const String& value) const;
    Bool ends_with(const String& value) const;
    std::shared_ptr<List<String>> split(const String& separator) const;
    String join(const std::shared_ptr<List<String>>& list) const;
    void strip(std::optional<const String> chars) const;
    void lstrip(std::optional<const String> chars) const;
    void rstrip(std::optional<const String> chars) const;
    void lower() const;
    void upper() const;
    void casefold() const;
    void capitalize() const;
    i64 find(const String& sub, std::optional<i64> start, std::optional<i64> end) const;
    i64 find(const Char& sub, std::optional<i64> start, std::optional<i64> end) const;
    i64 rfind(const String& sub, std::optional<i64> start, std::optional<i64> end) const;
    i64 rfind(const Char& sub, std::optional<i64> start, std::optional<i64> end) const;
    String cut(const Char& chr) const;
    void replace(const Char& old, const Char& _new) const;
    void replace(const String& old, const String& _new) const;
    Bool isdigit() const;
    Bool isnumeric() const;
    Bool isalpha() const;
    Bool isspace() const;

    int __len__() const;

    String __str__();

    i64 __int__() const;
};

namespace std
{
    template<> struct hash<String>
    {
        std::size_t operator()(String const& s) const noexcept
        {
            // ToDo
            return 0;
        }
    };

    template<> struct hash<Bool>
    {
        std::size_t operator()(Bool const& s) const noexcept
        {
            return s.m_value;
        }
    };
}

class Exception : public std::exception {

public:
    String m_what;
    Bytes m_what_bytes;

    Exception() : Exception("Exception")
    {
    }

    Exception(const char *name_p) : Exception(name_p, "")
    {
    }

    Exception(const char *name_p, String message);

    virtual ~Exception()
    {
    }

    virtual const char *what() const noexcept
    {
        return (char *)m_what_bytes.m_bytes->data();
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

class GeneralError : public Exception {

public:

    GeneralError() : GeneralError("")
    {
    }

    GeneralError(String message) :
        Exception("GeneralError", message)
    {
    }
};

class NoneError : public Exception {

public:

    NoneError() : NoneError("")
    {
    }

    NoneError(String message) :
        Exception("NoneError", message)
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

class SystemExitError : public Exception {

public:
    SystemExitError() : SystemExitError("")
    {
    }

    SystemExitError(String message) :
        Exception("SystemExitError", message)
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

    String __str__()
    {
        std::stringstream ss;
        ss << m_tuple;
        return String(ss.str().c_str());
    }
};

template<class... T>
std::ostream&
operator<<(std::ostream& os, const Tuple<T...>& obj)
{
    os << obj.m_tuple;

    return os;
}

template<class... T> bool
operator==(const std::shared_ptr<Tuple<T...>>& a,
           const std::shared_ptr<Tuple<T...>>& b)
{
    return shared_ptr_not_none(a)->m_tuple == shared_ptr_not_none(b)->m_tuple;
}

template<class... T> bool
operator!=(const std::shared_ptr<Tuple<T...>>& a,
           const std::shared_ptr<Tuple<T...>>& b)
{
    return !(a == b);
}

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
            throw IndexError("out of range");
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
            throw ValueError("min() arg is an empty sequence");
        }

        return *std::min_element(m_list.begin(), m_list.end());
    }

    T __max__() const
    {
        if (m_list.size() == 0) {
            throw ValueError("max() arg is an empty sequence");
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

// Dicts.
template<typename TK, typename TV>
class Dict final
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

    void __setitem__(const TK& key, const TV& value)
    {
        m_map[key] = value;
    }

    const TV& get(const TK& key, const TV& default_value)
    {
        auto it = m_map.find(key);

        if (it != m_map.end()) {
            return it->second;
        } else {
            return default_value;
        }
    }

    const TV& get(const TK& key) const
    {
        auto it = m_map.find(key);

        if (it != m_map.end()) {
            return it->second;
        } else {
            throw KeyError("key does not exist");
        }
    }

    TV& get(const TK& key)
    {
        auto it = m_map.find(key);

        if (it != m_map.end()) {
            return it->second;
        } else {
            throw KeyError("key does not exist");
        }
    }

    std::shared_ptr<List<TK>> keys() const
    {
        std::vector<TK> keys;
        for (const auto& kv : m_map) {
            keys.push_back(kv.first);
        }
        return std::make_shared<List<TK>>(keys);
    }

    std::shared_ptr<List<TV>> values() const
    {
        std::vector<TV> values;
        for (const auto& kv : m_map) {
            values.push_back(kv.second);
        }
        return std::make_shared<List<TV>>(values);
    }

    TV pop(const TK& key, const TV& def)
    {
        const auto& i = m_map.find(key);
        TV value;
        if (i == m_map.end()) {
            value = def;
        }
        else {
            value = i->second;
            m_map.erase(i);
        }
        return value;
    }

    void clear()
    {
        m_map.clear();
    }

    void update(const std::shared_ptr<Dict<TK, TV>>& other)
    {
        for (const auto& i : other->m_map) {
            m_map[i.first] = i.second;
        }
    }

    int __len__() const
    {
        return m_map.size();
    }

    bool __contains__(const TK& key) const
    {
        return m_map.contains(key);
    }

    String __str__()
    {
        std::stringstream ss;
        ss << *this;
        return String(ss.str().c_str());
    }
};

template<class TK, class TV> std::ostream&
operator<<(std::ostream& os, const Dict<TK, TV>& dict)
{
    const char *delim_p;

    os << "{";
    delim_p = "";

    for (auto item = dict.m_map.begin();
         item != dict.m_map.end();
         item++, delim_p = ", ") {
        os << delim_p << item->first << ": " << item->second;
    }

    os << "}";

    return os;
}

template<typename TK, typename TV> bool
operator==(const std::shared_ptr<Dict<TK, TV>>& a,
           const std::shared_ptr<Dict<TK, TV>>& b)
{
    if (!a && !b) {
        return true;
    } else {
        return shared_ptr_not_none(a)->m_map == shared_ptr_not_none(b)->m_map;
    }
}

template<typename TK, typename TV> bool
operator!=(const std::shared_ptr<Dict<TK, TV>>& a,
           const std::shared_ptr<Dict<TK, TV>>& b)
{
    return !(a == b);
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

std::ostream&
operator<<(std::ostream& os, const Bytes& obj);

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
auto sum(const std::shared_ptr<T>& obj)
{
    return obj->__sum__();
}

template <typename TI, typename TC>
bool contains(const TI& item, const TC& container)
{
    return container->__contains__(item);
}

using std::abs;

#define assert_eq(v1, v2)                                               \
    if (!((v1) == (v2))) {                                              \
        std::cout << "Assert: " << (v1) << " != " << (v2) << std::endl; \
                                                                        \
        throw AssertionError("assert_eq failed");                       \
    }

class Test;

extern Test *tests_head_p;
extern Test *tests_tail_p;

typedef void (*test_func_t)(void);

class Test {

public:
    const char *m_name_p;
    test_func_t m_func;
    Test *m_next_p;

    Test(const char *name_p, test_func_t func);
};

class Object {
public:
    virtual void __format__(std::ostream& os) const;
    virtual String __str__();
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

template <typename T> const std::shared_ptr<T>&
shared_ptr_not_none(const std::shared_ptr<T>& obj)
{
    if (!obj) {
        throw NoneError("object is None");
    }

    return obj;
}

const String& string_not_none(const String& obj);

const Bytes& bytes_not_none(const Bytes& obj);

template<typename TK, typename TV>
std::shared_ptr<List<std::shared_ptr<Tuple<TK, TV>>>>
create_list_from_dict(const std::shared_ptr<Dict<TK, TV>>& dict)
{
    auto list = std::make_shared<List<std::shared_ptr<Tuple<TK, TV>>>>();

    for (auto const& [key, value] : shared_ptr_not_none(dict)->m_map) {
        list->append(std::make_shared<Tuple<TK, TV>>(key, value));
    }

    return list;
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

std::ostream& operator<<(std::ostream& os, Object& obj);

class PrintString {
public:
    String m_value;

    PrintString(String value) : m_value(value) {}
};

std::ostream& operator<<(std::ostream& os, const PrintString& obj);

class PrintChar {
public:
    Char m_value;

    PrintChar(Char value) : m_value(value) {}
};

std::ostream& operator<<(std::ostream& os, const PrintChar& obj);

String input(String prompt);

String bytes_str(const Bytes& value);

String string_str(const String& value);

template <typename T>
using SharedList = std::shared_ptr<List<T>>;

template <class ...T>
using SharedTuple = std::shared_ptr<Tuple<T...>>;

template <typename TK, typename TV>
using SharedDict = std::shared_ptr<Dict<TK, TV>>;

#endif
