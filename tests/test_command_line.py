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
    
    def test_new(self):
        package_name = 'foo'
        argv = ['mys', 'new', package_name]

        remove_directory(package_name)

        with patch('sys.argv', argv):
            mys.main()

        self.assert_files_equal(f'{package_name}/Package.toml',
                                'tests/files/foo/Package.toml')
        self.assert_files_equal(f'{package_name}/src/main.mys',
                                'tests/files/foo/src/main.mys')
