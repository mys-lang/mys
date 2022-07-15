from .utils import TestCase
from .utils import remove_ansi
from .utils import transpile_header
from .utils import transpile_source


class Test(TestCase):

    def test_invalid_decorator_value(self):
        self.assert_transpile_raises(
            '@raises(A(B))\n'
            'func foo():\n'
            '    pass\n',
            '  File "", line 1\n'
            '    @raises(A(B))\n'
            '            ^\n'
            "CompileError: invalid decorator value\n")

    def test_invalid_decorator_value_syntax(self):
        self.assert_transpile_raises(
            '@raises[A]\n'
            'func foo():\n'
            '    pass\n',
            '  File "", line 1\n'
            '    @raises[A]\n'
            '     ^\n'
            "CompileError: decorators must be @name or @name()\n")

    def test_inferred_type_combined_integers_assignment_too_big(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    value = (0xffffffffffffffff + 1)\n'
            '    print(value)\n',
            '  File "", line 2\n'
            '        value = (0xffffffffffffffff + 1)\n'
            '                 ^\n'
            "CompileError: integer literal out of range for 'i64'\n")

    def test_test_functions_not_in_header(self):
        header = transpile_header('test test_foo():\n'
                                  '    pass\n',
                                  module_hpp='foo/lib.mys.hpp')

        self.assertNotIn('test_foo', header)

    def test_return_i64_from_function_returning_string(self):
        self.assert_transpile_raises(
            'func foo() -> string:\n'
            '    return True',
            '  File "", line 2\n'
            '        return True\n'
            '               ^\n'
            "CompileError: expected a 'string', got a 'bool'\n")

    def test_return_list_from_function_returning_tuple(self):
        self.assert_transpile_raises(
            'func foo() -> (bool, i64):\n'
            '    return [1]',
            '  File "", line 2\n'
            '        return [1]\n'
            '               ^\n'
            "CompileError: cannot convert list to '(bool, i64)'\n")

    def test_return_tuple_from_function_returning_list(self):
        self.assert_transpile_raises(
            'func foo() -> [bool]:\n'
            '    return (1, True)',
            '  File "", line 2\n'
            '        return (1, True)\n'
            '               ^\n'
            "CompileError: cannot convert tuple to '[bool]'\n")

    def test_wrong_number_of_function_parameters(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    pass\n'
            'func bar():\n'
            '    foo(1)\n',
            '  File "", line 4\n'
            '        foo(1)\n'
            '        ^\n'
            "CompileError: expected 0 parameters, got 1\n")

    def test_wrong_function_parameter_type(self):
        self.assert_transpile_raises(
            'func foo(a: string):\n'
            '    pass\n'
            'func bar():\n'
            '    foo(True)\n',
            '  File "", line 4\n'
            '        foo(True)\n'
            '            ^\n'
            "CompileError: expected a 'string', got a 'bool'\n")

    def test_assign_256_to_u8(self):
        self.assert_transpile_raises(
            'A: u8 = 256\n',
            '  File "", line 1\n'
            '    A: u8 = 256\n'
            '            ^\n'
            "CompileError: integer literal out of range for 'u8'\n")

    def test_assign_over_max_to_u64(self):
        self.assert_transpile_raises(
            'A: u64 = 0x1ffffffffffffffff\n',
            '  File "", line 1\n'
            '    A: u64 = 0x1ffffffffffffffff\n'
            '             ^\n'
            "CompileError: integer literal out of range for 'u64'\n")

    def test_assign_max_to_i64(self):
        source = transpile_source('A: i64 = 0x7fffffffffffffff\n')

        self.assert_in('A = 9223372036854775807;', source)

    def test_assign_over_max_to_i64(self):
        self.assert_transpile_raises(
            'A: i64 = 0xffffffffffffffff\n',
            '  File "", line 1\n'
            '    A: i64 = 0xffffffffffffffff\n'
            '             ^\n'
            "CompileError: integer literal out of range for 'i64'\n")

    def test_assign_float_to_u8(self):
        self.assert_transpile_raises(
            'A: u8 = 2.0\n',
            '  File "", line 1\n'
            '    A: u8 = 2.0\n'
            '            ^\n'
            "CompileError: cannot convert float to 'u8'\n")

    def test_assign_negative_number_to_u32(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    k: u32 = -1\n'
            '    print(k)\n',
            '  File "", line 2\n'
            '        k: u32 = -1\n'
            '                 ^\n'
            "CompileError: integer literal out of range for 'u32'\n")

    def test_assign_positive_number_to_u32(self):
        source = transpile_source('func foo():\n'
                                  '    i: u32 = +1\n'
                                  '    j: u32 = --1\n'
                                  '    print(i, j)\n')

        self.assert_in('u32 i = 1;', source)
        self.assert_in('u32 j = 1;', source)

    def test_reassign_negative_number_to_u32(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    i: u32 = 0\n'
            '    i = -1\n'
            '    print(i)\n',
            '  File "", line 3\n'
            '        i = -1\n'
            '            ^\n'
            "CompileError: integer literal out of range for 'u32'\n")

    def test_arithmetics_on_mix_of_literals_and_known_types_too_big(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    k: i64 = 1\n'
            '    value = (0xffffffffffffffff + k)\n'
            '    print(value)\n',
            '  File "", line 3\n'
            '        value = (0xffffffffffffffff + k)\n'
            '                 ^\n'
            "CompileError: integer literal out of range for 'i64'\n")

    def test_arithmetics_on_mix_of_literals_and_known_types_negative(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    value: u8 = (-1 * 5)\n'
            '    print(value)\n',
            '  File "", line 2\n'
            '        value: u8 = (-1 * 5)\n'
            '                     ^\n'
            "CompileError: integer literal out of range for 'u8'\n")

    def test_change_integer_type(self):
        source = transpile_source('func foo():\n'
                                  '    value = (i8(-1) * i8(u32(5)))\n'
                                  '    print(value)\n')

        self.assert_in('value = (i8(-(1)) * i8(u32(5)));', source)

    def test_change_integer_type_error(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    value = (i8(-1) * u32(5))\n'
            '    print(value)\n',
            '  File "", line 2\n'
            '        value = (i8(-1) * u32(5))\n'
            '                 ^\n'
            "CompileError: types 'i8' and 'u32' differs\n")

    def test_function_call(self):
        source = transpile_source('func foo(a: i32, b: f32):\n'
                                  '    print(a, b)\n'
                                  'func bar():\n'
                                  '    foo(1, 2.1)\n')

        self.assert_in('foo(1, 2.1);', source)

    def test_tuple_unpack_variable_defined_other_type(self):
        self.assert_transpile_raises(
            'class Foo:\n'
            '    func foo(self) -> (bool, i64):\n'
            '        return (True, -5)\n'
            'func foo():\n'
            '    v = Foo()\n'
            '    b: string = ""\n'
            '    a, b = v.foo()\n',
            '  File "", line 7\n'
            '        a, b = v.foo()\n'
            '           ^\n'
            "CompileError: expected a 'string', got a 'i64'\n")

    def test_tuple_unpack_integer(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    a, b = 1\n'
            '    print(a, b)\n',
            '  File "", line 2\n'
            '        a, b = 1\n'
            '               ^\n'
            "CompileError: only tuples can be unpacked\n")

    def test_type_error_1(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    a: u16 = 1\n'
            '    b: u32 = 1\n'
            '    c = b - a\n'
            '    print(c)\n',
            '  File "", line 4\n'
            '        c = b - a\n'
            '            ^\n'
            "CompileError: types 'u32' and 'u16' differs\n")

    def test_type_error_2(self):
        self.assert_transpile_raises(
            'func foo(a: i64):\n'
            '    b: u64 = a\n'
            '    print(b)\n',
            '  File "", line 2\n'
            '        b: u64 = a\n'
            '                 ^\n'
            "CompileError: expected a 'u64', got a 'i64'\n")

    def test_type_error_3(self):
        self.assert_transpile_raises(
            'func bar() -> string:\n'
            '    return ""\n'
            'func foo():\n'
            '    b: u64 = bar()\n'
            '    print(b)\n',
            '  File "", line 4\n'
            '        b: u64 = bar()\n'
            '                 ^\n'
            "CompileError: expected a 'u64', got a 'string'\n")

    def test_type_error_4(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    a: u32 = 1\n'
            '    b = a - [1]\n'
            '    print(b)\n',
            '  File "", line 3\n'
            '        b = a - [1]\n'
            '            ^\n'
            "CompileError: cannot convert 'u32' to "
            "'[i64/i32/i16/i8/u64/u32/u16/u8]'\n")

    def test_type_error_5(self):
        self.assert_transpile_raises(
            'func foo() -> bool:\n'
            '    return\n',
            '  File "", line 2\n'
            '        return\n'
            '        ^\n'
            "CompileError: return value missing\n")

    def test_type_error_6(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    return 1\n',
            '  File "", line 2\n'
            '        return 1\n'
            '               ^\n'
            "CompileError: function does not return any value\n")

    def test_bool_op_1(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    if True or None:\n'
            '        pass\n',
            '  File "", line 2\n'
            "        if True or None:\n"
            '                   ^\n'
            "CompileError: None is not a 'bool'\n")

    def test_bool_op_2(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    if True or False and 1:\n'
            '        pass\n',
            '  File "", line 2\n'
            "        if True or False and 1:\n"
            '                             ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

    def test_docstring(self):
        source = transpile_source('func foo():\n'
                                  '    "Hi!"\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    __MYS_TRACEBACK_ENTER();\n'
                       '    __MYS_TRACEBACK_EXIT();\n'
                       '}\n',
                       source)

    def test_global_integer_out_of_range(self):
        self.assert_transpile_raises(
            'V: i8 = 1000\n',
            '  File "", line 1\n'
            "    V: i8 = 1000\n"
            '            ^\n'
            "CompileError: integer literal out of range for 'i8'\n")

    def test_global_wrong_value_type(self):
        self.assert_transpile_raises(
            'V: i8 = ""\n',
            '  File "", line 1\n'
            '    V: i8 = ""\n'
            '            ^\n'
            "CompileError: expected a 'i8', got a 'string'\n")

    def test_assign_to_wrong_type(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    a = 1\n'
            '    a = ""\n',
            '  File "", line 3\n'
            '        a = ""\n'
            '            ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_min_wrong_types(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    print(min(u8(1), u8(2), i8(2)))\n',
            '  File "", line 2\n'
            '        print(min(u8(1), u8(2), i8(2)))\n'
            '                                ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_min_no_args(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    print(min())\n',
            '  File "", line 2\n'
            '        print(min())\n'
            '              ^\n'
            "CompileError: expected at least one parameter\n")

    def test_min_wrong_return_type(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    assert min(1, 2) == i8(1)\n',
            '  File "", line 2\n'
            '        assert min(1, 2) == i8(1)\n'
            '               ^\n'
            "CompileError: types 'i64' and 'i8' differs\n")

    def test_max_wrong_types(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    print(max(i8(1), i8(2), u8(2)))\n',
            '  File "", line 2\n'
            '        print(max(i8(1), i8(2), u8(2)))\n'
            '                                ^\n'
            "CompileError: expected a 'i8', got a 'u8'\n")

    def test_max_no_args(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    print(max())\n',
            '  File "", line 2\n'
            '        print(max())\n'
            '              ^\n'
            "CompileError: expected at least one parameter\n")

    def test_max_wrong_return_type(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    assert max(u8(1), 2) == i8(1)\n',
            '  File "", line 2\n'
            '        assert max(u8(1), 2) == i8(1)\n'
            '               ^\n'
            "CompileError: types 'u8' and 'i8' differs\n")

    def test_str_compare_to_non_string(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    assert str(0) == i8(0)\n',
            '  File "", line 2\n'
            '        assert str(0) == i8(0)\n'
            '               ^\n'
            "CompileError: types 'string' and 'i8' differs\n")

    def test_tuple_index_1(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    a = 1\n'
            '    v = (1, "b")\n'
            '    print(v[a])\n',
            '  File "", line 4\n'
            '        print(v[a])\n'
            '                ^\n'
            "CompileError: tuple indexes must be compile time known integers\n")

    def test_tuple_index_2(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v = (1, "b")\n'
            '    print(v[1 / 2])\n',
            '  File "", line 3\n'
            '        print(v[1 / 2])\n'
            '                ^\n'
            "CompileError: tuple indexes must be compile time known integers\n")

    def test_tuple_item_assign_1(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v = (1, "b")\n'
            '    v[0] = "ff"\n',
            '  File "", line 3\n'
            '        v[0] = "ff"\n'
            '               ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_tuple_item_assign_2(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    a, b, c = (1, "b")\n',
            '  File "", line 2\n'
            '        a, b, c = (1, "b")\n'
            '        ^\n'
            "CompileError: expected 3 values to unpack, got 2\n")

    def test_return_nones_as_bool_in_tuple(self):
        self.assert_transpile_raises(
            'func foo() -> (bool, bool):\n'
            '    return (None, None)\n',
            '  File "", line 2\n'
            '        return (None, None)\n'
            '                ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_return_wrong_integer_in_tuple(self):
        self.assert_transpile_raises(
            'func foo() -> (bool, u8, string):\n'
            '    return (True, i8(1), "")\n',
            '  File "", line 2\n'
            '        return (True, i8(1), "")\n'
            '                      ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_return_none_as_bool(self):
        self.assert_transpile_raises(
            'func foo() -> bool:\n'
            '    return None\n',
            '  File "", line 2\n'
            '        return None\n'
            '               ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_assign_none_to_i32(self):
        self.assert_transpile_raises(
            'A: i32 = None\n',
            '  File "", line 1\n'
            '    A: i32 = None\n'
            '             ^\n'
            "CompileError: 'i32' cannot be None\n")

    def test_return_short_tuple(self):
        self.assert_transpile_raises(
            'func foo() -> (bool, bool):\n'
            '    return (True, )\n',
            '  File "", line 2\n'
            '        return (True, )\n'
            '               ^\n'
            "CompileError: expected a '(bool, bool)', got a '(bool, )'\n")

    def test_tuple_index_out_of_range(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v = ("", 1)\n'
            '    print(v[2])\n',
            '  File "", line 3\n'
            '        print(v[2])\n'
            '                ^\n'
            "CompileError: tuple index out of range\n")

    def test_assign_to_function_call(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('func bar() -> i32:\n'
                             '    return 1\n'
                             'func foo():\n'
                             '    bar() = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<string>", line 4\n'
            '    bar() = 1\n'
            '    ^\n'
            "SyntaxError: cannot assign to function call\n")

    def test_call_iter_functions_outside_for(self):
        # At least true for now...
        for name in ['range', 'enumerate', 'zip', 'slice', 'reversed']:
            self.assert_transpile_raises(
                'func foo():\n'
                f'    v = {name}([1, 4])\n'
                '    print(v)',
                '  File "", line 2\n'
                f'        v = {name}([1, 4])\n'
                '            ^\n'
                "CompileError: function can only be used in for-loops\n")

    def test_main_in_non_main_file(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('func main():\n'
                             '    pass\n')

        self.assertEqual(str(cm.exception), 'main() is only allowed in main.mys')

    def test_no_main_in_main_file(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('func foo():\n'
                             '    pass\n',
                             has_main=True)

        self.assertEqual(str(cm.exception), 'main() not found in main.mys')

    def test_call_void_1(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    pass\n'
            'func bar():\n'
            '    foo().bar()\n',
            '  File "", line 4\n'
            '        foo().bar()\n'
            '        ^\n'
            "CompileError: None has no methods\n")

    def test_call_void_2(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    pass\n'
            'func bar():\n'
            '    print(foo())\n',
            '  File "", line 4\n'
            '        print(foo())\n'
            '              ^\n'
            "CompileError: None cannot be printed\n")

    def test_bare_integer(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    1\n',
            '  File "", line 2\n'
            '        1\n'
            '        ^\n'
            "CompileError: bare integer\n")

    def test_bare_float(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    2.0\n',
            '  File "", line 2\n'
            '        2.0\n'
            '        ^\n'
            "CompileError: bare float\n")

    def test_bare_not(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    not True\n',
            '  File "", line 2\n'
            '        not True\n'
            '        ^\n'
            "CompileError: bare unary operation\n")

    def test_bare_add(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    1 + 2\n',
            '  File "", line 2\n'
            '        1 + 2\n'
            '        ^\n'
            "CompileError: bare binary operation\n")

    def test_bare_name(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    a: i32 = 0\n'
            '    a\n',
            '  File "", line 3\n'
            '        a\n'
            '        ^\n'
            "CompileError: bare name\n")

    def test_not_only_allowed_on_bool(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    print(not "hi")\n',
            '  File "", line 2\n'
            '        print(not "hi")\n'
            '                  ^\n'
            "CompileError: expected a 'bool', got a 'string'\n")

    def test_negative_bool(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    print(-True)\n',
            '  File "", line 2\n'
            '        print(-True)\n'
            '              ^\n'
            "CompileError: unary '-' can only operate on numbers\n")

    def test_named_parameter_wrong_name(self):
        self.assert_transpile_raises(
            'func foo(a: bool):\n'
            '    print(a)\n'
            'func bar():\n'
            '    foo(b=True)\n',
            '  File "", line 4\n'
            '        foo(b=True)\n'
            '            ^\n'
            "CompileError: invalid parameter 'b'\n")

    def test_named_parameter_twice(self):
        self.assert_transpile_raises(
            'func foo(a: bool, b: i64):\n'
            '    print(a, b)\n'
            'func bar():\n'
            '    foo(b=True, b=1)\n',
            '  File "", line 4\n'
            '        foo(b=True, b=1)\n'
            '                    ^\n'
            "CompileError: parameter 'b: i64' given more than once\n")

    def test_both_regular_and_named_parameter(self):
        self.assert_transpile_raises(
            'func foo(a: bool):\n'
            '    print(a)\n'
            'func bar():\n'
            '    foo(True, a=True)\n',
            '  File "", line 4\n'
            '        foo(True, a=True)\n'
            '                  ^\n'
            "CompileError: parameter 'a: bool' given more than once\n")

    def test_both_regular_and_named_parameter_2(self):
        self.assert_transpile_raises(
            'func foo(a: (bool, string)):\n'
            '    print(a)\n'
            'func bar():\n'
            '    foo(True, a=True)\n',
            '  File "", line 4\n'
            '        foo(True, a=True)\n'
            '                  ^\n'
            "CompileError: parameter 'a: (bool, string)' given more than once\n")

    def test_named_parameter_before_regular(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('func foo(a: bool, b: i64):\n'
                             '    print(a, b)\n'
                             'func bar():\n'
                             '    foo(a=True, 1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<string>", line 4\n'
            '    foo(a=True, 1)\n'
            '                 ^\n'
            "SyntaxError: positional argument follows keyword argument\n")

    def test_name_clash(self):
        self.assert_transpile_raises(
            'func bar():\n'
            '    pass\n'
            'func foo():\n'
            '    bar = 1\n'
            '    print(bar)\n',
            '  File "", line 4\n'
            '        bar = 1\n'
            '        ^\n'
            "CompileError: redefining 'bar'\n")

    def test_inline_constant_default_bool_parameter_value(self):
        source = transpile_source('func foo(a: bool = True):\n'
                                  '    pass\n'
                                  'func bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(mys::Bool(true))', source)

    def test_inline_constant_default_u8_parameter_value(self):
        source = transpile_source('func foo(a: u8 = 1):\n'
                                  '    pass\n'
                                  'func bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(1)', source)

    def test_inline_constant_default_i8_parameter_value(self):
        source = transpile_source('func foo(a: i8 = -1):\n'
                                  '    pass\n'
                                  'func bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(-1)', source)

    def test_inline_constant_default_f64_parameter_value(self):
        source = transpile_source('func foo(a: f64 = 5.1):\n'
                                  '    pass\n'
                                  'func bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(5.1)', source)

    def test_inline_constant_default_string_parameter_value(self):
        source = transpile_source('func foo(a: string = "hi"):\n'
                                  '    pass\n'
                                  'func bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(mys::String("hi"))', source)

    def test_inline_constant_default_class_parameter_value_none(self):
        source = transpile_source('class Foo:\n'
                                  '    pass\n'
                                  'func foo(a: Foo = None):\n'
                                  '    pass\n'
                                  'func bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(nullptr)', source)

    def test_inline_constant_default_tuple_parameter_value_none(self):
        source = transpile_source('func foo(a: (i8, string) = None):\n'
                                  '    pass\n'
                                  'func bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(nullptr)', source)

    def test_not_inline_constant_default_class_parameter_value_not_none(self):
        source = transpile_source('class Foo:\n'
                                  '    pass\n'
                                  'func foo(a: Foo = Foo()):\n'
                                  '    pass\n'
                                  'func bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(mys::foo::lib::foo_a_default())', source)

    def test_aug_assign_wrong_integer_types(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    x: i32 = 0\n'
            '    x += i8(1)\n',
            '  File "", line 3\n'
            '        x += i8(1)\n'
            '             ^\n'
            "CompileError: expected a 'i32', got a 'i8'\n")

    def test_undefined_type_as_function_parameter(self):
        self.assert_transpile_raises(
            'func add(a: Foo):\n'
            '    pass\n',
            '  File "", line 1\n'
            '    func add(a: Foo):\n'
            '                ^\n'
            "CompileError: undefined type 'Foo'\n")

    def test_undefined_function_return_type(self):
        self.assert_transpile_raises(
            'func add() -> Foo:\n'
            '    return None\n',
            '  File "", line 1\n'
            '    func add() -> Foo:\n'
            '                  ^\n'
            "CompileError: undefined type 'Foo'\n")

    def test_power_f64_and_i64(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    print(2.0 ** 3)\n',
            '  File "", line 2\n'
            '        print(2.0 ** 3)\n'
            '              ^\n'
            "CompileError: cannot convert 'f64/f32' to "
            "'i64/i32/i16/i8/u64/u32/u16/u8'\n")

    # ToDo
    # def test_method_name_same_as_member_name(self):
    #     self.assert_transpile_raises(
    #         'class Bar:\n'
    #         '    text: string\n'
    #         '    func text(self) -> string:\n'
    #         '        return self.text\n',
    #         '  File "", line 1\n'
    #         '    func add() -> Foo:\n'
    #         '                 ^\n'
    #         "CompileError: undefined type 'Foo'\n")
