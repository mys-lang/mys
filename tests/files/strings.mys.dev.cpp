#include "mys.hpp"

shared_tuple<str, shared_string> get()
{
    return make_shared_tuple<todo>({"Hello", "!"});
}

int main(int __argc, const char *__argv[])
{
    auto args = init_args(__argc, __argv);
    auto value = get();
    auto foo = std::get<0>(*value);
    auto bar = std::get<1>(*value);
    foo2 = foo;
    foo += bar;
    ASSERT(foo == "Hello!");
    ASSERT(foo2 == foo);
    Final fie = foo;
    foo += "!";
    ASSERT(foo == "Hello!!");
    ASSERT(fie == "Hello!");

    return 0;
}
