import os
import shutil
import subprocess
from io import StringIO
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import create_new_package
from .utils import read_file
from .utils import remove_ansi
from .utils import remove_build_directory
from .utils import run_mys_command


class Test(TestCase):

    def assert_files_equal(self, actual, expected):
        # os.makedirs(os.path.dirname(expected), exist_ok=True)
        # open(expected, 'w').write(open(actual, 'r').read())
        self.assertEqual(read_file(actual), read_file(expected))

    def assert_file_exists(self, path):
        self.assertTrue(os.path.exists(path))

    def test_foo_new_and_run(self):
        package_name = 'test_foo_new_and_run'
        remove_build_directory(package_name)

        with Path('tests/build'):
            command = [
                'mys', 'new',
                '--author', 'Test Er <test.er@mys.com>',
                package_name
            ]

            stdout = StringIO()

            with patch('sys.stdout', stdout):
                with patch('sys.argv', command):
                    mys.cli.main()

        self.assert_in(
            '┌────────────────────────────────────────────────── 💡 ─┐\n'
            '│ Build and run the new package by typing:              │\n'
            '│                                                       │\n'
            f'│ cd {package_name}                               │\n'
            '│ mys run                                               │\n'
            '└───────────────────────────────────────────────────────┘\n',
            remove_ansi(stdout.getvalue()))

        self.assert_files_equal(f'tests/build/{package_name}/package.toml',
                                'tests/files/foo/package.toml')
        self.assert_files_equal(f'tests/build/{package_name}/.gitignore',
                                'tests/files/foo/.gitignore')
        self.assert_files_equal(f'tests/build/{package_name}/.gitattributes',
                                'tests/files/foo/.gitattributes')
        self.assert_files_equal(f'tests/build/{package_name}/README.rst',
                                'tests/files/foo/README.rst')
        self.assert_files_equal(f'tests/build/{package_name}/LICENSE',
                                'tests/files/foo/LICENSE')
        self.assert_files_equal(f'tests/build/{package_name}/src/main.mys',
                                'tests/files/foo/src/main.mys')
        self.assert_files_equal(f'tests/build/{package_name}/src/lib.mys',
                                'tests/files/foo/src/lib.mys')

        with Path(f'tests/build/{package_name}'):
            # Run.
            self.assertFalse(os.path.exists('./build/app'))

            with patch('sys.argv', ['mys', 'run', '-j', '1']):
                mys.cli.main()

            self.assert_file_exists(
                f'build/cpp/src/{package_name}/main.mys.cpp')
            self.assert_file_exists('build/app')

            # Clean.
            self.assert_file_exists('build')

            with patch('sys.argv', ['mys', '-d', 'clean']):
                mys.cli.main()

            self.assertFalse(os.path.exists('build'))

            # Build.
            with patch('sys.argv', ['mys', '-d', 'build', '-j', '1']):
                mys.cli.main()

            self.assert_file_exists('./build/app')

            # Run again, but with run() mock to verify that the
            # application is run.
            run_result = Mock()
            run_mock = Mock(side_effect=run_result)

            with patch('subprocess.run', run_mock):
                with patch('sys.argv', ['mys', 'run', '-j', '1']):
                    mys.cli.main()

            # -j 1 is not passed to make if a jobserver is already
            # running.
            self.assertIn(
                run_mock.mock_calls,
                [
                    [
                        call(['make', '-f', 'build/Makefile', 'all',
                              '-s', 'APPLICATION=yes'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             encoding='utf-8',
                             close_fds=False,
                             env=None),
                        call(['./build/app'], check=True)
                    ],
                    [
                        call(['make', '-f', 'build/Makefile', 'all',
                              '-j', '1', '-s', 'APPLICATION=yes'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             encoding='utf-8',
                             close_fds=False,
                             env=None),
                        call(['./build/app'], check=True)
                    ]
                ])

            # Test.
            with patch('sys.argv', ['mys', '-d', 'test', '-j', '1']):
                mys.cli.main()

            self.assert_file_exists('./build/test')

    def test_new_author_from_git(self):
        package_name = 'test_new_author_from_git'
        remove_build_directory(package_name)

        check_output_mock = Mock(side_effect=['First Last', 'first.last@test.org'])

        with Path('tests/build'):
            with patch('subprocess.check_output', check_output_mock):
                with patch('sys.argv', ['mys', '-d', 'new', package_name]):
                    mys.cli.main()

        self.assertEqual(
            check_output_mock.mock_calls,
            [
                call(['git', 'config', '--get', 'user.name'], encoding='utf-8'),
                call(['git', 'config', '--get', 'user.email'], encoding='utf-8')
            ])

        self.assert_files_equal(f'tests/build/{package_name}/package.toml',
                                'tests/files/test_new_author_from_git/package.toml')

    def test_new_git_command_failure(self):
        package_name = 'test_new_git_command_failure'
        remove_build_directory(package_name)

        check_output_mock = Mock(side_effect=Exception())
        getuser_mock = Mock(side_effect=['mystester'])

        with Path('tests/build'):
            with patch('subprocess.check_output', check_output_mock):
                with patch('getpass.getuser', getuser_mock):
                    with patch('sys.argv', ['mys', '-d', 'new', package_name]):
                        mys.cli.main()

        self.assertEqual(
            check_output_mock.mock_calls,
            [
                call(['git', 'config', '--get', 'user.name'], encoding='utf-8'),
                call(['git', 'config', '--get', 'user.email'], encoding='utf-8')
            ])

        self.assert_files_equal(f'tests/build/{package_name}/package.toml',
                                f'tests/files/test_{package_name}/package.toml')

    def test_new_multiple_authors(self):
        package_name = 'test_new_multiple_authors'
        remove_build_directory(package_name)

        with Path('tests/build'):
            command = [
                'mys', '-d', 'new',
                '--author', 'Test Er <test.er@mys.com>',
                '--author', 'Test2 Er2 <test2.er2@mys.com>',
                package_name
            ]

            with patch('sys.argv', command):
                mys.cli.main()

        self.assert_files_equal(f'tests/build/{package_name}/package.toml',
                                f'tests/files/{package_name}/package.toml')

    def test_publish(self):
        package_name = 'test_publish'
        remove_build_directory(package_name)
        create_new_package(package_name)

        with Path(f'tests/build/{package_name}'):
            # Publish.
            run_sdist_result = Mock()
            run_twine_result = Mock()
            run_mock = Mock(side_effect=[run_sdist_result, run_twine_result])

            with patch('sys.argv', ['mys', '-d', 'publish', '-u', 'a', '-p', 'b']):
                with patch('subprocess.run', run_mock):
                    mys.cli.main()

            # sdist.
            the_call = run_mock.call_args_list[0]
            self.assertEqual(the_call.args[0][1:], ['setup.py', 'sdist'])
            self.assertEqual(the_call.kwargs,
                             {
                                 'stdout': subprocess.PIPE,
                                 'stderr': subprocess.STDOUT,
                                 'encoding': 'utf-8',
                                 'close_fds': False,
                                 'env': None
                             })

            # twine.
            the_call = run_mock.call_args_list[1]
            self.assertEqual(the_call.args[0][1:], ['-m', 'twine', 'upload'])
            self.assertEqual(the_call.kwargs['stdout'], subprocess.PIPE)
            self.assertEqual(the_call.kwargs['stderr'], subprocess.STDOUT)
            self.assertEqual(the_call.kwargs['encoding'], 'utf-8')
            self.assertEqual(the_call.kwargs['env']['TWINE_USERNAME'], 'a')
            self.assertEqual(the_call.kwargs['env']['TWINE_PASSWORD'], 'b')

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

    def test_build_outside_package(self):
        # Empty directory.
        package_name = 'test_build_outside_package'
        remove_build_directory(package_name)

        with Path('tests/build'):
            os.makedirs(package_name)

        with Path(f'tests/build/{package_name}'):
            # Build.
            stdout = StringIO()

            with patch('sys.stdout', stdout):
                with self.assertRaises(SystemExit):
                    with patch('sys.argv', ['mys', 'build', '-j', '1']):
                        mys.cli.main()

                expected = '''\
┌──────────────────────────────────────────────────────────────── 💡 ─┐
│ Current directory does not contain a Mys package (package.toml does │
│ not exist).                                                         │
│                                                                     │
│ Please enter a Mys package directory, and try again.                │
│                                                                     │
│ You can create a new package with mys new <name>.                   │
└─────────────────────────────────────────────────────────────────────┘
'''

            self.assert_in(expected, remove_ansi(stdout.getvalue()))

    def test_verbose_build_and_run(self):
        # New.
        package_name = 'test_verbose_build_and_run'
        remove_build_directory(package_name)
        create_new_package(package_name)

        with Path(f'tests/build/{package_name}'):
            # Build.
            stdout = StringIO()

            with patch('sys.stdout', stdout):
                with patch('sys.argv', ['mys', '-d', 'build', '--verbose']):
                    mys.cli.main()

            self.assert_in(
                '✔ Building (',
                remove_ansi(stdout.getvalue()))

            # Run.
            stdout = StringIO()

            with patch('sys.stdout', stdout):
                with patch('sys.argv', ['mys', '-d', 'run', '--verbose']):
                    mys.cli.main()

            self.assert_in(
                '✔ Building (',
                remove_ansi(stdout.getvalue()))

    def test_lint(self):
        # New.
        package_name = 'test_lint'
        remove_build_directory(package_name)
        create_new_package(package_name)

        with Path(f'tests/build/{package_name}'):
            # Lint without errors.
            stdout = StringIO()

            with patch('sys.stdout', stdout):
                with patch('sys.argv', ['mys', '-d', 'lint']):
                    mys.cli.main()

            self.assertNotIn(
                ' ERROR invalid syntax (<unknown>, line 3) '
                '(syntax-error)',
                remove_ansi(stdout.getvalue()))

            # Lint with error.
            with open('src/main.mys', 'a') as fout:
                fout.write('some crap')

            stdout = StringIO()

            with patch('sys.stdout', stdout):
                with self.assertRaises(SystemExit):
                    with patch('sys.argv', ['mys', 'lint']):
                        mys.cli.main()

            self.assert_in(
                ' ERROR invalid syntax (<unknown>, line 3) '
                '(syntax-error)',
                remove_ansi(stdout.getvalue()))

    def test_build_empty_package_should_fail(self):
        package_name = 'test_build_empty_package_should_fail'
        remove_build_directory(package_name)
        create_new_package(package_name)

        with Path(f'tests/build/{package_name}'):
            os.remove('src/lib.mys')
            os.remove('src/main.mys')

            # Build.
            stdout = StringIO()

            with patch('sys.stdout', stdout):
                with self.assertRaises(SystemExit):
                    with patch('sys.argv', ['mys', 'build']):
                        mys.cli.main()

            self.assert_in(
                '┌─────────────────────────────────────────────────── ❌️ ─┐\n'
                "│ 'src/' is empty. Please create one or more .mys-files. │\n"
                '└────────────────────────────────────────────────────────┘\n',
                remove_ansi(stdout.getvalue()))

    def test_install_local_package_with_local_dependencies(self):
        package_name = 'test_install_local_package_with_local_dependencies'
        remove_build_directory(package_name)
        shutil.copytree('tests/files/install', f'tests/build/{package_name}')

        with Path(f'tests/build/{package_name}/foo'):
            command = ['mys', '-d', 'install', '--root', '..']

            with patch('sys.argv', command):
                mys.cli.main()

            proc = subprocess.run(['../bin/foo'],
                                  check=True,
                                  capture_output=True,
                                  text=True)
            self.assertEqual(proc.stdout, "hello\n")

    def test_install_package_from_registry(self):
        package_name = 'test_install_package_from_registry'
        remove_build_directory(package_name)
        os.makedirs(f'tests/build/{package_name}')

        with Path(f'tests/build/{package_name}'):
            command = ['mys', 'install', '--root', '.', 'hello_world']
            path = os.getcwd()

            try:
                with patch('sys.argv', command):
                    mys.cli.main()
            finally:
                os.chdir(path)

            proc = subprocess.run(['bin/hello_world'],
                                  check=True,
                                  capture_output=True,
                                  text=True)
            self.assertEqual(proc.stdout, "Hello, world!\n")

    def test_make_jobserver_unavaiable_warning(self):
        package_name = 'test_make_jobserver_unavaiable_warning'
        remove_build_directory(package_name)
        create_new_package(package_name)
        path = os.getcwd()

        with Path(f'tests/build/{package_name}'):
            _, stderr = run_mys_command(['build', '-v'], path)

            self.assertNotIn('jobserver unavailable', stderr)

        with Path(f'tests/build/{package_name}'):
            _, stderr = run_mys_command(['run', '-v'], path)

            self.assertNotIn('jobserver unavailable', stderr)

        with Path(f'tests/build/{package_name}'):
            _, stderr = run_mys_command(['test', '-v'], path)

            self.assertNotIn('jobserver unavailable', stderr)
