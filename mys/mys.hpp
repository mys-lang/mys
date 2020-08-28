#pragma once

#include <iostream>
#include <cstdint>
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
#include "range.hpp"
#include "iter.hpp"

// Strings.
typedef std::shared_ptr<std::string> shared_string;

template<typename T> shared_string
make_shared_string(T &value)
{
    return std::make_shared<std::string>(value);
}

// Tuples.
template<typename... T> using shared_tuple = std::shared_ptr<std::tuple<T...>>;

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

template<class... T> shared_tuple<T...>
make_shared_tuple(const T&... args)
{
    return std::make_shared<std::tuple<T...>>(args...);
}

// Vectors.
template<typename T> using shared_vector = std::shared_ptr<std::vector<T>>;

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

template<class T> shared_vector<T>
make_shared_vector(std::initializer_list<T> il)
{
    return std::make_shared<std::vector<T>>(il);
}

// Maps.
template<typename TK, typename TV> using shared_map = std::shared_ptr<std::unordered_map<TK, TV>>;

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

template<class TK, class TV> shared_map<TK, TV>
make_shared_map(std::initializer_list<typename std::unordered_map<TK, TV>::value_type> il)
{
    return std::make_shared<std::unordered_map<TK, TV>>(il);
}

// A text file.
class TextIO {

public:
    TextIO(const char *path_p, int mode)
    {
        std::cout << "TextIO(" << path_p << ")" << std::endl;
    }

    TextIO(shared_string path, int mode)
    {
        std::cout << "TextIO(" << *path << ")" << std::endl;
    }

    virtual ~TextIO()
    {
        std::cout << "~TextIO()" << std::endl;
    }

    shared_string read(int size = -1)
    {
        return make_shared_string("1");
    };

    int write(shared_string)
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

    BinaryIO(shared_string path, int mode)
    {
        std::cout << "BinaryIO(" << *path << ")" << std::endl;
    }

    virtual ~BinaryIO()
    {
        std::cout << "~BinaryIO()" << std::endl;
    }

    shared_string read(int size = -1)
    {
        return make_shared_string("\x01");
    }

    int write(shared_string)
    {
        return -1;
    }
};

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

shared_vector<shared_string> create_args(int argc, const char *argv[]);
