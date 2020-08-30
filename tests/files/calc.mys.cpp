#include "mys.hpp"

int main();

int main()
{
    int x = 10;
    int y = -2;
    int res = ((5 + (2 * x)) - (8 / y));
    std::cout << "(5 + 2 * x) - 8 / y =" << " " << res << std::endl;
    ASSERT(res == 29);
    res = (((5 + (2 * x)) - 8) / y);
    std::cout << "((5 + 2 * x) - 8) / y =" << " " << res << std::endl;
    ASSERT(res == -8);
    res = ipow(3, 2);
    std::cout << "3 ** 2 =" << " " << res << std::endl;
    ASSERT(res == 9);
    res = (1 << 2);
    std::cout << "1 << 2 =" << " " << res << std::endl;
    ASSERT(res == 4);
    res = (4 >> 2);
    std::cout << "4 >> 2 =" << " " << res << std::endl;
    ASSERT(res == 1);
    res = (1 | 8);
    std::cout << "1 | 8 =" << " " << res << std::endl;
    ASSERT(res == 9);
    res = (1 ^ 3);
    std::cout << "1 ^ 3 =" << " " << res << std::endl;
    ASSERT(res == 2);
    res = (1 & 3);
    std::cout << "1 & 3 =" << " " << res << std::endl;
    ASSERT(res == 1);
    res = (10 % 4);
    std::cout << "10 % 4 =" << " " << res << std::endl;
    ASSERT(res == 2);

    return 0;
}
