from mys.transpiler import TranspilerError
from .utils import transpile_source
from .utils import TestCase


class Test(TestCase):

    def test_undefined_variable_1(self):
        # Everything ok, 'value' defined.
        transpile_source('def foo(value: bool) -> bool:\n'
                         '    return value\n')

        # Error, 'value' is not defined.
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return value\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return value\n'
            '               ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_variable_2(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo() -> i32:\n'
                             '    return 2 * value\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        return 2 * value\n'
            '                   ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_variable_3(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo(v1: i32, v2: i32) -> i32:\n'
                             '    return v1 + v2\n'
                             'def bar() -> i32:\n'
                             '    a: i32 = 1\n'
                             '    return foo(a, value)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 5\n'
            '        return foo(a, value)\n'
            '                      ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_variable_5(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a: i8 = a\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            "        a: i8 = a\n"
            '                ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_undefined_variable_6(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a: [i8] = a\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            "        a: [i8] = a\n"
            '                  ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_undefined_variable_7(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    if a == "":\n'
                             '        print("hej")\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        if a == "":\n'
            '           ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_undefined_variable_in_fstring(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def bar():\n'
                             '    print(f"{value}")\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(f"{value}")\n'
            '                 ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_variable_index(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    bar[0] = True\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        bar[0] = True\n'
            '        ^\n'
            "CompileError: undefined variable 'bar'\n")

    def test_only_global_defined_in_callee(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('GLOB: bool = True\n'
                             'def bar() -> i32:\n'
                             '    a: i32 = 1\n'
                             '    print(a)\n'
                             'def foo() -> i32:\n'
                             '    return GLOB + a\n')

        self.assert_exception_string(
            cm,
            '  File "", line 6\n'
            '        return GLOB + a\n'
            '                      ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_non_snake_case_global_variable(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('Aa: i32 = 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    Aa: i32 = 1\n'
            '    ^\n'
            "CompileError: global variable names must be upper case snake case\n")

    def test_non_snake_case_local_variable(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    A: i32 = 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        A: i32 = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_underscore_variable_name(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    _: i32 = 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        _: i32 = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_underscore_inferred_variable_name(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    _ = 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        _ = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_non_snake_case_local_inferred_variable(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    A = 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        A = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_global_variables_can_not_be_redefeined(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('A: u8 = 1\n'
                             'A: u8 = 2\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '    A: u8 = 2\n'
            '    ^\n'
            "CompileError: there is already a variable called 'A'\n")

    def test_global_variable_types_can_not_be_inferred(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('a = 2\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    a = 2\n'
            '    ^\n'
            "CompileError: global variable types cannot be inferred\n")

    def test_no_variable_init(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             "    a: u8\n"
                             '    a = 1\n'
                             '    print(a)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            "        a: u8\n"
            '        ^\n'
            "CompileError: variables must be initialized when declared\n")

    def test_global_undefined_variable(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('V: i8 = (1 << K)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    V: i8 = (1 << K)\n'
            '                  ^\n'
            "CompileError: undefined variable 'K'\n")

    def test_global_use_variable_of_wrong_type(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('K: u8 = 1\n'
                             'V: i8 = (1 << K)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '    V: i8 = (1 << K)\n'
            '             ^\n'
            "CompileError: expected a 'i8', got a 'u8'\n")

    def test_global_integer(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    1\n'
            '    ^\n'
            "CompileError: syntax error\n")

    def test_unknown_local_variable_type(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a: u9 = 0\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        a: u9 = 0\n'
            '           ^\n'
            "CompileError: undefined type 'u9'\n")

    def test_unknown_global_variable_type_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('A: i9 = 0\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    A: i9 = 0\n'
            '       ^\n'
            "CompileError: undefined type 'i9'\n")

    def test_unknown_global_variable_type_2(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('A: [(bool, i9)] = None\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    A: [(bool, i9)] = None\n'
            '       ^\n'
            "CompileError: undefined type '[(bool, i9)]'\n")

    def test_unknown_global_variable_type_3(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('A: i10 = a\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    A: i10 = a\n'
            '       ^\n'
            "CompileError: undefined type 'i10'\n")
