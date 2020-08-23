#include "mys.hpp"

shared_tuple<int, shared_string> func_1(int a)
{
    return make_shared_tuple<int, shared_string>(2 * a, make_shared_string("Bar"));
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

shared_map<int, shared_vector<float>> func_4(int a)
{
    return make_shared_map<int, shared_vector<float>>({
            {1, make_shared_vector<float>({})},
            {10 * a, make_shared_vector<float>({7.5, -1.0})}
        });
}

void func_5()
{
    try {
        throw std::exception();
    } catch (...) {
        std::cout << "func_5():      An exception occurred." << std::endl;
    }
}

int main(int argc, const char *argv[])
{
    auto value = atoi(argv[1]);

    std::cout << "func_1(value):" << " " << *func_1(value) << std::endl;
    std::cout << "func_2(value):" << " " << func_2(value) << std::endl;
    std::cout << "func_3(None): " << " " << func_3({}) << std::endl;
    std::cout << "func_3(value):" << " " << func_3({value}) << std::endl;
    std::cout << "func_4(value):" << " " << *func_4(value) << std::endl;
    func_5();

    return (0);
}
