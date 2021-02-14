import os
import subprocess
import sys

from mys.transpiler import TranspilerError

from .utils import Path
from .utils import TestCase
from .utils import create_new_package_with_files
from .utils import remove_ansi
from .utils import transpile_source


class Test(TestCase):

    def test_print(self):
        module_name = 'print'
        package_name = f'test_{module_name}'
        create_new_package_with_files(package_name, module_name, 'main')
        path = os.getcwd()

        with Path('tests/build/' + package_name):
            env = os.environ
            env['PYTHONPATH'] = path
            proc = subprocess.run([sys.executable, '-m', 'mys', 'run'],
                                  input="Lobster #1\n10\n",
                                  capture_output=True,
                                  text=True,
                                  env=env)

            if proc.returncode != 0:
                print(proc.stdout)
                print(proc.stderr)

                raise Exception("Build error.")

            output = remove_ansi(proc.stdout)

            self.assert_in(
                'A string literal!\n'
                '1\n'
                '1.5\n'
                'False\n'
                'True\n'
                'Foo(v=5)\n'
                '(-500, "Hi!")\n'
                '[1, 2, 3]\n'
                'Bar(a=Foo(v=3), b=True, c="kalle")\n'
                'Foo(v=5)\n'
                '[(Foo(v=3), True), (Foo(v=5), False)]\n'
                'True\n'
                'False\n'
                'True\n'
                'None\n'
                'Fie(a=5, _b=False, _c=None)\n'
                'G\n'
                '7\n'
                "['j', 'u', 'l']\n"
                'Fam(x=None)\n'
                'Fam(x=Foo(v=4))\n'
                'Fam(x=Bar(a=None, b=False, c="kk"))\n'
                'Foo(v=-1)\n'
                'Bar(a=None, b=True, c="")\n'
                '[Foo(v=5), Bar(a=None, b=True, c="fes")]\n'
                'b""\n'
                'b"\\x01\\x02\\x03"!\n'
                '20\n'
                '1\n' # Todo: Should print "Animal.Cow".
                'Name: Lobster #1\n'
                'Age: 10\n'
                'MyError(a=True, b="g")\n'
                '[1, 4, 3]\n'
                'END\n',
                output)
            self.assertTrue(('{1: 2, 3: 4}\n' in output)
                            or ('{3: 4, 1: 2}\n' in output))
            self.assertTrue(('{"ho": Foo(v=4), "hi": Foo(v=5)}\n' in output)
                            or ('{"hi": Foo(v=5), "ho": Foo(v=4)}\n' in output))
            self.assertTrue(('{7: 49, 1: 1}\n' in output)
                            or ('{1: 1, 7: 49}\n' in output))

    def test_basic_print_function(self):
        source = transpile_source('def main():\n'
                                  '    print(1)\n',
                                  has_main=True)

        self.assert_in('std::cout << 1 << "\\n";', source)

    def test_print_function_with_flush_true(self):
        source = transpile_source('def main():\n'
                                  '    print(1, flush=True)\n',
                                  has_main=True)

        self.assert_in('    std::cout << 1 << "\\n";\n'
                       '    if (mys::Bool(true)) {\n'
                       '        std::cout << std::flush;\n'
                       '    }',
                       source)

    def test_print_function_with_flush_false(self):
        source = transpile_source('def main():\n'
                                  '    print(1, flush=False)\n',
                                  has_main=True)

        self.assert_in('std::cout << 1 << "\\n";', source)

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
            '<< " " << u16(1) << "\\n";\n',
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
