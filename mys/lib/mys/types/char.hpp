#pragma once

#include "../common.hpp"
#include "number.hpp"

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
