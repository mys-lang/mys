#include "mys.hpp"

int one()
{
    return 1;
}

List<String> two()
{
    return List<String>({"c", "d"});
}

int main()
{
    for (int i: range(10)) {
        std::cout << "range(10): " << i << std::endl;
    }

    for (int i: range(5, 6)) {
        std::cout << "range(5, 6): " << i << std::endl;
    }

    for (int i: range(1, 10, 2)) {
        std::cout << "range(1, 10, 2): " << i << std::endl;
    }

    for (int i: range(-4, 1)) {
        std::cout << "range(-4, 1): " << i << std::endl;
    }

    for (int i: range(9, -1, -1)) {
        std::cout << "range(9, -1, -1): " << i << std::endl;
    }

    for (int i: range(100, 90, -3)) {
        std::cout << "range(100, 90, -3): " << i << std::endl;
    }

    int a = 10;
    int b = 20;
    int c = 4;

    for (int i: range(a, b, c)) {
        std::cout << "range(a, b, c): " << i << std::endl;
    }

    a = 10;
    b = 0;
    c = -3;

    for (int i: range(a, b, c)) {
        std::cout << "range(a, b, c): " << i << std::endl;
    }

    for (int i: range(one(), one() + 2, one())) {
        std::cout << "range(one(), one() + 2, one()): " << i << std::endl;
    }

    return (0);
}
