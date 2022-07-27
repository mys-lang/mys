from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_set(self):
        build_and_test_module('set')

    def test_type_error(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    a: u32 = {1}\n'
            '    print(a)\n',
            '  File "", line 2\n'
            '        a: u32 = {1}\n'
            '                 ^\n'
            "CompileError: cannot convert set to 'u32'\n")

    def test_type_cannot_be_optional_variable(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v: {i64?} = {}\n',
            '  File "", line 2\n'
            '        v: {i64?} = {}\n'
            '            ^\n'
            "CompileError: set type cannot be optional\n")

    def test_type_cannot_be_optional_global(self):
        self.assert_transpile_raises(
            'FOO: {i64?} = {}\n',
            '  File "", line 1\n'
            '    FOO: {i64?} = {}\n'
            '          ^\n'
            "CompileError: set type cannot be optional\n")

    def test_type_cannot_be_optional_function_parameter(self):
        self.assert_transpile_raises(
            'func foo(x: {i64?}):\n'
            '    pass\n',
            '  File "", line 1\n'
            '    func foo(x: {i64?}):\n'
            '                 ^\n'
            "CompileError: set type cannot be optional\n")
