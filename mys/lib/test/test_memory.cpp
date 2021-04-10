#define CATCH_CONFIG_MAIN

#include "catch.hpp"
#include <iostream>
#include "mys/memory.hpp"

using mys::memory::shared_ptr;
using mys::memory::make_shared;

class Foo {
public:
    int x;

    Foo() {
        x = 5;
    }

    Foo(int y) {
        x = y;
    }

    ~Foo() {
    }
};

TEST_CASE("Various")
{
    shared_ptr<Foo> a = make_shared<Foo>();
    shared_ptr<Foo> b = make_shared<Foo>(2);
    shared_ptr<Foo> c;

    REQUIRE(a == a);
    REQUIRE(!(a == nullptr));
    REQUIRE(c == nullptr);
    REQUIRE(!(a == c));
    a = nullptr;
    c = b;
    REQUIRE(!(b == nullptr));
    b = nullptr;
    b = nullptr;
    REQUIRE(b == nullptr);
    REQUIRE(!(c == nullptr));
    REQUIRE(c->x == 2);
    b = c;
    REQUIRE(b->x == 2);
    b = b;
    REQUIRE(b->x == 2);
}

class Shape {
public:
    virtual ~Shape() {
    }

    virtual int area() = 0;
};

class Box : public Shape {
public:
    ~Box() {
    }

    int area() {
        return 5;
    }
};

static int area(shared_ptr<Shape> shape)
{
    return shape->area();
}

static int area_const_ref(const shared_ptr<Shape>& shape)
{
    return shape->area();
}

TEST_CASE("Inheritance")
{
    shared_ptr<Box> box = make_shared<Box>();

    REQUIRE(box.use_count() == 1);
    REQUIRE(box->area() == 5);
    REQUIRE(area(box) == 5);
    REQUIRE(area(static_cast<shared_ptr<Shape>>(box)) == 5);
    REQUIRE(area_const_ref(box) == 5);
    REQUIRE(area_const_ref(static_cast<shared_ptr<Shape>>(box)) == 5);
}
