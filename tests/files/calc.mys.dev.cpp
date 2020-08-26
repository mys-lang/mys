#include "mys.hpp"

int main()
{
    int x = 10;
    int y = -2;
    int res = ((5 + (2 * x)) - (8 / y));
    std::cout << "(5 + 2 * x) - 8 / y =" << " " << res << std::endl;
    assert(res == 29);
    res = (((5 + (2 * x)) - 8) / y);
    std::cout << "((5 + 2 * x) - 8) / y =" << " " << res << std::endl;
    assert(res == -8);
    res = (1 << 2);
    std::cout << "1 << 2 =" << " " << res << std::endl;
    assert(res == 4);
    res = (4 >> 2);
    std::cout << "4 >> 2 =" << " " << res << std::endl;
    assert(res == 1);
    res = (1 | 8);
    std::cout << "1 | 8 =" << " " << res << std::endl;
    assert(res == 9);
    res = (1 ^ 3);
    std::cout << "1 ^ 3 =" << " " << res << std::endl;
    assert(res == 2);
    res = (1 & 3);
    std::cout << "1 & 3 =" << " " << res << std::endl;
    assert(res == 1);
    res = (10 % 4);
    std::cout << "10 % 4 =" << " " << res << std::endl;
    assert(res == 2);
    u32 x_u32 = 1000000000;
    u32 y_u32 = 5;
    u32 res_u32 = (x_u32 - (2 * y_u32));
    std::cout << "x_u32 - 2 * y_u32 =" << " " << res_u32 << std::endl;
    assert(res_u32 == 999999990);
    res_u32 = (2 * x_u32);
    std::cout << "2 * x_u32 =" << " " << res_u32 << std::endl;
    assert(res_u32 == 2000000000);
    res_u32 = (3 * x_u32);
    std::cout << "3 * x_u32 =" << " " << res_u32 << std::endl;
    assert(res_u32 == 3000000000);
    res_u32 = (4 * x_u32);
    std::cout << "4 * x_u32 =" << " " << res_u32 << std::endl;
    assert(res_u32 == 4000000000);
    res_u32 = (5 * x_u32);
    std::cout << "5 * x_u32 =" << " " << res_u32 << std::endl;
    assert(res_u32 == 705032704);
    s16 x_s16 = 32767;
    s16 res_s16 = x_s16;
    std::cout << "x_s16 =" << " " << res_s16 << std::endl;
    assert(res_s16 == 32767);
    res_s16 = (x_s16 + 1);
    std::cout << "x_s16 + 1 =" << " " << res_s16 << std::endl;
    assert(res_s16 == -32768);

    return 0;
}
