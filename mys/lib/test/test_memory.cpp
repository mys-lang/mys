#define CATCH_CONFIG_MAIN

#include "catch.hpp"
#include <iostream>
#include "mys/memory.hpp"

using mys::shared_ptr;
using mys::make_shared;

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

class FromThis;

class FromThisFoo {
public:
    shared_ptr<FromThis> from_this;

    FromThisFoo(shared_ptr<FromThis> from_this)
        : from_this(from_this) {
    }

    ~FromThisFoo() {
    }
};

class FromThis {
public:
    int a;
    shared_ptr<FromThisFoo> foo;

    FromThis() : a(3) {
        foo = make_shared<FromThisFoo>(shared_ptr<FromThis>(this));
    }

    ~FromThis() {
    }

    shared_ptr<FromThis> get() {
        return shared_ptr<FromThis>(this);
    }
};

TEST_CASE("Shared pointer from this")
{
    shared_ptr<FromThis> from_this = make_shared<FromThis>();

    REQUIRE(from_this->a == 3);
    REQUIRE(from_this->get()->a == 3);
    REQUIRE(from_this->foo->from_this->a == 3);
    REQUIRE(from_this->foo->from_this->get()->a == 3);
}

class NullPtr {
public:
    int a;

    NullPtr() : a(3) {
    }

    ~NullPtr() {
    }
};

static bool is_null(shared_ptr<NullPtr> null)
{
    if (null) {
        return false;
    } else {
        return true;
    }
}

TEST_CASE("Null pointer")
{
    REQUIRE(is_null(nullptr));
    REQUIRE(!is_null(make_shared<NullPtr>()));
}
