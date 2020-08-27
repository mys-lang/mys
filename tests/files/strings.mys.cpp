#include "mys.hpp"

shared_string str1 = make_shared_string("!");

shared_tuple<shared_string, shared_string> get()
{
    return make_shared_tuple<shared_string, shared_string>(make_shared_string("Hello"),
                                                           str1);
}

int main()
{
    auto value = get();
    auto foo = std::get<0>(*value);
    auto bar = std::get<1>(*value);
    auto foo2 = foo;
    *foo += *bar;
    ASSERT(*foo == "Hello!");
    ASSERT(*foo == *foo2);
    auto fie = make_shared_string(*foo);
    *foo += "!";
    ASSERT(*foo == "Hello!!");
    ASSERT(*fie == "Hello!");
    
    return (0);
}
