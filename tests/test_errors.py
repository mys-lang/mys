from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_errors(self):
        build_and_test_module('errors')

    def test_bare_integer_in_try(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    try:\n'
            '        a\n'
            '    except:\n'
            '        pass\n',
            '  File "", line 3\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_bare_integer_in_except(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    try:\n'
            '        pass\n'
            '    except:\n'
            '        a\n',
            '  File "", line 5\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_try_except_different_variable_type_1(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    try:\n'
            '        x = 1\n'
            '    except:\n'
            '        x = ""\n'
            '    print(x)\n',
            '  File "", line 6\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_try_except_different_variable_type_2(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    try:\n'
            '        x = 1\n'
            '    except GeneralError:\n'
            '        x = ""\n'
            '    except ValueError:\n'
            '        x = 2\n'
            '    print(x)\n',
            '  File "", line 8\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_try_except_missing_branch(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    try:\n'
            '        x = 1\n'
            '    except GeneralError:\n'
            '        pass\n'
            '    except ValueError:\n'
            '        x = 2\n'
            '    print(x)\n',
            '  File "", line 8\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_all_branches_different_variable_type_1(self):
        self.assert_transpile_raises(
            'def foo():\n'
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
            '    print(x)\n',
            '  File "", line 15\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_missing_errors_in_raises(self):
        self.assert_transpile_raises(
            '@raises()\n'
            'def foo():\n'
            '    pass\n',
            '  File "", line 1\n'
            '    @raises()\n'
            '     ^\n'
            "CompileError: @raises requires at least one error\n")

    def test_raise_not_an_error_1(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    try:\n'
            '        raise 1\n'
            '    except:\n'
            '        pass\n',
            '  File "", line 3\n'
            '            raise 1\n'
            '                  ^\n'
            "CompileError: errors must implement the Error trait\n")

    def test_raise_not_an_error_2(self):
        self.assert_transpile_raises(
            'class Foo:\n'
            '    pass\n'
            'def foo():\n'
            '    try:\n'
            '        raise Foo()\n'
            '    except Foo:\n'
            '        pass\n',
            '  File "", line 5\n'
            '            raise Foo()\n'
            '                  ^\n'
            "CompileError: errors must implement the Error trait\n")
