import os
import shutil
import subprocess
import sys
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import build_and_test_module
from .utils import create_new_package
from .utils import create_new_package_with_files
from .utils import remove_ansi
from .utils import remove_build_directory


class Test(TestCase):

    def test_calc(self):
        build_and_test_module('calc')

    def test_hello_world(self):
        build_and_test_module('hello_world')

    def test_loops(self):
        build_and_test_module('loops')

    def test_fstrings(self):
        build_and_test_module('fstrings')

    def test_match(self):
        build_and_test_module('match')

    def test_various_1(self):
        build_and_test_module('various_1')

    def test_various_2(self):
        build_and_test_module('various_2')

    def test_various_3(self):
        build_and_test_module('various_3')

    def test_special_symbols(self):
        build_and_test_module('special_symbols')

    def test_imports(self):
        name = 'test_imports'
        remove_build_directory(name)
        shutil.copytree('tests/files/imports', f'tests/build/{name}')

        with Path(f'tests/build/{name}/mypkg'):
            with patch('sys.argv', ['mys', '-d', 'test', '-v']):
                mys.cli.main()

    def test_circular_imports(self):
        name = 'test_circular_imports'
        remove_build_directory(name)
        shutil.copytree('tests/files/circular_imports', f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            with patch('sys.argv', ['mys', '-d', 'test', '-v']):
                mys.cli.main()

    def test_filename_in_error_1(self):
        name = 'test_filename_in_error_1'
        remove_build_directory(name)
        shutil.copytree('tests/files/imports', f'tests/build/{name}')

        with Path(f'tests/build/{name}/mypkg'):
            with open("src/lib.mys", "a") as fout:
                fout.write("APA BANAN")

            with self.assertRaises(SystemExit) as cm:
                with patch('sys.argv', ['mys', 'build']):
                    mys.cli.main()

            self.assert_in('File "./src/lib.mys", line ',
                           remove_ansi(str(cm.exception)))

    def test_filename_in_error_2(self):
        name = 'test_filename_in_error_2'
        remove_build_directory(name)
        shutil.copytree('tests/files/imports', f'tests/build/{name}')

        with Path(f'tests/build/{name}/mypkg'):
            with open("src/lib.mys", "a") as fout:
                fout.write("A: bool = kaka()")

            with self.assertRaises(SystemExit) as cm:
                with patch('sys.argv', ['mys', 'build']):
                    mys.cli.main()

            self.assert_in('File "./src/lib.mys", line ',
                           remove_ansi(str(cm.exception)))

    def test_filename_in_error_in_local_dependency(self):
        name = 'test_filename_in_error_in_local_dependency'
        remove_build_directory(name)
        shutil.copytree('tests/files/imports', f'tests/build/{name}')

        with Path(f'tests/build/{name}/mypkg'):
            with open("../mypkg1/src/subpkg1/mod1.mys", "a") as fout:
                fout.write("APA BANAN")

            with self.assertRaises(SystemExit) as cm:
                with patch('sys.argv', ['mys', 'build']):
                    mys.cli.main()

            self.assert_in('File "../mypkg1/src/subpkg1/mod1.mys", line ',
                           remove_ansi(str(cm.exception)))

    def test_filename_in_error_in_dependency_from_registry(self):
        package_name = 'test_filename_in_error_in_dependency_from_registry'
        remove_build_directory(package_name)
        create_new_package(package_name)

        with Path(f'tests/build/{package_name}'):
            with open('package.toml', 'a') as fout:
                fout.write('bar = "0.3.0"\n')

            with patch('sys.argv', ['mys', 'build']):
                mys.cli.main()

            with open("build/dependencies/mys-bar-0.3.0/src/lib.mys", "a") as fout:
                fout.write("APA BANAN")

            with self.assertRaises(SystemExit) as cm:
                with patch('sys.argv', ['mys', 'build']):
                    mys.cli.main()

            self.assert_in(
                'File "build/dependencies/mys-bar-0.3.0/src/lib.mys", line ',
                remove_ansi(str(cm.exception)))

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
                'MyError(a=True, b="g")\n',
                output)
            self.assertTrue(('{1: 2, 3: 4}\n' in output)
                            or ('{3: 4, 1: 2}\n' in output))
            self.assertTrue(('{ho: Foo(v=4), hi: Foo(v=5)}\n' in output)
                            or ('{"hi": Foo(v=5), "ho": Foo(v=4)}\n' in output))
