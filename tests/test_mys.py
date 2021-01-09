from mys.transpiler import TranspilerError
from .utils import transpile_header
from .utils import transpile_source
from .utils import remove_ansi
from .utils import TestCase


class Test(TestCase):

    def test_invalid_main_argument(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def main(argv: i32): pass',
                             has_main=True)

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    def main(argv: i32): pass\n'
            '    ^\n'
            "CompileError: main() takes 'argv: [string]' or no arguments\n")

    def test_main_no_argv(self):
        transpile_source('def main():\n'
                         '    pass\n',
                         has_main=True)

    def test_main_argv(self):
        transpile_source('def main(argv: [string]):\n'
                         '    pass\n',
                         has_main=True)

    def test_invalid_main_return_type(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def main() -> i32: pass',
                             has_main=True)

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "", line 1\n'
                         '    def main() -> i32: pass\n'
                         '    ^\n'
                         "CompileError: main() must not return any value\n")

    def test_return_nothing_in_main(self):
        source = transpile_source('def main():\n'
                                  '    return\n',
                                  has_main=True)

        # main() must return void.
        self.assert_in('void main(int __argc, const char *__argv[])\n'
                       '{\n'
                       '    (void)__argc;\n'
                       '    (void)__argv;\n'
                       '    return;\n'
                       '}\n',
                       source)

    def test_lambda_not_supported(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def main(): print((lambda x: x)(1))',
                             mys_path='foo.py',
                             has_main=True)

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "foo.py", line 1\n'
                         '    def main(): print((lambda x: x)(1))\n'
                         '                       ^\n'
                         'CompileError: lambda functions are not supported\n')

    def test_bad_syntax(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('DEF main(): pass',
                             mys_path='<unknown>',
                             has_main=True)

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "<unknown>", line 1\n'
                         '    DEF main(): pass\n'
                         '        ^\n'
                         'SyntaxError: invalid syntax\n')

    def test_empty_function(self):
        source = transpile_source('def foo():\n'
                                  '    pass\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '\n'
                       '}\n',
                       source)

    def test_undefined_function(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    bar()\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        bar()\n'
            '        ^\n'
            "CompileError: undefined function 'bar'\n")

    def test_test_can_not_take_any_values(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('@test(H)\n'
                             'def foo():\n'
                             '    pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    @test(H)\n'
            '     ^\n'
            "CompileError: no parameters expected\n")

    def test_non_snake_case_function(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def Apa():\n'
                             '    pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    def Apa():\n'
            '    ^\n'
            "CompileError: function names must be snake case\n")

    def test_non_snake_case_function_parameter_name(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(A: i32):\n'
                             '    pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    def foo(A: i32):\n'
            '            ^\n'
            "CompileError: parameter names must be snake case\n")

    def test_missing_function_parameter_type(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(x):\n'
                             '    pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    def foo(x):\n'
            '            ^\n'
            "CompileError: parameters must have a type\n")

    def test_invalid_decorator_value(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('@raises(A(B))\n'
                             'def foo():\n'
                             '    pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    @raises(A(B))\n'
            '            ^\n'
            "CompileError: invalid decorator value\n")

    def test_invalid_decorator_value_syntax(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('@raises[A]\n'
                             'def foo():\n'
                             '    pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    @raises[A]\n'
            '     ^\n'
            "CompileError: decorators must be @name or @name()\n")

    def test_inferred_type_combined_integers_assignment_too_big(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    value = (0xffffffffffffffff + 1)\n'
                             '    print(value)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        value = (0xffffffffffffffff + 1)\n'
            '                 ^\n'
            "CompileError: integer literal out of range for 'i64'\n")

    def test_test_functions_not_in_header(self):
        header = transpile_header('@test\n'
                                  'def test_foo():\n'
                                  '    pass\n',
                                  module_hpp='foo/lib.mys.hpp')

        self.assertNotIn('test_foo', header)

    def test_return_i64_from_function_returning_string(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> string:\n'
                             '    return True')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return True\n'
            '               ^\n'
            "CompileError: expected a 'string', got a 'bool'\n")

    def test_return_list_from_function_returning_tuple(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> (bool, i64):\n'
                             '    return [1]')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return [1]\n'
            '               ^\n'
            "CompileError: cannot convert list to '(bool, i64)'\n")

    def test_return_tuple_from_function_returning_list(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> [bool]:\n'
                             '    return (1, True)')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return (1, True)\n'
            '               ^\n'
            "CompileError: cannot convert tuple to '[bool]'\n")

    def test_wrong_number_of_function_parameters(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    pass\n'
                             'def bar():\n'
                             '    foo(1)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        foo(1)\n'
            '        ^\n'
            "CompileError: expected 0 parameters, got 1\n")

    def test_wrong_function_parameter_type(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: string):\n'
                             '    pass\n'
                             'def bar():\n'
                             '    foo(True)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        foo(True)\n'
            '            ^\n'
            "CompileError: expected a 'string', got a 'bool'\n")

    def test_compare_i64_and_bool(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return 1 == True')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return 1 == True\n'
            '               ^\n'
            "CompileError: cannot convert 'i64/i32/i16/i8/u64/u32/u16/u8' "
            "to 'bool'\n")

    def test_compare_mix_of_literals_and_known_types_1(self):
        source = transpile_source('def foo():\n'
                                  '    k: u64 = 1\n'
                                  '    v: i64 = 1\n'
                                  '    if 0xffffffffffffffff == k:\n'
                                  '        pass\n'
                                  '    print(v)\n')

        self.assert_in('18446744073709551615ull', source)

    def test_assign_256_to_u8(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('A: u8 = 256\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    A: u8 = 256\n'
            '            ^\n'
            "CompileError: integer literal out of range for 'u8'\n")

    def test_assign_over_max_to_u64(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('A: u64 = 0x1ffffffffffffffff\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    A: u64 = 0x1ffffffffffffffff\n'
            '             ^\n'
            "CompileError: integer literal out of range for 'u64'\n")

    def test_assign_max_to_i64(self):
        source = transpile_source('A: i64 = 0x7fffffffffffffff\n')

        self.assert_in('i64 A = 9223372036854775807;', source)

    def test_assign_over_max_to_i64(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('A: i64 = 0xffffffffffffffff\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    A: i64 = 0xffffffffffffffff\n'
            '             ^\n'
            "CompileError: integer literal out of range for 'i64'\n")

    def test_assign_float_to_u8(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('A: u8 = 2.0\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    A: u8 = 2.0\n'
            '            ^\n'
            "CompileError: cannot convert float to 'u8'\n")

    def test_arithmetics_on_mix_of_literals_and_known_types_5(self):
        source = transpile_source('def foo():\n'
                                  '    k: i32 = -1\n'
                                  '    v: u8 = 1\n'
                                  '    value = ((-1 / 2) - 2 * k)\n'
                                  '    print(value, v)\n')

        self.assert_in('value = ((-1 / 2) - (2 * k));', source)

    def test_assign_negative_number_to_u32(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    k: u32 = -1\n'
                             '    print(k)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        k: u32 = -1\n'
            '                 ^\n'
            "CompileError: integer literal out of range for 'u32'\n")

    def test_assign_positive_number_to_u32(self):
        # Not sure if --1 should be allowed.
        source = transpile_source('def foo():\n'
                                  '    i: u32 = +1\n'
                                  '    j: u32 = --1\n'
                                  '    print(i, j)\n')

        self.assert_in('u32 i = 1;', source)
        self.assert_in('u32 j = 1;', source)

    def test_reassign_negative_number_to_u32(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    i: u32 = 0\n'
                             '    i = -1\n'
                             '    print(i)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        i = -1\n'
            '            ^\n'
            "CompileError: integer literal out of range for 'u32'\n")

    def test_arithmetics_on_mix_of_literals_and_known_types_too_big(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    k: i64 = 1\n'
                             '    value = (0xffffffffffffffff + k)\n'
                             '    print(value)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        value = (0xffffffffffffffff + k)\n'
            '                 ^\n'
            "CompileError: integer literal out of range for 'i64'\n")

    def test_arithmetics_on_mix_of_literals_and_known_types_negative(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    value: u8 = (-1 * 5)\n'
                             '    print(value)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        value: u8 = (-1 * 5)\n'
            '                     ^\n'
            "CompileError: integer literal out of range for 'u8'\n")

    def test_arithmetics_and_compare(self):
        source = transpile_source('def foo():\n'
                                  '    k: i32 = -1\n'
                                  '    if ((-1 / 2) - 2 * k) == k:\n'
                                  '        pass\n')

        self.assert_in('if (Bool(((-1 / 2) - (2 * k)) == k)) {', source)

    def test_change_integer_type(self):
        source = transpile_source('def foo():\n'
                                  '    value = (i8(-1) * i8(u32(5)))\n'
                                  '    print(value)\n')

        self.assert_in('value = (i8(-1) * i8(u32(5)));', source)

    # ToDo
    # def test_change_integer_type_error(self):
    #     with self.assertRaises(TranspilerError) as cm:
    #         transpile_source('def foo():\n'
    #                          '    value = (i8(-1) * u32(5))\n'
    #                          '    print(value)\n')
    #
    #     self.assert_exception_string(
    #         cm,
    #         '  File "", line 2\n'
    #         '        value = (i8(-1) * u32(5))\n'
    #         '                 ^\n'
    #         "CompileError: cannot compare 'i8' and 'u32'\n")

    def test_function_call(self):
        source = transpile_source('def foo(a: i32, b: f32):\n'
                                  '    print(a, b)\n'
                                  'def bar():\n'
                                  '    foo(1, 2.1)\n')

        self.assert_in('foo(1, 2.1);', source)

    def test_tuple_unpack_variable_defined_other_type(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('class Foo:\n'
                             '    def foo(self) -> (bool, i64):\n'
                             '        return (True, -5)\n'
                             'def foo():\n'
                             '    v = Foo()\n'
                             '    b: string = ""\n'
                             '    a, b = v.foo()\n')

        self.assert_exception_string(
            cm,
            '  File "", line 7\n'
            '        a, b = v.foo()\n'
            '           ^\n'
            "CompileError: expected a 'string', got a 'i64'\n")

    def test_tuple_unpack_integer(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a, b = 1\n'
                             '    print(a, b)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        a, b = 1\n'
            '               ^\n'
            "CompileError: only tuples can be unpacked\n")

    def test_assert_between(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a = 2\n'
                             '    assert 1 <= a < 3\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            "        assert 1 <= a < 3\n"
            '               ^\n'
            "CompileError: can only compare two values\n")

    def test_compare_between(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a = 2\n'
                             '    print(1 <= a < 3)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            "        print(1 <= a < 3)\n"
            '              ^\n'
            "CompileError: can only compare two values\n")

    def test_type_error_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a: u16 = 1\n'
                             '    b: u32 = 1\n'
                             '    c = b - a\n'
                             '    print(c)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        c = b - a\n'
            '            ^\n'
            "CompileError: types 'u32' and 'u16' differs\n")

    def test_type_error_2(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: i64):\n'
                             '    b: u64 = a\n'
                             '    print(b)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        b: u64 = a\n'
            '                 ^\n'
            "CompileError: expected a 'u64', got a 'i64'\n")

    def test_type_error_3(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def bar() -> string:\n'
                             '    return ""\n'
                             'def foo():\n'
                             '    b: u64 = bar()\n'
                             '    print(b)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        b: u64 = bar()\n'
            '                 ^\n'
            "CompileError: expected a 'u64', got a 'string'\n")

    # ToDo
    # def test_type_error_4(self):
    #     with self.assertRaises(TranspilerError) as cm:
    #         transpile_source('def foo():\n'
    #                          '    a: u32 = 1\n'
    #                          '    b = a - [1]\n'
    #                          '    print(b)\n')
    #
    #     self.assertEqual(
    #         remove_ansi(str(cm.exception)),
    #         '  File "", line 3\n'
    #         '        b = a - [1]\n'
    #         '            ^\n'
    #         "CompileError: types 'u32' and '[i64]' differs\n")

    def test_type_error_5(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return\n'
            '        ^\n'
            "CompileError: return value missing\n")

    def test_type_error_6(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    return 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return 1\n'
            '               ^\n'
            "CompileError: function does not return any value\n")

    def test_compare_wrong_types_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return 1 == [""]\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return 1 == [""]\n'
            '               ^\n'
            "CompileError: cannot convert 'i64/i32/i16/i8/u64/u32/u16/u8' to "
            "'[string]'\n")

    def test_compare_wrong_types_2(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return [""] in 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return [""] in 1\n'
            '                       ^\n'
            "CompileError: not an iterable\n")

    def test_compare_wrong_types_3(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return [""] not in 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return [""] not in 1\n'
            '                           ^\n'
            "CompileError: not an iterable\n")

    def test_compare_wrong_types_4(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return 2.0 == 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return 2.0 == 1\n'
            '               ^\n'
            "CompileError: cannot convert 'f64/f32' to "
            "'i64/i32/i16/i8/u64/u32/u16/u8'\n")

    def test_compare_wrong_types_5(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return 1.0 == [""]\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return 1.0 == [""]\n'
            '               ^\n'
            "CompileError: cannot convert 'f64/f32' to '[string]'\n")

    def test_compare_wrong_types_6(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: i32) -> bool:\n'
                             '    return a in [""]\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return a in [""]\n'
            '               ^\n'
            "CompileError: types 'i32' and 'string' differs\n")

    def test_compare_wrong_types_7(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: i32) -> bool:\n'
                             '    return a in a\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return a in a\n'
            '                    ^\n'
            "CompileError: not an iterable\n")

    def test_compare_wrong_types_8(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: i32) -> bool:\n'
                             '    return 1 in a\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return 1 in a\n'
            '                    ^\n'
            "CompileError: not an iterable\n")

    def test_compare_wrong_types_9(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: i32) -> bool:\n'
                             '    return "" == a\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return "" == a\n'
            '               ^\n'
            "CompileError: types 'string' and 'i32' differs\n")

    def test_compare_wrong_types_10(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(1 is None)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(1 is None)\n'
            '                   ^\n'
            "CompileError: 'i64' cannot be None\n")

    def test_compare_wrong_types_11(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(1.0 is None)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(1.0 is None)\n'
            '                     ^\n'
            "CompileError: 'f64' cannot be None\n")

    def test_compare_wrong_types_12(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: i32):\n'
                             '    print(a is None)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(a is None)\n'
            '              ^\n'
            "CompileError: 'i32' cannot be None\n")

    def test_compare_wrong_types_13(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: i32):\n'
                             '    print(None is a)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(None is a)\n'
            '              ^\n'
            "CompileError: 'i32' cannot be None\n")

    def test_compare_wrong_types_14(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(True is None)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(True is None)\n'
            '              ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_compare_wrong_types_15(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: bool):\n'
                             '    print(None is a)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(None is a)\n'
            '              ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_compare_wrong_types_16(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: bool):\n'
                             '    print(a is not 1)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(a is not 1)\n'
            '              ^\n'
            "CompileError: cannot convert 'bool' to "
            "'i64/i32/i16/i8/u64/u32/u16/u8'\n")

    def test_compare_wrong_types_17(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(None in [1, 5])\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(None in [1, 5])\n'
            '              ^\n'
            "CompileError: 'i64' cannot be None\n")

    def test_compare_wrong_types_18(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(None == "")\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(None == "")\n'
            '              ^\n'
            "CompileError: use 'is' and 'is not' to compare to None\n")

    def test_compare_wrong_types_20(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    if (1, ("", True)) == (1, ("", 1)):\n'
                             '        pass\n')

        # ToDo: Marker in wrong place.
        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        if (1, ("", True)) == (1, ("", 1)):\n'
            '           ^\n'
            "CompileError: cannot convert 'bool' to "
            "'i64/i32/i16/i8/u64/u32/u16/u8'\n")

    def test_bool_op_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    if True or None:\n'
                             '        pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            "        if True or None:\n"
            '                   ^\n'
            "CompileError: None is not a 'bool'\n")

    def test_bool_op_2(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    if True or False and 1:\n'
                             '        pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            "        if True or False and 1:\n"
            '                             ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

    def test_inferred_type_none(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a = None\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            "        a = None\n"
            '        ^\n'
            "CompileError: cannot infer type from None\n")

    def test_docstring(self):
        source = transpile_source('def foo():\n'
                                  '    "Hi!"\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '}\n',
                       source)

    def test_docstring_embedded_cpp(self):
        source = transpile_source('def foo():\n'
                                  '    "mys-embedded-c++ print();"\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    /* mys-embedded-c++ start */\n'
                       '    print();\n'
                       '    /* mys-embedded-c++ stop */;\n'
                       '}\n',
                       source)

    def test_global_integer_out_of_range(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('V: i8 = 1000\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            "    V: i8 = 1000\n"
            '            ^\n'
            "CompileError: integer literal out of range for 'i8'\n")

    def test_global_wrong_value_type(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('V: i8 = ""\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    V: i8 = ""\n'
            '            ^\n'
            "CompileError: expected a 'i8', got a 'string'\n")

    def test_assign_to_wrong_type(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a = 1\n'
                             '    a = ""\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        a = ""\n'
            '            ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_format_string_i8_u8(self):
        source = transpile_source('def foo():\n'
                                  '    print(f"{i8(1)} {u8(1)} {u16(1)}")\n')

        self.assert_in('String((int)i8(1))', source)
        self.assert_in('String((unsigned)u8(1))', source)
        self.assert_in('String(u16(1))', source)

    def test_min_wrong_types(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(min(u8(1), u8(2), i8(2)))\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(min(u8(1), u8(2), i8(2)))\n'
            '                                ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_min_no_args(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(min())\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(min())\n'
            '              ^\n'
            "CompileError: expected at least one parameter\n")

    def test_min_wrong_return_type(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    assert min(1, 2) == i8(1)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        assert min(1, 2) == i8(1)\n'
            '               ^\n'
            "CompileError: types 'i64' and 'i8' differs\n")

    def test_max_wrong_types(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(max(i8(1), i8(2), u8(2)))\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(max(i8(1), i8(2), u8(2)))\n'
            '                                ^\n'
            "CompileError: expected a 'i8', got a 'u8'\n")

    def test_max_no_args(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(max())\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(max())\n'
            '              ^\n'
            "CompileError: expected at least one parameter\n")

    def test_max_wrong_return_type(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    assert max(u8(1), 2) == i8(1)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        assert max(u8(1), 2) == i8(1)\n'
            '               ^\n'
            "CompileError: types 'u8' and 'i8' differs\n")

    def test_len_no_params(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(len())\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(len())\n'
            '              ^\n'
            "CompileError: expected 1 parameter, got 0\n")

    def test_len_two_params(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(len(1, 2))\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(len(1, 2))\n'
            '              ^\n'
            "CompileError: expected 1 parameter, got 2\n")

    def test_len_compare_to_non_u64(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    assert len("") == i8(0)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        assert len("") == i8(0)\n'
            '               ^\n'
            "CompileError: types 'u64' and 'i8' differs\n")

    def test_str_compare_to_non_string(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    assert str(0) == i8(0)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        assert str(0) == i8(0)\n'
            '               ^\n'
            "CompileError: types 'string' and 'i8' differs\n")

    def test_tuple_index_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a = 1\n'
                             '    v = (1, "b")\n'
                             '    print(v[a])\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        print(v[a])\n'
            '                ^\n'
            "CompileError: tuple indexes must be compile time known integers\n")

    def test_tuple_index_2(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    v = (1, "b")\n'
                             '    print(v[1 / 2])\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        print(v[1 / 2])\n'
            '                ^\n'
            "CompileError: tuple indexes must be compile time known integers\n")

    def test_tuple_item_assign_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    v = (1, "b")\n'
                             '    v[0] = "ff"\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        v[0] = "ff"\n'
            '               ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_tuple_item_assign_2(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a, b, c = (1, "b")\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        a, b, c = (1, "b")\n'
            '        ^\n'
            "CompileError: expected 3 values to unpack, got 2\n")

    def test_return_nones_as_bool_in_tuple(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> (bool, bool):\n'
                             '    return (None, None)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return (None, None)\n'
            '                ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_return_wrong_integer_in_tuple(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> (bool, u8, string):\n'
                             '    return (True, i8(1), "")\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return (True, i8(1), "")\n'
            '                      ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_return_none_as_bool(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return None\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return None\n'
            '               ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_assign_none_to_i32(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('A: i32 = None\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    A: i32 = None\n'
            '             ^\n'
            "CompileError: 'i32' cannot be None\n")

    def test_return_short_tuple(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> (bool, bool):\n'
                             '    return (True, )\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return (True, )\n'
            '               ^\n'
            "CompileError: expected a '(bool, bool)', got a '(bool, )'\n")

    def test_tuple_index_out_of_range(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    v = ("", 1)\n'
                             '    print(v[2])\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        print(v[2])\n'
            '                ^\n'
            "CompileError: tuple index out of range\n")

    def test_assign_to_function_call(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def bar() -> i32:\n'
                             '    return 1\n'
                             'def foo():\n'
                             '    bar() = 1\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 4\n'
            '    bar() = 1\n'
            '    ^\n'
            "SyntaxError: cannot assign to function call\n")

    def test_call_iter_functions_outside_for(self):
        # At least true for now...
        for name in ['range', 'enumerate', 'zip', 'slice', 'reversed']:
            with self.assertRaises(TranspilerError) as cm:
                transpile_source('def foo():\n'
                                 f'    v = {name}([1, 4])\n'
                                 '    print(v)')

            self.assertEqual(
                remove_ansi(str(cm.exception)),
                '  File "", line 2\n'
                f'        v = {name}([1, 4])\n'
                '            ^\n'
                "CompileError: function can only be used in for-loops\n")

    def test_main_in_non_main_file(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main():\n'
                             '    pass\n')

        self.assertEqual(str(cm.exception), 'main() is only allowed in main.mys')

    def test_no_main_in_main_file(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    pass\n',
                             has_main=True)

        self.assertEqual(str(cm.exception), 'main() not found in main.mys')

    def test_call_void_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    pass\n'
                             'def bar():\n'
                             '    foo().bar()\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        foo().bar()\n'
            '        ^\n'
            "CompileError: None has no methods\n")

    def test_call_void_2(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    pass\n'
                             'def bar():\n'
                             '    print(foo())\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        print(foo())\n'
            '              ^\n'
            "CompileError: None cannot be printed\n")

    def test_bare_compare(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    1 == 2\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        1 == 2\n'
            '        ^\n'
            "CompileError: bare comparision\n")

    def test_bare_integer(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        1\n'
            '        ^\n'
            "CompileError: bare integer\n")

    def test_bare_float(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    2.0\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        2.0\n'
            '        ^\n'
            "CompileError: bare float\n")

    def test_bare_not(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    not True\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        not True\n'
            '        ^\n'
            "CompileError: bare unary operation\n")

    def test_bare_add(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    1 + 2\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        1 + 2\n'
            '        ^\n'
            "CompileError: bare binary operation\n")

    def test_bare_name(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a: i32 = 0\n'
                             '    a\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        a\n'
            '        ^\n'
            "CompileError: bare name\n")

    def test_not_only_allowed_on_bool(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(not "hi")\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(not "hi")\n'
            '                  ^\n'
            "CompileError: expected a 'bool', got a 'string'\n")

    def test_negative_bool(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(-True)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(-True)\n'
            '              ^\n'
            "CompileError: unary '-' can only operate on numbers\n")

    def test_named_parameter_wrong_name(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: bool):\n'
                             '    print(a)\n'
                             'def bar():\n'
                             '    foo(b=True)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        foo(b=True)\n'
            '            ^\n'
            "CompileError: invalid parameter 'b'\n")

    def test_named_parameter_twice(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: bool, b: i64):\n'
                             '    print(a, b)\n'
                             'def bar():\n'
                             '    foo(b=True, b=1)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        foo(b=True, b=1)\n'
            '                    ^\n'
            "CompileError: parameter 'b' given more than once\n")

    def test_both_regular_and_named_parameter(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(a: bool):\n'
                             '    print(a)\n'
                             'def bar():\n'
                             '    foo(True, a=True)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        foo(True, a=True)\n'
            '        ^\n'
            "CompileError: expected 1 parameter, got 2\n")

    def test_named_parameter_before_regular(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: bool, b: i64):\n'
                             '    print(a, b)\n'
                             'def bar():\n'
                             '    foo(a=True, 1)\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 4\n'
            '    foo(a=True, 1)\n'
            '                 ^\n'
            "SyntaxError: positional argument follows keyword argument\n")

    def test_name_clash(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def bar():\n'
                             '    pass\n'
                             'def foo():\n'
                             '    bar = 1\n'
                             '    print(bar)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        bar = 1\n'
            '        ^\n'
            "CompileError: redefining 'bar'\n")

    def test_inline_constant_default_bool_parameter_value(self):
        source = transpile_source('def foo(a: bool = True):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(Bool(true))', source)

    def test_inline_constant_default_u8_parameter_value(self):
        source = transpile_source('def foo(a: u8 = 1):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(1)', source)

    def test_inline_constant_default_i8_parameter_value(self):
        source = transpile_source('def foo(a: i8 = -1):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(-1)', source)

    def test_inline_constant_default_f64_parameter_value(self):
        source = transpile_source('def foo(a: f64 = 5.1):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(5.1)', source)

    def test_inline_constant_default_string_parameter_value(self):
        source = transpile_source('def foo(a: string = "hi"):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(String("hi"))', source)

    def test_inline_constant_default_class_parameter_value_none(self):
        source = transpile_source('class Foo:\n'
                                  '    pass\n'
                                  'def foo(a: Foo = None):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(nullptr)', source)

    def test_inline_constant_default_tuple_parameter_value_none(self):
        source = transpile_source('def foo(a: (i8, string) = None):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(nullptr)', source)

    def test_not_inline_constant_default_class_parameter_value_not_none(self):
        source = transpile_source('class Foo:\n'
                                  '    pass\n'
                                  'def foo(a: Foo = Foo()):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(foo::lib::foo_a_default())', source)

    def test_aug_assign_wrong_integer_types(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    x: i32 = 0\n'
                             '    x += i8(1)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        x += i8(1)\n'
            '             ^\n'
            "CompileError: expected a 'i32', got a 'i8'\n")

    def test_embedded_cpp_instead_of_docstring(self):
        source = transpile_source('class Foo:\n'
                                  '    def foo(self):\n'
                                  '        "mys-embedded-c++ // nothing 1"\n'
                                  'def bar():\n'
                                  '    "mys-embedded-c++ // nothing 2"\n')

        self.assert_in('// nothing 1', source)
        self.assert_in('// nothing 2', source)

    def test_complex(self):
        # complex may be implemented at some point.
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('VAR: complex = 1 + 2j\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    VAR: complex = 1 + 2j\n'
            '         ^\n'
            "CompileError: undefined type 'complex'\n")

    def test_undefined_type_as_function_parameter(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def add(a: Foo):\n'
                             '    pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    def add(a: Foo):\n'
            '               ^\n'
            "CompileError: undefined type 'Foo'\n")

    def test_undefined_function_return_type(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def add() -> Foo:\n'
                             '    return None\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    def add() -> Foo:\n'
            '                 ^\n'
            "CompileError: undefined type 'Foo'\n")

    # ToDo
    # def test_raise_not_error_1(self):
    #     with self.assertRaises(TranspilerError) as cm:
    #         transpile_source('def add():\n'
    #                          '    raise None\n')
    #
    #     self.assert_exception_string(
    #         cm,
    #         '  File "", line 1\n'
    #         '        raise None\n'
    #         '              ^\n'
    #         "CompileError: errors must implement the Error trait\n")

    # def test_raise_not_error_2(self):
    #     with self.assertRaises(TranspilerError) as cm:
    #         transpile_source('def add():\n'
    #                          '    raise 5\n')
    #
    #     self.assert_exception_string(
    #         cm,
    #         '  File "", line 1\n'
    #         '        raise 5\n'
    #         '              ^\n'
    #         "CompileError: errors must implement the Error trait\n")

    # def test_method_name_same_as_member_name(self):
    #     with self.assertRaises(TranspilerError) as cm:
    #         transpile_source('class Bar:\n'
    #                          '    text: string\n'
    #                          '    def text(self) -> string:\n'
    #                          '        return self.text\n')
    #
    #     self.assert_exception_string(
    #         cm,
    #         '  File "", line 1\n'
    #         '    def add() -> Foo:\n'
    #         '                 ^\n'
    #         "CompileError: undefined type 'Foo'\n")
