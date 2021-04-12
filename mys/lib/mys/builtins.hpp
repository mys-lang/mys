#pragma once

#include "common.hpp"
#include "types/bytes.hpp"
#include "types/string.hpp"

namespace mys {

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
auto sum(const mys::shared_ptr<T>& obj)
{
    return obj->__sum__();
}

template <typename TI, typename TC>
bool contains(const TI& item, const mys::shared_ptr<TC>& container)
{
    return container->__contains__(item);
}

static inline bool contains(const Char& item, const String& container)
{
    return container.find(item, 0, std::nullopt) != -1;
}

static inline bool contains(const String& item, const String& container)
{
    return container.find(item, 0, std::nullopt) != -1;
}

using std::abs;

String input(String prompt);

String bytes_str(const Bytes& value);

String string_str(const String& value);

String string_with_quotes(const String& value);

String assets(const char *package_p);

String executable();

template<typename T>
static inline T denominator_not_zero(T denom)
{
#if !defined(MYS_UNSAFE)
    if (denom == 0) {
        mys::make_shared<ValueError>("cannot divide or modulo by zero")->__throw();
    }
#endif

    return denom;
}

}
