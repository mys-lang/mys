import os
import unittest
from unittest.mock import patch

import mys

from .utils import read_file
from .utils import remove_directory


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
        with patch('sys.argv', ['mys', 'run']):
            mys.main()

        os.chdir(path)
