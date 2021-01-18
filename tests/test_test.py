import shutil
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import build_and_test_module
from .utils import create_new_package
from .utils import remove_ansi
from .utils import remove_build_directory


class Test(TestCase):

    def test_calc(self):
        build_and_test_module('calc')

    def test_hello_world(self):
        build_and_test_module('hello_world')

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
