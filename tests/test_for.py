from .utils import TestCase


class Test(TestCase):

    def test_for_loop_underscore_variable(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for _ in [1, 4]:\n'
            '        print(_)\n',
            '  File "", line 3\n'
            '            print(_)\n'
            '                  ^\n'
            "CompileError: undefined variable '_'\n")

    def test_iterate_over_tuple(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for i in (5, 1):\n'
            '        print(i)\n',
            '  File "", line 2\n'
            '        for i in (5, 1):\n'
            '                 ^\n'
            "CompileError: iteration over tuples not allowed\n")

    def test_iterate_over_enumerate_not_tuple(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    values: [u32] = [3, 8]\n'
            '    for i in enumerate(values):\n'
            '        print(i)\n',
            '  File "", line 3\n'
            '        for i in enumerate(values):\n'
            '            ^\n'
            "CompileError: can only unpack enumerate into two variables, got 1\n")

    def test_iterate_over_slice_with_different_types_1(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for i in slice([1], 1, u16(2)):\n'
            '        print(i)\n',
            '  File "", line 2\n'
            '        for i in slice([1], 1, u16(2)):\n'
            '                               ^\n'
            "CompileError: types 'u16' and 'i64' differs\n")

    def test_iterate_over_slice_with_different_types_2(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for i in slice(range(4), 1, 2, i8(-1)):\n'
            '        print(i)\n',
            '  File "", line 2\n'
            '        for i in slice(range(4), 1, 2, i8(-1)):\n'
            '                                       ^\n'
            "CompileError: types 'i8' and 'i64' differs\n")

    def test_iterate_over_slice_no_params(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for i in slice(range(2)):\n'
            '        print(i)\n',
            '  File "", line 2\n'
            '        for i in slice(range(2)):\n'
            '                 ^\n'
            "CompileError: expected 2 to 4 parameters, got 1\n")

    def test_iterate_over_range_with_different_types_1(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for i in range(i8(1), u16(2)):\n'
            '        print(i)\n',
            '  File "", line 2\n'
            '        for i in range(i8(1), u16(2)):\n'
            '                       ^\n'
            "CompileError: types 'i8' and 'i64' differs\n")

    def test_iterate_over_range_with_different_types_2(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for i in range(1, i8(2), 2):\n'
            '        print(i)\n',
            '  File "", line 2\n'
            '        for i in range(1, i8(2), 2):\n'
            '                          ^\n'
            "CompileError: types 'i8' and 'i64' differs\n")

    def test_iterate_over_range_with_too_many_parameters(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for i in range(1, 2, 2, 2):\n'
            '        print(i)\n',
            '  File "", line 2\n'
            '        for i in range(1, 2, 2, 2):\n'
            '                 ^\n'
            "CompileError: expected 1 to 3 parameters, got 4\n")

    def test_iterate_over_enumerate_no_parameters(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for i, j in enumerate():\n'
            '        print(i)\n',
            '  File "", line 2\n'
            '        for i, j in enumerate():\n'
            '                    ^\n'
            "CompileError: expected 1 or 2 parameters, got 0\n")

    def test_iterate_over_zip_wrong_unpack(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for i in zip(range(2), range(2)):\n'
            '        print(i)\n',
            '  File "", line 2\n'
            '        for i in zip(range(2), range(2)):\n'
            '            ^\n'
            "CompileError: cannot unpack 2 values into 1\n")

    def test_iterate_over_reversed_no_parameter(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for i in reversed():\n'
            '        print(i)\n',
            '  File "", line 2\n'
            '        for i in reversed():\n'
            '                 ^\n'
            "CompileError: expected 1 parameter, got 0\n")

    def test_bare_integer_in_for(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for i in "":\n'
            '        1\n',
            '  File "", line 3\n'
            '            1\n'
            '            ^\n'
            "CompileError: bare integer\n")

    def test_variable_defined_in_for_not_be_used_after(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    l: [bool] = []\n'
            '    for _ in l:\n'
            '        v = 1\n'
            '    print(v)\n',
            '  File "", line 5\n'
            '        print(v)\n'
            '              ^\n'
            "CompileError: undefined variable 'v'\n")

    def test_fail_to_redefine_method_call_variable_in_for_loop_for_now_1(self):
        self.assert_transpile_raises(
            'class Foo:\n'
            '    def foo(self) -> [string]:\n'
            '        return []\n'
            'def foo(a: bool):\n'
            '    for a in Foo().foo():\n'
            '        print(a)\n',
            '  File "", line 5\n'
            '        for a in Foo().foo():\n'
            '            ^\n'
            "CompileError: redefining variable 'a'\n")

    def test_fail_to_redefine_method_call_variable_in_for_loop_for_now_2(self):
        self.assert_transpile_raises(
            'class Foo:\n'
            '    def foo(self) -> [(string, u8)]:\n'
            '        return []\n'
            'def foo(b: bool):\n'
            '    for a, b in Foo().foo():\n'
            '        print(a, b)\n',
            '  File "", line 5\n'
            '        for a, b in Foo().foo():\n'
            '               ^\n'
            "CompileError: redefining variable 'b'\n")

    def test_fail_slice_dict(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for k, v in slice({1: 2}):\n'
            '        print(k, v)\n',
            '  File "", line 2\n'
            '        for k, v in slice({1: 2}):\n'
            '                          ^\n'
            "CompileError: unsupported iterator type {i64: i64}\n")
