from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_list(self):
        build_and_test_module('list')

    def test_type_error(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    a: u32 = [1.0]\n'
            '    print(a)\n',
            '  File "", line 2\n'
            '        a: u32 = [1.0]\n'
            '                 ^\n'
            "CompileError: cannot convert list to 'u32'\n")

    def test_return_wrong_list_type_1(self):
        self.assert_transpile_raises(
            'def foo() -> [u8]:\n'
            '    return [i8(1), -1]\n',
            '  File "", line 2\n'
            '        return [i8(1), -1]\n'
            '                ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_return_wrong_list_type_2(self):
        self.assert_transpile_raises(
            'def foo() -> [u8]:\n'
            '    return [1, i8(-1)]\n',
            '  File "", line 2\n'
            '        return [1, i8(-1)]\n'
            '                   ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_list_of_integer(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    a = list("")\n',
            '  File "", line 2\n'
            '        a = list("")\n'
            '            ^\n'
            "CompileError: list('string') not supported\n")

    def test_class_member_list_two_types(self):
        self.assert_transpile_raises(
            'class Foo:\n'
            '    a: [i32, u32]\n',
            '  File "", line 2\n'
            '        a: [i32, u32]\n'
            '           ^\n'
            "CompileError: expected 1 type in list, got 2\n")

    def test_define_empty_list_without_type(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    v = []\n'
            '    print(v)\n',
            '  File "", line 2\n'
            '        v = []\n'
            '        ^\n'
            "CompileError: cannot infer type from empty list\n")

    def test_list_with_two_types(self):
        self.assert_transpile_raises(
            'VAR: [bool, bool] = None\n',
            '  File "", line 1\n'
            '    VAR: [bool, bool] = None\n'
            '         ^\n'
            "CompileError: expected 1 type in list, got 2\n")
