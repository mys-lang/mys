from .utils import build_and_test_module
from .utils import TestCase
from .utils import transpile_source
from .utils import remove_ansi


class Test(TestCase):

    def test_char(self):
        build_and_test_module('char_')

    def test_bad_char_literal(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "    print('foo')\n")

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            "        print('foo')\n"
            "              ^\n"
            'CompileError: bad character literal\n')
