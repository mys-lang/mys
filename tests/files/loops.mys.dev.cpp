#include "mys.hpp"

int one();

shared_vector<str> two();

int main();

int one()
{
    return 1;
}

shared_vector<str> two()
{
    return make_shared_vector<todo>({"c", "d"});
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
    for (auto make_shared_tuple<todo>({i, j}): enumerate(make_shared_vector<todo>({one(), 5, 3}))) {
        std::cout << "in enumerate([one(), 5, 3]):" << " " << i << " " << j << std::endl;
    }
    for (auto i: make_shared_tuple<todo>({1.0, 5.2, -3.7})) {
        std::cout << "(1.0, 5.2, -3.7):" << " " << i << std::endl;
    }
    make_shared_map<todo>({}) d = make_shared_map<todo>({});
    for (auto make_shared_tuple<todo>({i, j}): d.items()) {
        std::cout << "in d.items():" << " " << i << " " << j << std::endl;
    }
    for (auto i: two()) {
        std::cout << "two():" << " " << i << std::endl;
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
