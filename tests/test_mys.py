import sys
import unittest
from mys.transpile import transpile

from .utils import read_file
from .utils import remove_ansi

class MysTest(unittest.TestCase):

    maxDiff = None

    def assert_equal_to_file(self, actual, expected):
        # open(expected, 'w').write(actual)
        self.assertEqual(actual, read_file(expected))

    def test_all(self):
        datas = [
            'basics'
        ]

        for data in datas:
            header, source = transpile(read_file(f'tests/files/{data}.mys'),
                                       f'{data}.mys',
                                       f'{data}.mys.hpp')
            self.assert_equal_to_file(
                header,
                f'tests/files/{data}.mys.hpp')
            self.assert_equal_to_file(
                source,
                f'tests/files/{data}.mys.cpp')

    def test_invalid_main_argument(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main(args: int): pass', '', '')

        self.assertEqual(str(cm.exception),
                         "main() takes 'args: [str]' or no arguments.")

    def test_invalid_main_return_type(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main() -> int: pass', '', '')

        self.assertEqual(str(cm.exception), "main() must return 'None'.")

    def test_lambda_not_supported(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main(): print((lambda x: x)(1))', 'foo.py', '')

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "foo.py", line 1\n'
                         '    def main(): print((lambda x: x)(1))\n'
                         '                       ^\n'
                         'LanguageError: lambda functions are not supported\n')

    def test_bad_syntax(self):
        with self.assertRaises(Exception) as cm:
            transpile('DEF main(): pass', '<unknown>', '')

        if sys.version_info < (3, 8):
            return

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "<unknown>", line 1\n'
                         '    DEF main(): pass\n'
                         '        ^\n'
                         'SyntaxError: invalid syntax\n')

    def test_import_in_function_should_fail(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main():\n'
                      '    import foo\n',
                      '<unknown>',
                      '')

        if sys.version_info < (3, 8):
            return

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<unknown>", line 2\n'
            '        import foo\n'
            '        ^\n'
            'LanguageError: imports are only allowed on module level\n')

    def test_class_in_function_should_fail(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main():\n'
                      '    class A:\n'
                      '        pass\n',
                      '<unknown>',
                      '')

        if sys.version_info < (3, 8):
            return

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<unknown>", line 2\n'
            '        class A:\n'
            '        ^\n'
            'LanguageError: class definitions are only allowed on module level\n')
