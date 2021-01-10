from mys.transpiler import TranspilerError

from .utils import TestCase
from .utils import transpile_source


class Test(TestCase):

    def test_basic_print_function(self):
        source = transpile_source('def main():\n'
                                  '    print(1)\n',
                                  has_main=True)

        self.assert_in('std::cout << 1 << std::endl;', source)

    def test_print_function_with_flush_true(self):
        source = transpile_source('def main():\n'
                                  '    print(1, flush=True)\n',
                                  has_main=True)

        self.assert_in('    std::cout << 1 << std::endl;\n'
                       '    if (Bool(true)) {\n'
                       '        std::cout << std::flush;\n'
                       '    }',
                       source)

    def test_print_function_with_flush_false(self):
        source = transpile_source('def main():\n'
                                  '    print(1, flush=False)\n',
                                  has_main=True)

        self.assert_in('std::cout << 1 << std::endl;', source)

    def test_print_function_with_and_and_flush(self):
        source = transpile_source('def main():\n'
                                  '    print(1, end="!!", flush=True)\n',
                                  has_main=True)

        self.assert_in('std::cout << std::flush;\n',
                       source)

    def test_print_function_i8_u8_as_integers_not_char(self):
        source = transpile_source('def main():\n'
                                  '    print(i8(-1), u8(1), u16(1))\n',
                                  has_main=True)

        self.assert_in(
            '    std::cout << (int)i8(-1) << " " << (unsigned)u8(1) '
            '<< " " << u16(1) << std::endl;\n',
            source)

    def test_print_function_invalid_keyword(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def main():\n'
                             '    print("Hi!", foo=True)\n',
                             'src/mod.mys',
                             'pkg/mod.mys.hpp',
                             has_main=True)

        self.assert_exception_string(
            cm,
            '  File "src/mod.mys", line 2\n'
            '        print("Hi!", foo=True)\n'
            '        ^\n'
            "CompileError: invalid keyword argument 'foo' to print(), only "
            "'end' and 'flush' are allowed\n")
