import os
import unittest
from unittest.mock import patch
from io import BytesIO

import mys

from .utils import read_file
from .utils import remove_directory


class Stdout:

    def __init__(self):
        self._data = BytesIO()

    @property
    def buffer(self):
        return self._data

    def flush(self):
        pass

    def getvalue(self):
        return self._data.getvalue()


class MysTest(unittest.TestCase):

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
        stdout = Stdout()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', ['mys', 'run']):
                mys.main()

        self.assertEqual(stdout.getvalue(), b'Hello, world!\n')

        # Clean.
        self.assertTrue(os.path.exists('build'))

        with patch('sys.argv', ['mys', 'clean']):
            mys.main()

        self.assertFalse(os.path.exists('build'))

        # Build.
        stdout = Stdout()

        with patch('sys.stdout', stdout):
            with patch('sys.argv', ['mys', 'build']):
                mys.main()

        self.assertEqual(stdout.getvalue(), b'')
        self.assertTrue(os.path.exists('build/app'))

        os.chdir(path)
