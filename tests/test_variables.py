from .utils import TestCase
from .utils import build_and_test_module
from .utils import transpile_source


class Test(TestCase):

    def test_char(self):
        build_and_test_module('variables')

    def test_undefined_variable_1(self):
        # Everything ok, 'value' defined.
        transpile_source('def foo(value: bool) -> bool:\n'
                         '    return value\n')

        # Error, 'value' is not defined.
        self.assert_transpile_raises(
            'def foo() -> bool:\n'
            '    return value\n',
            '  File "", line 2\n'
            '        return value\n'
            '               ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_variable_2(self):
        self.assert_transpile_raises(
            'def foo() -> i32:\n'
            '    return 2 * value\n',
            '  File "", line 2\n'
            '        return 2 * value\n'
            '                   ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_variable_3(self):
        self.assert_transpile_raises(
            'def foo(v1: i32, v2: i32) -> i32:\n'
            '    return v1 + v2\n'
            'def bar() -> i32:\n'
            '    a: i32 = 1\n'
            '    return foo(a, value)\n',
            '  File "", line 5\n'
            '        return foo(a, value)\n'
            '                      ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_variable_5(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    a: i8 = a\n',
            '  File "", line 2\n'
            "        a: i8 = a\n"
            '                ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_undefined_variable_6(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    a: [i8] = a\n',
            '  File "", line 2\n'
            "        a: [i8] = a\n"
            '                  ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_undefined_variable_7(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    if a == "":\n'
            '        print("hej")\n',
            '  File "", line 2\n'
            '        if a == "":\n'
            '           ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_undefined_variable_in_fstring(self):
        self.assert_transpile_raises(
            'def bar():\n'
            '    print(f"{value}")\n',
            '  File "", line 2\n'
            '        print(f"{value}")\n'
            '                 ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_variable_index(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    bar[0] = True\n',
            '  File "", line 2\n'
            '        bar[0] = True\n'
            '        ^\n'
            "CompileError: undefined variable 'bar'\n")

    def test_only_global_defined_in_callee(self):
        self.assert_transpile_raises(
            'GLOB: bool = True\n'
            'def bar() -> i32:\n'
            '    a: i32 = 1\n'
            '    return a\n'
            'def foo() -> i32:\n'
            '    return GLOB + a\n',
            '  File "", line 6\n'
            '        return GLOB + a\n'
            '                      ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_non_snake_case_global_variable(self):
        self.assert_transpile_raises(
            'Aa: i32 = 1\n',
            '  File "", line 1\n'
            '    Aa: i32 = 1\n'
            '    ^\n'
            "CompileError: global variable names must be upper case snake case\n")

    def test_non_snake_case_local_variable(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    A: i32 = 1\n',
            '  File "", line 2\n'
            '        A: i32 = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_underscore_variable_name(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    _: i32 = 1\n',
            '  File "", line 2\n'
            '        _: i32 = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_underscore_inferred_variable_name(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    _ = 1\n',
            '  File "", line 2\n'
            '        _ = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_non_snake_case_local_inferred_variable(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    A = 1\n',
            '  File "", line 2\n'
            '        A = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_global_variables_can_not_be_redefeined(self):
        self.assert_transpile_raises(
            'A: u8 = 1\n'
            'A: u8 = 2\n',
            '  File "", line 2\n'
            '    A: u8 = 2\n'
            '    ^\n'
            "CompileError: there is already a variable called 'A'\n")

    def test_global_variable_types_can_not_be_inferred(self):
        self.assert_transpile_raises(
            'a = 2\n',
            '  File "", line 1\n'
            '    a = 2\n'
            '    ^\n'
            "CompileError: global variable types cannot be inferred\n")

    def test_no_variable_init(self):
        self.assert_transpile_raises(
            'def foo():\n'
            "    a: u8\n"
            '    a = 1\n'
            '    print(a)\n',
            '  File "", line 2\n'
            "        a: u8\n"
            '        ^\n'
            "CompileError: variables must be initialized when declared\n")

    def test_global_undefined_variable(self):
        self.assert_transpile_raises(
            'V: i8 = (1 << K)\n',
            '  File "", line 1\n'
            '    V: i8 = (1 << K)\n'
            '                  ^\n'
            "CompileError: undefined variable 'K'\n")

    def test_global_use_variable_of_wrong_type(self):
        self.assert_transpile_raises(
            'K: u8 = 1\n'
            'V: i8 = (1 << K)\n',
            '  File "", line 2\n'
            '    V: i8 = (1 << K)\n'
            '             ^\n'
            "CompileError: expected a 'i8', got a 'u8'\n")

    def test_global_integer(self):
        self.assert_transpile_raises(
            '1\n',
            '  File "", line 1\n'
            '    1\n'
            '    ^\n'
            "CompileError: syntax error\n")

    def test_unknown_local_variable_type(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    a: u9 = 0\n',
            '  File "", line 2\n'
            '        a: u9 = 0\n'
            '           ^\n'
            "CompileError: undefined type 'u9'\n")

    def test_unknown_global_variable_type_1(self):
        self.assert_transpile_raises(
            'A: i9 = 0\n',
            '  File "", line 1\n'
            '    A: i9 = 0\n'
            '       ^\n'
            "CompileError: undefined type 'i9'\n")

    def test_unknown_global_variable_type_2(self):
        self.assert_transpile_raises(
            'A: [(bool, i9)] = None\n',
            '  File "", line 1\n'
            '    A: [(bool, i9)] = None\n'
            '       ^\n'
            "CompileError: undefined type '[(bool, i9)]'\n")

    def test_unknown_global_variable_type_3(self):
        self.assert_transpile_raises(
            'A: i10 = a\n',
            '  File "", line 1\n'
            '    A: i10 = a\n'
            '       ^\n'
            "CompileError: undefined type 'i10'\n")
