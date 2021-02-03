import shutil
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import create_new_package
from .utils import read_file
from .utils import remove_build_directory


class Test(TestCase):

    def assert_files_equal(self, actual, expected):
        # os.makedirs(os.path.dirname(expected), exist_ok=True)
        # open(expected, 'w').write(open(actual, 'r').read())
        self.assertEqual(read_file(actual), read_file(expected))

    def test_foo_build_with_local_path_dependencies(self):
        package_name = 'test_foo_build_with_local_path_dependencies'
        remove_build_directory(package_name)
        create_new_package(package_name)

        with Path(f'tests/build/{package_name}'):
            # Add dependencies.
            with open('package.toml', 'a') as fout:
                fout.write('bar = { path = "../../files/bar" }\n'
                           'fie = { path = "../../files/fie" }\n')

            # Run.
            with patch('sys.argv', ['mys', '-d', 'run', '-v']):
                mys.cli.main()

            self.assert_file_exists(
                f'build/cpp/include/{package_name}/main.mys.hpp')
            self.assert_file_exists(
                f'build/cpp/src/{package_name}/main.mys.cpp')
            self.assert_file_exists('build/cpp/include/bar/lib.mys.hpp')
            self.assert_file_exists('build/cpp/src/bar/lib.mys.cpp')
            self.assert_file_exists('build/cpp/include/fie/lib.mys.hpp')
            self.assert_file_exists('build/cpp/src/fie/lib.mys.cpp')
            self.assert_file_exists('./build/app')

    def test_foo_build_with_dependencies(self):
        # New.
        package_name = 'test_foo_build_with_dependencies'
        remove_build_directory(package_name)
        create_new_package(package_name)

        with Path(f'tests/build/{package_name}'):
            # Add dependencies.
            with open('package.toml', 'a') as fout:
                fout.write('bar = "0.3.0"\n')

            # Import from bar.
            with open('src/main.mys', 'w') as fout:
                print('from bar import hello', file=fout)
                print('', file=fout)
                print('def main():', file=fout)
                print('    v = "3.14"', file=fout)
                print('    hello(v)', file=fout)

            # Run.
            with patch('sys.argv', ['mys', '-d', 'run']):
                mys.cli.main()

            self.assert_file_exists(
                f'build/cpp/include/{package_name}/main.mys.hpp')
            self.assert_file_exists(
                f'build/cpp/src/{package_name}/main.mys.cpp')
            self.assert_file_exists('build/cpp/include/bar/lib.mys.hpp')
            self.assert_file_exists('build/cpp/src/bar/lib.mys.cpp')
            self.assert_file_exists('./build/app')

    def test_c_dependencies(self):
        name = 'test_c_dependencies'
        remove_build_directory(name)
        shutil.copytree('tests/files/c_dependencies', f'tests/build/{name}')

        with Path(f'tests/build/{name}/mypkg'):
            with patch('sys.argv', ['mys', '-d', 'test']):
                mys.cli.main()

    def test_c_dependencies_not_found(self):
        name = 'test_c_dependencies_not_found'
        remove_build_directory(name)
        shutil.copytree('tests/files/c_dependencies_not_found', f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            with patch('sys.argv', ['mys', 'test']):
                with self.assertRaises(SystemExit):
                    mys.cli.main()
