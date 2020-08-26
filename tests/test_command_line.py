import os
import unittest
from unittest.mock import patch
from unittest.mock import call
from unittest.mock import MagicMock

import mys

from .utils import read_file
from .utils import remove_directory


class MysTest(unittest.TestCase):

    maxDiff = None

    def assert_files_equal(self, actual, expected):
        # open(expected, 'w').write(open(actual, 'r').read())
        self.assertEqual(read_file(actual), read_file(expected))

    def test_foo_new_and_run(self):
        # New.
        package_name = 'foo'
        remove_directory(package_name)

        with patch('sys.argv', ['mys', 'new', package_name]):
            mys.main()

        self.assert_files_equal(f'{package_name}/Package.toml',
                                'tests/files/foo/Package.toml')
        self.assert_files_equal(f'{package_name}/src/main.mys',
                                'tests/files/foo/src/main.mys')

        # Enter the package directory.
        path = os.getcwd()
        os.chdir(package_name)

        # Run.
        self.assertFalse(os.path.exists('build/app'))

        with patch('sys.argv', ['mys', 'run']):
            mys.main()

        self.assertTrue(os.path.exists('build/app'))

        # Clean.
        self.assertTrue(os.path.exists('build'))

        with patch('sys.argv', ['mys', 'clean']):
            mys.main()

        self.assertFalse(os.path.exists('build'))

        # Build.
        with patch('sys.argv', ['mys', 'build']):
            mys.main()

        self.assertTrue(os.path.exists('build/app'))

        # Run again, but with run() mock to verify that the
        # application is run.
        run_mock = MagicMock()

        with patch('subprocess.run', run_mock):
            with patch('sys.argv', ['mys', 'run']):
                mys.main()

        self.assertEqual(run_mock.mock_calls,
                         [
                             call(['make', '-C', 'build', '-s'] , check=True),
                             call(['build/app'] , check=True)
                         ])

        os.chdir(path)
