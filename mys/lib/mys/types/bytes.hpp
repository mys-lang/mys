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

    i64 find(const Bytes& needle,
             std::optional<i64> start,
             std::optional<i64> end) const;

    int __len__() const
    {
        return shared_ptr_not_none(m_bytes)->size();
    }

    String to_hex() const;
};

std::ostream&
operator<<(std::ostream& os, const Bytes& obj);

#if !defined(MYS_UNSAFE)
const Bytes& bytes_not_none(const Bytes& obj);
#else
static inline const Bytes& bytes_not_none(const Bytes& obj)
{
    return obj;
}
#endif

}
