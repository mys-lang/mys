#include <iostream>
#include <cassert>
#include <cstdint>
#include <tuple>
#include <utility>
#include <vector>
#include <string>

// Tuple printer.
template<class T, size_t... I>
std::ostream& print_tuple(std::ostream& os,
                          const T& tup,
                          std::index_sequence<I...>)
{
    os << "(";
    (..., (os << (I == 0 ? "" : ", ") << std::get<I>(tup)));
    os << ")";
    return os;
}

template<class... T>
std::ostream& operator<<(std::ostream& os, const std::tuple<T...>& tup)
{
    return print_tuple(os, tup, std::make_index_sequence<sizeof...(T)>());
}

typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef int8_t s8;
typedef int16_t s16;
typedef int32_t s32;
typedef int64_t s64;
typedef float f32;
typedef double f64;

class NotImplementedError : public std::logic_error {

public:
    NotImplementedError() : std::logic_error("Function not yet implemented") {
    };
};

// Inheritance.
class A {

public:
    u64 value;

    A() {
        this->value = 0;
    }

    virtual void add(u64 value) {
        (void)value;

        throw NotImplementedError();
    }
};

class B: public A {

public:
    void add(u64 value) {
        this->value += value;
    }
};

class C: public A {

public:
    void add(u64 value) {
        this->value += (2 * value);
    }
};

// Functions must always be typed.
template <typename Ta> auto f1(Ta a) {
    return std::make_tuple(2 * a, 6);
}

int main()
{
    // Explicit types.
    u8 ve1 = 1;
    s8 ve2 = -4;
    f64 ve3 = 1.2;
    std::string ve4("apa");
    // ve5: Tuple[str, f64] = ('hello', 5.6)
    // ve6: List[Tuple[u8, s8]] = [(ve1, ve2), (2, 6)]
    // ve7: List[u8] = [v + k for v, k in ve6]
    // ve8: Optional[u8] = None
    s32 ve8 = 5;
    // ve9: Optional[List[str]] = None
    // ve9 = ['foo']

    std::cout << "ve1: " << (unsigned int)ve1 << std::endl;
    std::cout << "ve2: " << (int)ve2 << std::endl;
    std::cout << "ve3: " << ve3 << std::endl;
    std::cout << "ve4: " << ve4 << std::endl;
    std::cout << "ve8: " << ve8 << std::endl;

    // Inferred types.
    auto vi1 = ve1;
    s32 vi2 = 99;
    s64 vi3 = 9999999999;
    f32 vi4 = 1.2;
    std::string vi5("apa");
    // vi6 = ('hello', 5.6)  # Tuple of str and f32
    // vi7 = [(vi1, vi2), (2, 6)]
    // vi8 = [2 * v for v in [1, 2, 3]]  # List of s32
    // vi9 = {'1': 1, '2': 2}
    auto vi10 = 5;
    auto vi11 = 5.5;

    std::cout << "vi1: " << (unsigned int)vi1 << std::endl;
    std::cout << "vi2: " << vi2 << std::endl;
    std::cout << "vi3: " << vi3 << std::endl;
    std::cout << "vi4: " << vi4 << std::endl;
    std::cout << "vi5: " << vi5 << std::endl;
    std::cout << "vi10: " << vi10 << std::endl;
    std::cout << "vi11: " << vi11 << std::endl;

    std::cout << "f1: " << f1(-1) << std::endl;

    // i becomes s32 by default
    for (s32 i = 0; i < 5; i++) {
        std::cout << i << std::endl;
    }

    // # Read strings. fin becomes TextIO.
    // with open('tests/files/main.py') as fin:
    //     for line in fin:
    //         if 'main.py' in line:
    //             print(line)
    //
    // # Read bytes. fin becomes BinaryIO.
    // with open('tests/files/main.py', 'rb') as fin:
    //     print(fin.read(10))

    // Wrap around is silently ignored by default. Possibly add an option to
    // raise an overflow exception.
    u8 a = 255;
    a += 1;

    // Inheritance.
    B b;
    C c;
    b.add(2);
    c.add(1);
    assert(b.value == c.value);

    return (0);
}
