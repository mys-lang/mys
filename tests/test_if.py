from mys.transpiler import TranspilerError
from .utils import transpile_source
from .utils import TestCase


class Test(TestCase):

    def test_value_if_cond_else_value_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(1 if 1 else 2)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(1 if 1 else 2)\n'
            '                   ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

    def test_value_if_cond_else_value_2(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    print(1 if True else "")\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        print(1 if True else "")\n'
            '                             ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_if_cond_as_non_bool(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    if 1:\n'
                             '        pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        if 1:\n'
            '           ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

    def test_bare_name_in_if(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a: i32 = 0\n'
                             '    if True:\n'
                             '        a\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_bare_name_in_else(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    a: i32 = 0\n'
                             '    if True:\n'
                             '        pass\n'
                             '    else:\n'
                             '        a\n')

        self.assert_exception_string(
            cm,
            '  File "", line 6\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_variable_defined_in_if_can_not_be_used_after(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    if True:\n'
                             '        v = 1\n'
                             '    print(v)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        print(v)\n'
            '              ^\n'
            "CompileError: undefined variable 'v'\n")

    def test_if_else_different_variable_type_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    if False:\n'
                             '        x: i8 = 1\n'
                             '    else:\n'
                             '        x: i16 = 2\n'
                             '    print(x)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 6\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_if_else_different_variable_type_2(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    if False:\n'
                             '        x = 1\n'
                             '    elif True:\n'
                             '        x = 2\n'
                             '    else:\n'
                             '        if True:\n'
                             '            x = ""\n'
                             '        else:\n'
                             '            x = 3\n'
                             '    print(x)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 11\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")
