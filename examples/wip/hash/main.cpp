#include <iostream>
#include <iomanip>
#include <functional>
#include <string>
#include <unordered_set>

class Foo {
public:
    std::string first_name;
    std::string last_name;
    int age;

    std::size_t __hash__() const noexcept
    {
        std::size_t hash = 0;

        hash += std::hash<std::string>{}(first_name);
        hash += std::hash<std::string>{}(last_name);
        hash += std::hash<int>{}(age);

        return hash;
    }

    bool __eq__(const Foo& other) const
    {
        return (first_name == other.first_name
                && last_name == other.last_name
                && age == other.age);
    }

    bool operator==(const Foo& other) const
    {
        return __eq__(other);
    }
};

template<>
struct std::hash<Foo>
{
    std::size_t operator()(Foo const& s) const noexcept
    {
        return s.__hash__();
    }
};

int main()
{
    Foo obj = { "Hubert", "Farnsworth", 10 };

    std::cout
        << "hash(" << std::quoted(obj.first_name) << ", "
        << std::quoted(obj.last_name) << ") = "
        << std::hash<Foo>{}(obj) << " (using std::hash<Foo>)\n";

    std::unordered_set<Foo> names = {
        obj,
        {"Bender", "Rodriguez", 5},
        {"Turanga", "Leela", 2}
    };

    for (auto& s : names) {
        std::cout
            << std::quoted(s.first_name)
            << ' '
            << std::quoted(s.last_name)
            << '\n';
    }

    return 0;
}
