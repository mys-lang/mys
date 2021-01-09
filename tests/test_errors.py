from mys.transpiler import TranspilerError
from .utils import transpile_source
from .utils import TestCase


class Test(TestCase):

    def test_bare_integer_in_try(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        a\n'
                             '    except:\n'
                             '        pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_bare_integer_in_except(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        pass\n'
                             '    except:\n'
                             '        a\n')

        self.assert_exception_string(
            cm,
            '  File "", line 5\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_try_except_different_variable_type_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        x = 1\n'
                             '    except:\n'
                             '        x = ""\n'
                             '    print(x)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 6\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_try_except_different_variable_type_2(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        x = 1\n'
                             '    except GeneralError:\n'
                             '        x = ""\n'
                             '    except ValueError:\n'
                             '        x = 2\n'
                             '    print(x)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 8\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_try_except_missing_branch(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        x = 1\n'
                             '    except GeneralError:\n'
                             '        pass\n'
                             '    except ValueError:\n'
                             '        x = 2\n'
                             '    print(x)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 8\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_all_branches_different_variable_type_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        if False:\n'
                             '            x = 1\n'
                             '        else:\n'
                             '            x = 2\n'
                             '    except GeneralError:\n'
                             '        try:\n'
                             '            x = 3\n'
                             '        except:\n'
                             '            if True:\n'
                             '                x: u8 = 4\n'
                             '            else:\n'
                             '                x = 5\n'
                             '    print(x)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 15\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_missing_errors_in_raises(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('@raises()\n'
                             'def foo():\n'
                             '    pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    @raises()\n'
            '     ^\n'
            "CompileError: @raises requires at least one error\n")
