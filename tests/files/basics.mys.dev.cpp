#include "mys.hpp"

shared_tuple<int, shared_string> func_1(int a)
{
}

int func_2(int a, int b)
{
    for (auto i: range(b)) {
        a += (i * b);
    }
}

int func_3(std::optional<int>& a)
{
}

shared_map<int, shared_vector<float>> func_4(int a)
{
}

void func_5()
{
}

class Calc {

public:

    Calc(int value)
    {
    }

    void triple()
    {
    }

};

int main()
{
    std::cout << "func_1(value):" << " " << func_1(value) << std::endl;
    std::cout << "func_2(value):" << " " << func_2(value) << std::endl;
    std::cout << "func_3(None): " << " " << func_3({}) << std::endl;
    std::cout << "func_3(value):" << " " << func_3(value) << std::endl;
    std::cout << "func_4(value):" << " " << func_4(value) << std::endl;
    func_5();
    ;
    std::cout << "calc:         " << " " << calc << std::endl;

    return (0);
}