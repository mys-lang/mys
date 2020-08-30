#include "mys.hpp"

int foo();

void bar(Tuple<int, String>& a);

String fie(String& a);

int main();

int foo()
{
    return 5;
}

int V1 = ((1 << 2) / 2);

int V2 = (foo() + 1);

void bar(Tuple<int, String>& a)
{

}

String fie(String& a)
{
    return (2 * a);
}

int main()
{
    int res = 0;
    if (true) {
        res = 1;
    }
    ASSERT(res == 1);
    if (false) {
        res = 2;
    } else {
        res = 3;
    }
    ASSERT(res == 3);
    if (false) {
        res = 4;
    } else {
        if (false) {
            res = 5;
        } else {
            if (true) {
                res = 6;
            } else {
                res = 7;
            }
        }
    }
    ASSERT(res == 6);
    try {
        try {
            throw TypeError("foo");
        } catch (ValueError& e) {
            res = 8;
        } catch (TypeError& e) {
            std::cout << e << std::endl;
            res = 9;
        }
        ASSERT(res == 9);
        std::cout << "finally" << std::endl;
        res = 10;
    } catch (...) {
        ASSERT(res == 9);
        std::cout << "finally" << std::endl;
        res = 10;
        throw;
    }
    ASSERT(res == 10);
    int a = 5;
    try {
        try {
            for (auto i: range(5)) {
                std::cout << "i, a, i * a:" << " " << i << " " << a << " " << (i * a) << std::endl;
            }
            throw ValueError();
        } catch (ValueError& e) {
            res = 11;
            std::cout << e << std::endl;
            throw;
        }
        throw TypeError();
    } catch (ValueError& e) {
        ASSERT(res == 11);
        std::cout << e << std::endl;
        res = 12;
    }
    ASSERT(res == 12);
    try {
        throw ValueError();
    } catch (std::exception& e) {
        res = 13;
        std::cout << "Any" << std::endl;
    }
    ASSERT(res == 13);
    try {
        ASSERT(false);
    } catch (AssertionError& e) {
        res = 14;
        std::cout << e << std::endl;
    }
    ASSERT(res == 14);
    ASSERT(V1 == 2);
    ASSERT(V2 == 6);
    String s("hello");
    std::cout << "s:" << " " << s << " " << len(s) << " " << str(s) << std::endl;
    ASSERT(len(s) == 5);
    ASSERT(str(s) == s);
    ASSERT(s == "hello");
    ASSERT(s != "hello!");
    String t(s);
    ASSERT(s == t);
    t += "!";
    ASSERT(t == "hello!");
    ASSERT(s == t);
    ASSERT(str(1) == "1");
    ASSERT(str(1.0f) == "1.000000");
    int u = -5000;
    String v(str(u));
    ASSERT(v == "-5000");
    ASSERT((4 * v) == "-5000-5000-5000-5000");
    ASSERT((v * 3) == "-5000-5000-5000");
    ASSERT((v + v) == "-5000-5000");
    ASSERT(fie(v) == "-5000-5000");
    auto w = List<int>({});
    std::cout << "w:" << " " << w << std::endl;
    ASSERT(len(w) == 0);
    w.append(5);
    w.append(1);
    std::cout << "w:" << " " << w << std::endl;
    ASSERT(len(w) == 2);
    auto x = List<int>({5, 1, 5, 1});
    ASSERT(w != x);
    ASSERT((2 * w) == x);
    ASSERT(len((2 * w)) == 4);
    res = 0;
    try {
        res = 1;
        ASSERT(res == 1);
        res = 2;
    } catch (...) {
        ASSERT(res == 1);
        res = 2;
        throw;
    }
    ASSERT(res == 2);
    // mys-embedded-c++ start
    int vv = atoi("2");
    // mys-embedded-c++ stop;
    ASSERT(vv == 2);

    return 0;
}
