from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_complex(self):
        build_and_test_module('complex')

    def test_j_instead_of_i(self):
        self.assert_transpile_raises(
            'def foo():\n'
            "    print(1 + 2i)\n",
            '  File "", line 2\n'
            '        print(1 + 2i)\n'
            "                  ^\n"
            'CompileError: complex numbers are not supported\n')

    def test_complex_type(self):
        self.assert_transpile_raises(
            'VAR: complex = 1 + 3i\n',
            '  File "", line 1\n'
            '    VAR: complex = 1 + 3i\n'
            '         ^\n'
            "CompileError: undefined type 'complex'\n")
