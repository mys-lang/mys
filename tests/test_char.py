from .utils import TestCase
from .utils import build_and_test_module
from .utils import transpile_source


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

    def test_triple_quoted(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "    print('''f''')\n")

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            "    print('''f''')\n"
            "                 ^\n"
            'SyntaxError: characters cannot be triple quoted\n')

    def test_with_prefix(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "    print(b'f')\n")

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            "    print(b'f')\n"
            "              ^\n"
            'SyntaxError: characters cannot have a prefix\n')

    def test_concatenate(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "    print('f' 'o' 'o')\n")

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            "    print('f' 'o' 'o')\n"
            "                     ^\n"
            'SyntaxError: cannot concatenate characters\n')
