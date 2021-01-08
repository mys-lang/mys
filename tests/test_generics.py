import os
from .utils import build_and_test_module
from .utils import TestCase
from .utils import transpile_source
from .utils import remove_ansi


class Test(TestCase):

    def setUp(self):
        os.makedirs('tests/build', exist_ok=True)

    def test_generics(self):
        build_and_test_module('generics')

    def test_missing_generic_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@generic\n'
                             'def foo():\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @generic\n'
            '     ^\n'
            "CompileError: at least one parameter required\n")

    def test_generic_given_more_than_once(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@generic(T1)\n'
                             '@generic(T2)\n'
                             'def foo(a: T1, b: T2):\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '    @generic(T2)\n'
            '     ^\n'
            "CompileError: @generic can only be given once\n")

    def test_generic_type_given_more_than_once(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@generic(T1, T1)\n'
                             'def foo(a: T1):\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @generic(T1, T1)\n'
            '                 ^\n'
            "CompileError: 'T1' can only be given once\n")
        
    # ToDo
    # def test_genric_undefined_type(self):
    #     with self.assertRaises(Exception) as cm:
    #         transpile_source('@generic(T)\n'
    #                          'def add(a: T) -> T:\n'
    #                          '    return a\n'
    #                          'def foo():\n'
    #                          '    print(add[Foo](None))\n')
    #
    #     self.assertEqual(
    #         remove_ansi(str(cm.exception)),
    #         '  File "", line 1\n'
    #         '    VAR: complex = 1 + 2j\n'
    #         '         ^\n'
    #         "CompileError: undefined type 'complex'\n")
