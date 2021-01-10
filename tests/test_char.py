from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_char(self):
        build_and_test_module('char_')

    def test_bad_char_literal(self):
        self.assert_transpile_raises(
            'def foo():\n'
            "    print('foo')\n",
            '  File "", line 2\n'
            "        print('foo')\n"
            "              ^\n"
            'CompileError: bad character literal\n')
