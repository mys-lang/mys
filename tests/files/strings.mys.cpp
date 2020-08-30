#include "mys.hpp"

String str1 = String("!");

Tuple<String, String> get()
{
    return Tuple<String, String>("Hello", str1);
}

int main()
{
    auto value = get();
    auto foo = std::get<0>(*value.m_tuple);
    auto bar = std::get<1>(*value.m_tuple);
    auto foo2 = foo;
    foo += bar;
    ASSERT(foo == "Hello!");
    ASSERT(foo == foo2);
    auto fie = String(foo.m_string->c_str());
    foo += "!";
    ASSERT(foo == "Hello!!");
    ASSERT(fie == "Hello!");
    
    return (0);
}
