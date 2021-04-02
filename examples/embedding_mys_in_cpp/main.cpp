#include "mys.hpp"
#include "embedding_mys_in_cpp/lib.mys.hpp"
#include "random/pseudo.mys.hpp"

using namespace mys::embedding_mys_in_cpp;

int main()
{
    // Initialize the Mys runtime. The current thread becomes the
    // main fiber.
    mys::init();

    std::cout << lib::multiply(2, 3) << std::endl;
    std::cout << lib::multiply(3, -4) << std::endl;

    std::cout << mys::random::pseudo::random() << std::endl;
    std::cout << mys::random::pseudo::random() << std::endl;

    return 0;
}
