#include "mys.hpp"

int one();

List<String> two();

int main();

int one()
{
    return 1;
}

List<String> two()
{
    /* mys-embedded-c++ start */
    return List<String>({"c", "d"});
    /* mys-embedded-c++ stop */;
}

int main()
{
    for (auto i: range(10)) {
        std::cout << "range(10):" << " " << i << std::endl;
    }
    for (auto i: range(5, 6)) {
        std::cout << "range(5, 6):" << " " << i << std::endl;
    }
    for (auto i: range(1, 10, 2)) {
        std::cout << "range(1, 10, 2):" << " " << i << std::endl;
    }
    for (auto i: range(-4, 1)) {
        std::cout << "range(-4, 1):" << " " << i << std::endl;
    }
    for (auto i: range(9, -1, -1)) {
        std::cout << "range(9, -1, -1):" << " " << i << std::endl;
    }
    for (auto i: range(100, 90, -3)) {
        std::cout << "range(100, 90, -3):" << " " << i << std::endl;
    }
    int a = 10;
    int b = 20;
    int c = 4;
    for (auto i: range(a, b, c)) {
        std::cout << "range(a, b, c):" << " " << i << std::endl;
    }
    a = 10;
    b = 0;
    c = -3;
    for (auto i: range(a, b, c)) {
        std::cout << "range(a, b, c):" << " " << i << std::endl;
    }
    for (auto i: range(one(), (one() + 2), one())) {
        std::cout << "range(one(), one() + 2, one()):" << " " << i << std::endl;
    }
    for (auto i: range(10)) {
        if (i == 0) {
            std::cout << "range(10):" << " " << 0 << std::endl;
        } else {
            if (i == 1) {
                continue;
            } else {
                if (i < 5) {
                    std::cout << "range(10):" << " " << i << std::endl;
                } else {
                    break;
                }
            }
        }
    }
    for (auto _: range(2)) {
        std::cout << "range(2):" << " " << "_" << std::endl;
    }
    while (false) {
    }
    while (true) {
        break;
    }

    return 0;
}
