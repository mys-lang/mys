#pragma once

#include "../common.hpp"
#include "number.hpp"
#include "../utils.hpp"

namespace mys {

class String;

// A bytes.
class Bytes final {

public:
    mys::shared_ptr<std::vector<u8>> m_bytes;

    Bytes() : m_bytes(nullptr)
    {
    }

    Bytes(char *data) : m_bytes(nullptr)
    {
    }

    Bytes(u64 size);

    Bytes(std::initializer_list<u8> il) :
        m_bytes(mys::make_shared<std::vector<u8>>(il))
    {
    }

    Bytes(String hex);

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

    i64 find(const Bytes& needle,
             std::optional<i64> start,
             std::optional<i64> end) const;

    void reserve(i64 size) const
    {
        m_bytes->reserve(size);
    }

    void resize(i64 size) const
    {
        m_bytes->resize(size);
    }

#if !defined(MYS_UNSAFE)
    u8& get(i64 index) const;
#else
    u8& get(i64 index) const
    {
        if (index < 0) {
            index = m_bytes->size() + index;
        }

        return (*m_bytes)[index];
    }
#endif

    Bytes get(std::optional<i64> start, std::optional<i64> end,
               i64 step) const;

    i64 length() const
    {
        return shared_ptr_not_none(m_bytes)->size();
    }

    Bytes __copy__() const
    {
        return *this;
    }

    Bytes __deepcopy__() const
    {
        auto res = Bytes(m_bytes->size());

        for (auto v : *m_bytes) {
            res.m_bytes->push_back(v);
        }

        return res;
    }

    String to_hex() const;

    Bool starts_with(const Bytes& value) const;

    Bool ends_with(const Bytes& value) const;

    void copy_into(const Bytes& data, i64 start, i64 end, i64 to_start);
};

std::ostream&
operator<<(std::ostream& os, const Bytes& obj);

#if !defined(MYS_UNSAFE)
Bytes bytes_not_none(Bytes obj);
#else
static inline Bytes bytes_not_none(Bytes obj)
{
    return obj;
}
#endif

}

namespace std
{
    template<> struct hash<mys::Bytes>
    {
        std::size_t operator()(mys::Bytes const& s) const noexcept
        {
            if (s.m_bytes) {

                int p1 = 7;
                int p2 = 31;
                std::size_t hash = p1;

                for (auto v : *s.m_bytes) {
                    hash = hash * p2 + v;
                }

                return hash;
            } else {
                return 0;
            }
        }
    };
}
