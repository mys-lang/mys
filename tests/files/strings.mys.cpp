#include <cassert>
#include "mys.hpp"

shared_string str1 = make_shared_string("!");

shared_tuple<shared_string, shared_string> get()
{
    return make_shared_tuple<shared_string, shared_string>(make_shared_string("Hello"),
                                                           str1);
}

int main()
{
    shared_tuple<shared_string, shared_string> value = get();
    shared_string foo = std::get<0>(*value);
    shared_string foo2 = foo;
    shared_string bar = std::get<1>(*value);
    *foo += *bar;
    assert(*foo == "Hello!");
    assert(*foo == *foo2);
    shared_string fie = make_shared_string(*foo);
    *foo += "!";
    assert(*foo == "Hello!!");
    assert(*fie == "Hello!");
    
    return (0);
}
