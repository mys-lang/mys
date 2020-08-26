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
#include "range.hpp"

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef int8_t s8;
typedef int16_t s16;
typedef int32_t s32;
typedef int64_t s64;
typedef float f32;
typedef double f64;

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

using whoshuu::range;
