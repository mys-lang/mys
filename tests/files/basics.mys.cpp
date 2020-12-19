// This file was generated by mys. DO NOT EDIT!!!
#include "basics.mys.hpp"
/* mys-embedded-c++-before-namespace start */
#include <before>
/* mys-embedded-c++-before-namespace stop */
namespace mys::basics
{
std::shared_ptr<Tuple<i32, String>> func_1(i32 a);
std::shared_ptr<Dict<i64, std::shared_ptr<List<f64>>>> func_3(i32 a);
void func_4(void);
std::shared_ptr<List<i64>> func_5(void);
void main(int __argc, const char *__argv[]);
;
/* mys-embedded-c++ start */

#include <not-before>

/* mys-embedded-c++ stop */;
std::shared_ptr<Tuple<i32, String>> func_1(i32 a)
{
    return std::make_shared<Tuple<i32, String>>((2 * a), "Bar");
}
std::shared_ptr<Dict<i64, std::shared_ptr<List<f64>>>> func_3(i32 a)
{
    return std::make_shared<Dict<i64, std::shared_ptr<List<f64>>>>(std::initializer_list<robin_hood::pair<i64, std::shared_ptr<List<f64>>>>{{1, std::make_shared<List<None>>(std::initializer_list<None>{})}, {(10 * i64(a)), std::make_shared<List<f64>>(std::initializer_list<f64>{7.5, -(1.0)})}});
}
void func_4(void)
{
    try {
        throw GeneralError();
    } catch (std::exception& e) {
        std::cout << "func_4():      An exception occurred." << std::endl;
    }
}
std::shared_ptr<List<i64>> func_5(void)
{
    std::shared_ptr<List<i64>> small = std::make_shared<List<i64>>(std::initializer_list<i64>{});
    auto items_2 = std::make_shared<List<i64>>(std::initializer_list<i64>{3, 1, 5, 7, 2});
    for (auto i_3 = 0; i_3 < items_2->__len__(); i_3++) {
        auto v = items_2->get(i_3);
        if (Bool(v < 5)) {
            shared_ptr_not_none(small)->append(v);
        }
    }
    shared_ptr_not_none(small)->sort();
    shared_ptr_not_none(small)->reverse();
    return small;
}
void Calc::triple(void)
{
    this->value *= 3;
}
Calc::Calc(i32 value)
{
    this->value = value;
}
Calc::~Calc(){
}
String Calc::__str__() const
{
    std::stringstream ss;
    __format__(ss);
    return String(ss.str().c_str());
}
void Calc::__format__(std::ostream& os) const
{
    os << "Calc(";
    os << "value=" << value;
    os << ")";
}
void main(int __argc, const char *__argv[])
{
    auto argv = create_args(__argc, __argv);
    i32 value = i32(shared_ptr_not_none(argv)->get(1));
    std::cout << "func_1(value):" << " " << func_1(value) << std::endl;
    std::cout << "func_3(value):" << " " << func_3(value) << std::endl;
    func_4();
    std::cout << "func_5():     " << " " << func_5() << std::endl;
    std::shared_ptr<Calc> calc = std::make_shared<Calc>(value);
    shared_ptr_not_none(calc)->triple();
    std::cout << "calc:         " << " " << calc << std::endl;
}
}

void package_main(int argc, const char *argv[])
{
    mys::basics::main(argc, argv);
}