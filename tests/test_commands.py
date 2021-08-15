import os
import shutil
import subprocess
import tarfile
from io import BytesIO
from io import StringIO
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import create_new_package
from .utils import remove_ansi
from .utils import remove_build_directory
from .utils import run_mys_command


class Test(TestCase):

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
        self.assert_files_equal(f'tests/build/{package_name}/doc/index.rst',
                                'tests/files/foo/doc/index.rst')

        with Path(f'tests/build/{package_name}'):
            # Run.
            self.assertFalse(os.path.exists('./build/default/app'))

            with patch('sys.argv', ['mys', 'run', '-j', '1']):
                mys.cli.main()

            self.assert_file_exists(
                f'build/speed/cpp/src/{package_name}/main.mys.cpp')
            self.assert_file_exists('build/speed/app')

            # Clean.
            self.assert_file_exists('build')

            with patch('sys.argv', ['mys', '-d', 'clean']):
                mys.cli.main()

            self.assert_file_not_exists('build')

            with patch('sys.argv', ['mys', '-d', 'clean']):
                mys.cli.main()

            # Build.
            with patch('sys.argv', ['mys', '-d', 'build', '-j', '1']):
                mys.cli.main()

            self.assert_file_exists('./build/speed/app')

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
                        call(['make', '-f', 'build/speed/Makefile', 'all',
                              '-s', 'APPLICATION=yes'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             encoding='utf-8',
                             close_fds=False,
                             env=None),
                        call(['./build/speed/app'], check=True)
                    ],
                    [
                        call(['make', '-f', 'build/speed/Makefile', 'all',
                              '-j', '1', '-s', 'APPLICATION=yes'],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             encoding='utf-8',
                             close_fds=False,
                             env=None),
                        call(['./build/speed/app'], check=True)
                    ]
                ])

            # Test.
            with patch('sys.argv', ['mys', '-d', 'test', '-j', '1']):
                mys.cli.main()

            self.assert_file_exists('./build/debug/test')

            # Doc without logo.
            with patch('sys.argv', ['mys', '-d', 'doc']):
                mys.cli.main()

            self.assert_file_exists('./build/doc/html/index.html')
            self.assert_file_not_exists('./build/doc/html/_static/logo.png')

            # Doc with logo.
            os.makedirs('doc/images')

            with open('doc/images/logo.png', 'w'):
                pass

            with patch('sys.argv', ['mys', 'doc']):
                mys.cli.main()

            self.assert_file_exists('./build/doc/html/index.html')
            self.assert_file_exists('./build/doc/html/_static/logo.png')

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
            os.makedirs('assets')

            with open('assets/foo.txt', 'w'):
                pass

            def post_mock(url, params, data):
                del params
                self.assertEqual(
                    url,
                    'https://mys-lang.org/package/test_publish-0.1.0.tar.gz')

                with tarfile.open(fileobj=BytesIO(data), mode='r:gz') as fin:
                    names = fin.getnames()

                self.assertEqual(names,
                                 [
                                     'test_publish-0.1.0',
                                     'test_publish-0.1.0/README.rst',
                                     'test_publish-0.1.0/assets',
                                     'test_publish-0.1.0/assets/foo.txt',
                                     'test_publish-0.1.0/doc',
                                     'test_publish-0.1.0/doc/index.rst',
                                     'test_publish-0.1.0/package.toml',
                                     'test_publish-0.1.0/src',
                                     'test_publish-0.1.0/src/lib.mys',
                                     'test_publish-0.1.0/src/main.mys'
                                 ])

                return Mock(status_code=200, text=None)

            with patch('sys.argv', ['mys', '-d', 'publish']):
                with patch('requests.post', post_mock):
                    mys.cli.main()

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
            self.assertTrue(os.path.exists('../bin/foo-assets/foo/foo.json'))
            self.assertTrue(os.path.exists('../bin/foo-assets/bar/bar.txt'))

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

    def test_error_if_package_name_is_not_snake_case(self):
        name = 'test_error_if_package_name_is_not_snake_case'
        remove_build_directory(name)
        shutil.copytree('tests/files/error_if_package_name_is_not_snake_case',
                        f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            with self.assertRaises(SystemExit) as cm:
                with patch('sys.argv', ['mys', 'build']):
                    mys.cli.main()

        self.assertEqual(str(cm.exception),
                         "package name must be snake case, got 'a-hypen'")

    def test_error_if_package_version_is_not_semantic(self):
        name = 'test_error_if_package_version_is_not_semantic'
        remove_build_directory(name)
        shutil.copytree('tests/files/error_if_package_version_is_not_semantic',
                        f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            with self.assertRaises(SystemExit) as cm:
                with patch('sys.argv', ['mys', 'build']):
                    mys.cli.main()

        self.assertEqual(str(cm.exception),
                         "package version must be a semantic version, got '1.0'")

    def test_package_with_local_and_registry_dependencies(self):
        name = 'test_package_with_local_and_registry_dependencies'
        remove_build_directory(name)
        shutil.copytree('tests/files/package_with_local_and_registry_dependencies',
                        f'tests/build/{name}')

        with Path(f'tests/build/{name}/top'):
            # Default.
            stdout = StringIO()

            with patch('sys.stdout', stdout):
                with patch('sys.argv', ['mys', 'dependencies']):
                    mys.cli.main()

            self.assert_in('dep1 = { path = "../dep1" }\n'
                           'hello_world = "latest"\n'
                           'dep2 = { path = "../dep2" }\n',
                           stdout.getvalue())

            # Versions.
            stdout = StringIO()

            with patch('sys.stdout', stdout):
                with patch('sys.argv', ['mys', 'dependencies', '--versions']):
                    mys.cli.main()

            self.assert_in('dep1 = "1.1.0"\n'
                           'hello_world = "0.4.0"\n'
                           'dep2 = "0.1.0-rc10"\n',
                           stdout.getvalue())
