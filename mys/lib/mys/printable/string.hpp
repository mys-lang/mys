#pragma once

#include "../common.hpp"
#include "../types/string.hpp"

namespace mys {

class PrintString {
public:
    const String& m_value;

    PrintString(const String& value) : m_value(value) {}
};

std::ostream& operator<<(std::ostream& os, const PrintString& obj);

}
