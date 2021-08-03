#pragma once

#include "../common.hpp"
#include "number.hpp"
#include "bool.hpp"
#include "char.hpp"
#include "bytes.hpp"

namespace mys {

template <typename T> class List;
template <class... T> class Tuple;
template <class ...T> using SharedTuple = mys::shared_ptr<Tuple<T...>>;

class Regex;
class RegexMatch;

// A string.
class String final {
private:
    String strip_left_right(std::optional<const String> chars, bool left, bool right) const;
    i64 find(const String& sub, std::optional<i64> start, std::optional<i64> end,
             bool reverse) const;

    enum class CaseMode { LOWER, UPPER, FOLD, CAPITALIZE };
    String set_case(CaseMode mode) const;

public:
    typedef std::vector<Char> CharVector;
    mys::shared_ptr<CharVector> m_string;

    String() : m_string(nullptr)
    {
    }

    String(const char *str);

    String(const std::string& str) : String(str.c_str())
    {
    }

    String(std::initializer_list<Char> il) :
        m_string(mys::make_shared<CharVector>(il))
    {
    }

    String(const Bytes& bytes);

    String(const Bytes& bytes, i64 start, i64 end);

    String(i8 value, char radix = 'd') : String((i64)value, radix)
    {
    }

    String(i16 value, char radix = 'd') : String((i64)value, radix)
    {
    }

    String(i32 value, char radix = 'd') : String((i64)value, radix)
    {
    }

    String(i64 value, char radix = 'd');

    String(u8 value, char radix = 'd') : String((u64)value, radix)
    {
    }

    String(u16 value, char radix = 'd') : String((u64)value, radix)
    {
    }

    String(u32 value, char radix = 'd') : String((u64)value, radix)
    {
    }

    String(u64 value, char radix = 'd');

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

    void from_unsigned(std::stringstream& ss, u64 value, char radix);

    void append(const String& other)
    {
        m_string->insert(m_string->end(),
                         other.m_string->begin(),
                         other.m_string->end());
    }

    void append(const Char& other)
    {
        m_string->push_back(other);
    }

    void operator+=(const String& other)
    {
        m_string = mys::make_shared<CharVector>(*m_string.get());
        append(other);
    }

    void operator+=(const Char& other)
    {
        m_string = mys::make_shared<CharVector>(*m_string.get());
        append(other);
    }

    String operator+(const String& other);

    String operator*(int value) const;
    void operator*=(int value);

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

    bool operator>(const String& other) const
    {
        return !(*this <= other);
    }

    bool operator<=(const String& other) const
    {
        return (*this < other) || (*this == other);
    }

    bool operator>=(const String& other) const
    {
        return !(*this < other);
    }

    Bytes to_utf8() const;

#if !defined(MYS_UNSAFE)
    Char& get(i64 index) const;
#else
    Char& get(i64 index) const
    {
        if (index < 0) {
            index = m_string->size() + index;
        }

        return (*m_string)[index];
    }
#endif

    String get(std::optional<i64> start, std::optional<i64> end,
               i64 step) const;

    Bool starts_with(const String& value) const;
    Bool ends_with(const String& value) const;
    mys::shared_ptr<List<String>> split() const;
    mys::shared_ptr<List<String>> split(const String& separator) const;
    mys::shared_ptr<List<String>> split(const Regex& regex) const;
    String join(const mys::shared_ptr<List<String>>& list) const;
    String strip(std::optional<const String> chars) const;
    String strip_left(std::optional<const String> chars) const;
    String strip_right(std::optional<const String> chars) const;
    String lower() const;
    String upper() const;
    String casefold() const;
    String capitalize() const;
    i64 find(const String& sub, std::optional<i64> start, std::optional<i64> end) const;
    i64 find(const Char& sub, std::optional<i64> start, std::optional<i64> end) const;
    i64 find_reverse(const String& sub, std::optional<i64> start, std::optional<i64> end) const;
    i64 find_reverse(const Char& sub, std::optional<i64> start, std::optional<i64> end) const;
    SharedTuple<String, String, String> partition(const Char& chr) const;
    SharedTuple<String, String, String> partition(const String& chr) const;
    String replace(const Char& old, const Char& _new) const;
    String replace(const String& old, const String& _new) const;
    String replace(const Regex& regex, const String& replacement, int flags = 0) const;
    Bool is_digit() const;
    Bool is_numeric() const;
    Bool is_alpha() const;
    Bool is_space() const;
    RegexMatch match(const Regex& regex) const;
    int __len__() const;
    String __str__();
    i64 __int__() const;
    f64 __float__() const;
};

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

static inline String operator+(const String& string_1, const String& string_2)
{
    String res(string_1);

    res += string_2;

    return res;
}

#if !defined(MYS_UNSAFE)
const String& string_not_none(const String& obj);

String& string_not_none(String& obj);
#else
static inline const String& string_not_none(const String& obj)
{
    return obj;
}

static inline String& string_not_none(String& obj)
{
    return obj;
}
#endif
}

namespace std
{
    template<> struct hash<mys::String>
    {
        std::size_t operator()(mys::String const& s) const noexcept
        {
            if (s.m_string) {
                std::size_t hash = 0;
                int p = 53;
                int m = 1e9 + 9;
                long long power_of_p = 1;

                for (auto v : *s.m_string) {
                    hash = (hash + (v - 'a' + 1) * power_of_p) % m;
                    power_of_p = (power_of_p * p) % m;
                }

                return hash;
            } else {
                return 0;
            }
        }
    };
}
