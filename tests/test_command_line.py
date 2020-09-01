import sys
import subprocess
import os
import unittest
from unittest.mock import patch
from unittest.mock import call
from unittest.mock import Mock

import mys.cli

from .utils import read_file
from .utils import remove_directory
from .utils import remove_files

class MysTest(unittest.TestCase):

    maxDiff = None

    def assert_files_equal(self, actual, expected):
        # open(expected, 'w').write(open(actual, 'r').read())
        self.assertEqual(read_file(actual), read_file(expected))

    def test_foo_new_and_run(self):
        # New.
        package_name = 'foo'
        remove_directory(package_name)
        command = [
            'mys', 'new',
            '--author', 'Test Er <test.er@mys.com>',
            package_name
        ]

        with patch('sys.argv', command):
            mys.cli.main()

        self.assert_files_equal(f'{package_name}/Package.toml',
                                'tests/files/foo/Package.toml')
        self.assert_files_equal(f'{package_name}/src/main.mys',
                                'tests/files/foo/src/main.mys')

        # Enter the package directory.
        path = os.getcwd()
        os.chdir(package_name)

        # Run.
        self.assertFalse(os.path.exists('./build/app'))

        with patch('sys.argv', ['mys', 'run']):
            mys.cli.main()

        self.assertTrue(os.path.exists('./build/app'))

        # Clean.
        self.assertTrue(os.path.exists('build'))

        with patch('sys.argv', ['mys', 'clean']):
            mys.cli.main()

        self.assertFalse(os.path.exists('build'))

        # Build.
        with patch('sys.argv', ['mys', 'build']):
            mys.cli.main()

        self.assertTrue(os.path.exists('./build/app'))

        # Run again, but with run() mock to verify that the
        # application is run.
        run_result = Mock()
        run_mock = Mock(side_effect=run_result)

        with patch('subprocess.run', run_mock):
            with patch('sys.argv', ['mys', 'run']):
                mys.cli.main()

        self.assertEqual(
            run_mock.mock_calls,
            [
                call(['make', '-C', 'build', '-s'],
                     stdout=subprocess.PIPE,
                     stderr=subprocess.STDOUT,
                     encoding='utf-8',
                     env=None),
                call(['./build/app'], check=True)
            ])

        os.chdir(path)

    def test_new_author_from_git(self):
        package_name = 'foo'
        remove_directory(package_name)

        check_output_mock = Mock(side_effect=['First Last', 'first.last@test.org'])

        with patch('subprocess.check_output', check_output_mock):
            with patch('sys.argv', ['mys', 'new', package_name]):
                mys.cli.main()

        self.assertEqual(
            check_output_mock.mock_calls,
            [
                call(['git', 'config', '--get', 'user.name'], encoding='utf-8'),
                call(['git', 'config', '--get', 'user.email'], encoding='utf-8')
            ])

        expected_package_toml = '.test_new_author_from_git.toml'

        with open(expected_package_toml, 'w') as fout:
            fout.write('[package]\n'
                       'name = "foo"\n'
                       'version = "0.1.0"\n'
                       'authors = ["First Last <first.last@test.org>"]\n'
                       '\n'
                       '[dependencies]\n'
                       '# foobar = "*"\n')

        self.assert_files_equal(f'{package_name}/Package.toml',
                                expected_package_toml)

    def test_new_git_command_failure(self):
        package_name = 'foo'
        remove_directory(package_name)

        check_output_mock = Mock(side_effect=Exception())
        getuser_mock = Mock(side_effect=['mystester'])

        with patch('subprocess.check_output', check_output_mock):
            with patch('getpass.getuser', getuser_mock):
                with patch('sys.argv', ['mys', 'new', package_name]):
                    mys.cli.main()

        self.assertEqual(
            check_output_mock.mock_calls,
            [
                call(['git', 'config', '--get', 'user.name'], encoding='utf-8'),
                call(['git', 'config', '--get', 'user.email'], encoding='utf-8')
            ])

        expected_package_toml = '.test_new_git_command_failure.toml'

        with open(expected_package_toml, 'w') as fout:
            fout.write('[package]\n'
                       'name = "foo"\n'
                       'version = "0.1.0"\n'
                       'authors = ["mystester <mystester@example.com>"]\n'
                       '\n'
                       '[dependencies]\n'
                       '# foobar = "*"\n')

        self.assert_files_equal(f'{package_name}/Package.toml',
                                expected_package_toml)

    def test_new_multiple_authors(self):
        package_name = 'foo'
        remove_directory(package_name)
        command = [
            'mys', 'new',
            '--author', 'Test Er <test.er@mys.com>',
            '--author', 'Test2 Er2 <test2.er2@mys.com>',
            package_name
        ]

        with patch('sys.argv', command):
            mys.cli.main()

        expected_package_toml = '.test_new_multiple_authors.toml'

        with open(expected_package_toml, 'w') as fout:
            fout.write(
                '[package]\n'
                'name = "foo"\n'
                'version = "0.1.0"\n'
                'authors = ["Test Er <test.er@mys.com>", '
                '"Test2 Er2 <test2.er2@mys.com>"]\n'
                '\n'
                '[dependencies]\n'
                '# foobar = "*"\n')

        self.assert_files_equal(f'{package_name}/Package.toml',
                                expected_package_toml)

    def test_publish(self):
        # New.
        package_name = 'foo'
        remove_directory(package_name)
        command = [
            'mys', 'new',
            '--author', 'Test Er <test.er@mys.com>',
            package_name
        ]

        with patch('sys.argv', command):
            mys.cli.main()

        # Enter the package directory.
        path = os.getcwd()
        os.chdir(package_name)

        # Publish.
        run_sdist_result = Mock()
        run_twine_result = Mock()
        run_mock = Mock(side_effect=[run_sdist_result, run_twine_result])

        with patch('sys.argv', ['mys', 'publish', '-u', 'a', '-p', 'b']):
            with patch('subprocess.run', run_mock):
                mys.cli.main()

        if sys.version_info < (3, 8):
            return

        # sdist.
        call = run_mock.call_args_list[0]
        self.assertEqual(call.args[0][1:], ['setup.py', 'sdist'])
        self.assertEqual(call.kwargs,
                         {
                             'stdout': subprocess.PIPE,
                             'stderr': subprocess.STDOUT,
                             'encoding': 'utf-8',
                             'env': None
                         })

        # twine.
        call = run_mock.call_args_list[1]
        self.assertEqual(call.args[0][1:], ['-m', 'twine', 'upload'])
        self.assertEqual(call.kwargs['stdout'], subprocess.PIPE)
        self.assertEqual(call.kwargs['stderr'], subprocess.STDOUT)
        self.assertEqual(call.kwargs['encoding'], 'utf-8')
        self.assertEqual(call.kwargs['env']['TWINE_USERNAME'], 'a')
        self.assertEqual(call.kwargs['env']['TWINE_PASSWORD'], 'b')

        os.chdir(path)
