import shutil
import os
from .utils import build_and_test_module
from .utils import TestCase
from .utils import transpile_source
from .utils import remove_ansi


class Test(TestCase):

    def setUp(self):
        os.makedirs('tests/build', exist_ok=True)

    def test_list(self):
        build_and_test_module('list')

    def test_type_error_4(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a: u32 = [1.0]\n'
                             '    print(a)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        a: u32 = [1.0]\n'
            '                 ^\n'
            "CompileError: cannot convert list to 'u32'\n")

    def test_return_wrong_list_type_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> [u8]:\n'
                             '    return [i8(1), -1]\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return [i8(1), -1]\n'
            '                ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_return_wrong_list_type_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> [u8]:\n'
                             '    return [1, i8(-1)]\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return [1, i8(-1)]\n'
            '                   ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_list_of_integer(self):
        with self.assertRaises(Exception) as cm:
            source = transpile_source('def foo():\n'
                                      '    a = list("")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        a = list("")\n'
            '            ^\n'
            "CompileError: list('string') not supported\n")

    def test_class_member_list_two_types(self):
        with self.assertRaises(Exception) as cm:
            source = transpile_source('class Foo:\n'
                                      '    a: [i32, u32]\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        a: [i32, u32]\n'
            '           ^\n'
            "CompileError: expected 1 type in list, got 2\n")

    def test_list_comprehension(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print([v for v in ""])\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print([v for v in ""])\n'
            '              ^\n'
            "CompileError: list comprehension is not implemented\n")

    def test_define_empty_list_without_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v = []\n'
                             '    print(v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        v = []\n'
            '        ^\n'
            "CompileError: cannot infer type from empty list\n")

    def test_list_with_two_types(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('VAR: [bool, bool] = None\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    VAR: [bool, bool] = None\n'
            '         ^\n'
            "CompileError: expected 1 type in list, got 2\n")
