#pragma once

#include "../common.hpp"
#include "../types/char.hpp"

class PrintChar {
public:
    Char m_value;

    PrintChar(Char value) : m_value(value) {}
};

std::ostream& operator<<(std::ostream& os, const PrintChar& obj);
