#include "catch.hpp"
#include "mys/optional.hpp"

using mys::optional;

TEST_CASE("Various optional")
{
    optional<int> v;
    REQUIRE(v == nullptr);
    v = 1;
    REQUIRE(v != nullptr);
    REQUIRE(v == 1);
    v = nullptr;
    REQUIRE(v == nullptr);
    optional<int> v2{5};
    v = 5;
    REQUIRE(v == v2);
}
