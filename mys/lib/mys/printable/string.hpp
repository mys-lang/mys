#pragma once

#include "../common.hpp"
#include "../types/string.hpp"

class PrintString {
public:
    String m_value;

    PrintString(String value) : m_value(value) {}
};

std::ostream& operator<<(std::ostream& os, const PrintString& obj);
