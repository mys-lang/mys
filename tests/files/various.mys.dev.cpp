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

    return 0;
}
