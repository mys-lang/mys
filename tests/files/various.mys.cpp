#include "mys.hpp"

int foo()
{
    return 5;
}

int V1 = ((1 << 2) / 2);

int V2 = (foo() + 1);

void bar(shared_tuple<int, shared_string>& a)
{

}

int calc(std::function<int (int, int)> callback)
{
    return callback(1, 2);
}


int add(int a, int b)
{
    return a + b;
}

class Adder {

public:
    int value;

    Adder() : value(1)
    {
    }

    int add(int a, int b)
    {
        return value + a + b;
    }
};

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
    ASSERT(calc(add) == 3);
    auto adder = Adder();
    adder.value += 1;
    ASSERT(calc(std::bind(&Adder::add,
                          adder,
                          std::placeholders::_1,
                          std::placeholders::_2)) == 5);

    return 0;
}
