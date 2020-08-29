#include "mys.hpp"

Tuple<str, String> get();

int main();

Tuple<str, String> get()
{
    return MakeTuple<todo>({"Hello", "!"});
}

int main()
{
    auto value = get();
    auto foo = std::get<0>(*value);
    auto bar = std::get<1>(*value);
    foo2 = foo;
    foo += bar;
    ASSERT(foo == "Hello!");
    ASSERT(foo2 == foo);
    auto fie = foo;
    foo += "!";
    ASSERT(foo == "Hello!!");
    ASSERT(fie == "Hello!");

    return 0;
}
