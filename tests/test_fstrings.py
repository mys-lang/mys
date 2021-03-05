from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_fstrings(self):
        build_and_test_module('fstrings')

    def test_invalid_format_spec(self):
        self.assert_transpile_raises(
            'def foo() -> string:\n'
            '    return f"{1:f}"\n',
            '  File "", line 2\n'
            '        return f"{1:f}"\n'
            '               ^\n'
            "CompileError: invalid integer format specifier 'f'\n")

    def test_invalid_format_spec_2(self):
        self.assert_transpile_raises(
            'def foo() -> string:\n'
            '    return f"{1:08d}"\n',
            '  File "", line 2\n'
            '        return f"{1:08d}"\n'
            '               ^\n'
            "CompileError: invalid integer format specifier '08d'\n")

    def test_float_with_format_spec(self):
        self.assert_transpile_raises(
            'def foo() -> string:\n'
            '    return f"{1.0:d}"\n',
            '  File "", line 2\n'
            '        return f"{1.0:d}"\n'
            '               ^\n'
            "CompileError: format specifiers are only allowed for integers\n")
