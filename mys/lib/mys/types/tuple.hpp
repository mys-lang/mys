#pragma once

#include "../common.hpp"
#include "../utils.hpp"

namespace mys {

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
operator==(const mys::shared_ptr<Tuple<T...>>& a,
           const mys::shared_ptr<Tuple<T...>>& b)
{
    return shared_ptr_not_none(a)->m_tuple == shared_ptr_not_none(b)->m_tuple;
}

template<class... T> bool
operator!=(const mys::shared_ptr<Tuple<T...>>& a,
           const mys::shared_ptr<Tuple<T...>>& b)
{
    return !(a == b);
}

template <class ...T>
using SharedTuple = mys::shared_ptr<Tuple<T...>>;

}
