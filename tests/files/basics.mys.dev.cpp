#include "mys.hpp"

Tuple<int, String> func_1(int a);

int func_2(int a, int b);

int func_3(std::optional<int>& a);

Dict<int, List<float>> func_4(int a);

void func_5();

int main(int __argc, const char *__argv[]);

Tuple<int, String> func_1(int a)
{
    return MakeTuple<todo>({(2 * a), "Bar"});
}

int func_2(int a, int b)
{
    for (auto i: range(b)) {
        a += (i * b);
    }
    return a;
}

int func_3(std::optional<int>& a)
{
    if (a == None) {
        return 0;
    } else {
        return (2 * a);
    }
}

Dict<int, List<float>> func_4(int a)
{
    return MakeDict<todo>({});
}

void func_5()
{
    try {
        throw Exception();
    } catch (std::exception& e) {
        std::cout << "func_5():      An exception occurred." << std::endl;
    }
}

class Calc {

public:

    Calc(int value)
    {
        this->value = value;
    }

    void triple()
    {
        this->value *= 3;
    }

};

int main(int __argc, const char *__argv[])
{
    auto args = create_args(__argc, __argv);
    value = int(args);
    std::cout << "func_1(value):" << " " << func_1(value) << std::endl;
    std::cout << "func_2(value):" << " " << func_2(value) << std::endl;
    std::cout << "func_3(None): " << " " << func_3(None) << std::endl;
    std::cout << "func_3(value):" << " " << func_3(value) << std::endl;
    std::cout << "func_4(value):" << " " << func_4(value) << std::endl;
    func_5();
    calc = Calc(value);
    calc.triple();
    std::cout << "calc:         " << " " << calc << std::endl;

    return 0;
}
