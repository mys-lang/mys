#pragma once

#include "../common.hpp"
#include "number.hpp"
#include "../utils.hpp"

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

std::ostream&
operator<<(std::ostream& os, const Bytes& obj);

const Bytes& bytes_not_none(const Bytes& obj);
