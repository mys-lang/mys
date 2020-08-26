#include "mys.hpp"

int main()
{
    {
        auto fout = open("foo.txt", "w");
        fout.write("1");
    }
    {
        auto fin = open("foo.txt", "r");
        assert(fin.read() == "1");
    }
    {
        auto fout = open("foo.bin", "wb");
        fout.write(b'\x01');
    }
    {
        auto fin = open("foo.bin", "rb");
        assert(fin.read() == b'\x01');
    }
    if (true) {
        std::cout << 1 << std::endl;
    }
    if (false) {
        std::cout << 2 << std::endl;
    } else {
        std::cout << 3 << std::endl;
    }
    if (true) {
        std::cout << 4 << std::endl;
    } else {
        if (false) {
            std::cout << 5 << std::endl;
        } else {
            if (true) {
                std::cout << 6 << std::endl;
            } else {
                std::cout << 7 << std::endl;
            }
        }
    }
    try {
        try {
            throw TypeError();
        } catch (ValueError& e) {
            std::cout << "ValueError" << std::endl;
        } catch (TypeError& e) {
            std::cout << "TypeError" << std::endl;
        }
        std::cout << "finally" << std::endl;
    } catch (...) {
        std::cout << "finally" << std::endl;
        throw;
    }
    try {
        throw ValueError();
    } catch (ValueError& e) {
        std::cout << "ValueError" << std::endl;
        throw;
    }

    return 0;
}
