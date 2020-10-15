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
            transpile('def main(argv: i32): pass', '', '')

        self.assertEqual(str(cm.exception),
                         "main() takes 'argv: [string]' or no arguments.")

    def test_invalid_main_return_type(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main() -> i32: pass', '', '')

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

    def test_empty_function(self):
        _, source = transpile('def foo():\n'
                              '    pass\n',
                              '<unknown>',
                              '')

        self.assertIn('void foo(void)\n'
                      '{\n'
                      '\n'
                      '}\n',
                      source)

    def test_multiple_imports_failure(self):
        with self.assertRaises(Exception) as cm:
            transpile('from foo import bar, fie\n',
                      '<unknown>',
                      '')

        if sys.version_info < (3, 8):
            return

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<unknown>", line 1\n'
            '    from foo import bar, fie\n'
            '    ^\n'
            'LanguageError: only one import is allowed, found 2\n')

    def test_relative_import_outside_package(self):
        with self.assertRaises(Exception) as cm:
            transpile('from .. import fie\n',
                      'src/mod.mys',
                      'pkg/mod.mys.hpp')

        if sys.version_info < (3, 8):
            return

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "src/mod.mys", line 1\n'
            '    from .. import fie\n'
            '    ^\n'
            'LanguageError: relative import is outside package\n')

    def test_comaprsion_operator_return_types(self):
        ops = ['eq', 'ne', 'gt', 'ge', 'lt', 'le']

        for op in ops:
            with self.assertRaises(Exception) as cm:
                transpile('class Foo:\n'
                          f'    def __{op}__(self, other: Foo):\n'
                          '        return True\n',
                          'src/mod.mys',
                          'pkg/mod.mys.hpp')

            if sys.version_info < (3, 8):
                return

            self.assertEqual(
                remove_ansi(str(cm.exception)),
                '  File "src/mod.mys", line 2\n'
                f'        def __{op}__(self, other: Foo):\n'
                '        ^\n'
                f'LanguageError: __{op}__() must return bool\n')

    def test_arithmetic_operator_return_types(self):
        ops = ['add', 'sub']

        for op in ops:
            with self.assertRaises(Exception) as cm:
                transpile('class Foo:\n'
                          f'    def __{op}__(self, other: Foo) -> bool:\n'
                          '        return True\n',
                          'src/mod.mys',
                          'pkg/mod.mys.hpp')

            if sys.version_info < (3, 8):
                return

            self.assertEqual(
                remove_ansi(str(cm.exception)),
                '  File "src/mod.mys", line 2\n'
                f'        def __{op}__(self, other: Foo) -> bool:\n'
                '        ^\n'
                f'LanguageError: __{op}__() must return Foo\n')

    def test_basic_print_function(self):
        _, source = transpile('def main():\n'
                              '    print("Hi!")\n',
                              'src/mod.mys',
                              'pkg/mod.mys.hpp')

        self.assertIn('std::cout << "Hi!" << std::endl;', source)

    def test_print_function_with_end(self):
        _, source = transpile('def main():\n'
                              '    print("Hi!", end="")\n',
                              'src/mod.mys',
                              'pkg/mod.mys.hpp')

        self.assertIn('std::cout << "Hi!" << "";', source)

    def test_print_function_with_flush_true(self):
        _, source = transpile('def main():\n'
                              '    print("Hi!", flush=True)\n',
                              'src/mod.mys',
                              'pkg/mod.mys.hpp')

        self.assertIn('    std::cout << "Hi!" << std::endl;\n'
                      '    if (true) {\n'
                      '        std::cout << std::flush;\n'
                      '    }',
                      source)


    def test_print_function_with_flush_false(self):
        _, source = transpile('def main():\n'
                              '    print("Hi!", flush=False)\n',
                              'src/mod.mys',
                              'pkg/mod.mys.hpp')

        self.assertIn('std::cout << "Hi!" << std::endl;', source)

    def test_print_function_with_and_and_flush(self):
        _, source = transpile('def main():\n'
                              '    print("Hi!", end="!!", flush=True)\n',
                              'src/mod.mys',
                              'pkg/mod.mys.hpp')

        self.assertIn('    std::cout << "Hi!" << "!!";\n'
                      '    if (true) {\n'
                      '        std::cout << std::flush;\n'
                      '    }',
                      source)



    def test_print_function_invalid_keyword(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main():\n'
                      '    print("Hi!", foo=True)\n',
                      'src/mod.mys',
                      'pkg/mod.mys.hpp')

        if sys.version_info < (3, 8):
            return

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "src/mod.mys", line 2\n'
            '        print("Hi!", foo=True)\n'
            '        ^\n'
            "LanguageError: invalid keyword argument 'foo' to print(), only "
            "'end' and 'flush' are allowed\n")
