#include <iostream>
#include <cassert>
#include <cstdint>
#include <tuple>
#include <utility>
#include <vector>
#include <string>
#include <iterator>
#include <algorithm>
#include <memory>

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

template <typename T>
std::ostream& operator<< (std::ostream& os, const std::vector<T>& vec) {
    os << '[';
    std::copy(vec.begin(), vec.end(), std::ostream_iterator<T>(os, ", "));
    os << "]";
  return os;
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

template <typename Tn> auto fibonacci(Tn n) {
    if (n == 0) {
        return 0;
    } else if (n == 1) {
        return 1;
    } else {
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
}

template <typename T> auto list_comprehension(T items) {
    T result;

    for (auto item: items) {
        if (item == "Dog") {
            result.push_back(item);
        }
    }

    return result;
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
    auto vi2 = 99;
    auto vi3 = 9999999999;
    auto vi4 = 1.2;
    std::string vi5("apa");
    // vi6 = ('hello', 5.6)  # Tuple of str and f32
    // vi7 = [(vi1, vi2), (2, 6)]
    // vi8 = [2 * v for v in [1, 2, 3]]  # List of s32
    // vi9 = {'1': 1, '2': 2}

    std::cout << "vi1: " << (unsigned int)vi1 << std::endl;
    std::cout << "vi2: " << vi2 << std::endl;
    std::cout << "vi3: " << vi3 << std::endl;
    std::cout << "vi4: " << vi4 << std::endl;
    std::cout << "vi5: " << vi5 << std::endl;

    std::cout << "f1(-1): " << f1(-1) << std::endl;

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

    std::cout << "fibonacci(0): " << fibonacci(0) << std::endl;
    std::cout << "fibonacci(5): " << fibonacci(5) << std::endl;

    std::vector<std::string> things({"Apple", "Banana", "Dog"});
    std::vector<std::string> animals;

    for (auto thing: things) {
        if (thing == "Dog") {
            animals.push_back(thing);
        }
    }

    std::cout << "animals: " << animals << std::endl;

    std::vector<std::string> things2({"Apple", "Banana", "Dog"});
    std::vector<std::string> result;
    std::copy_if(things2.begin(),
                 things2.end(),
                 std::back_inserter(result),
                 [](std::string item) {
                     return item == "Dog";
                 });
    std::cout << "animals2: " << result << std::endl;

    std::vector<int> list;
    std::vector<std::tuple<int, int>> items({
            std::tuple<int, int>(1, 2),
            std::tuple<int, int>(3, 4)
        });
    std::transform(items.begin(),
                   items.end(),
                   std::back_inserter(list),
                   [](std::tuple<int, int> item) {
                       return std::get<0>(item) + std::get<1>(item);
                   });
    std::cout << "list: " << list << std::endl;

    auto shared_p = std::make_shared<std::vector<int>>();
    shared_p->push_back(1);
    std::vector<std::shared_ptr<std::vector<int>>> sa({shared_p});
    std::vector<std::shared_ptr<std::vector<int>>> sb({shared_p});
    shared_p->push_back(5);
    assert(sa[0]->size() == 2);
    assert(sa[0]->at(0) == 1);
    assert(sa[0]->at(1) == 5);
    assert(sb[0]->size() == 2);
    assert(sa[0]->at(0) == 1);
    assert(sb[0]->at(1) == 5);

    return (0);
}
