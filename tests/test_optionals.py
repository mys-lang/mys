from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_optionals(self):
        build_and_test_module('optionals')

    def test_set_non_optional_variable_to_none(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v: string = None\n',
            '  File "", line 2\n'
            '        v: string = None\n'
            '                    ^\n'
            "CompileError: non-optional type 'string' cannot be None\n")

    def test_set_non_optional_parameter_to_none(self):
        self.assert_transpile_raises(
            'func foo(v: string):\n'
            '    v = None\n',
            '  File "", line 2\n'
            '        v = None\n'
            '            ^\n'
            "CompileError: non-optional type 'string' cannot be None\n")

    def test_set_non_optional_integer_parameter_to_none(self):
        self.assert_transpile_raises(
            'func foo(v: i64):\n'
            '    v = None\n',
            '  File "", line 2\n'
            '        v = None\n'
            '            ^\n'
            "CompileError: non-optional type 'i64' cannot be None\n")
