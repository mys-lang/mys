#include <iostream>
#include <cassert>
#include <cstdint>
#include <tuple>
#include <utility>
#include <vector>
#include <string>
#include <iterator>
#include <algorithm>
#include <memory>
#include <optional>
#include <map>

std::tuple<int, std::string> func_1(int a)
{
    return std::make_tuple<int, std::string>(2 * a, "Bar");
}

int func_2(int a, int b = 1)
{
    return a * b;
}

int func_3(std::optional<int> a)
{
    if (!a) {
        return 0;
    } else {
        return 2 * a.value();
    }
}

std::map<int, std::vector<float>> func_4(int a)
{
    return {{10 * a, {7.5, -1.0}}};
}

void func_5()
{
    try {
        throw std::exception();
    } catch (...) {
        std::cout << "func_5(): An exception occurred." << std::endl;
    }
}

int main(int argc, const char *argv[])
{
    auto value = atoi(argv[1]);

    std::cout << "func_1(value):" << " " << std::get<0>(func_1(value)) << std::endl;
    std::cout << "func_2(value):" << " " << func_2(value) << std::endl;
    std::cout << "func_3(None): " << " " << func_3({}) << std::endl;
    std::cout << "func_3(value):" << " " << func_3({value}) << std::endl;
    std::cout << "func_4(value):" << " " << func_4(value)[10 * value][0] << std::endl;
    func_5();

    return (0);
}
