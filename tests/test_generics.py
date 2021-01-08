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
