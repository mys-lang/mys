import shutil
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import remove_build_directory


class Test(TestCase):

    def test_doc(self):
        name = 'test_doc'
        remove_build_directory(name)

        shutil.copytree('tests/files/doc', f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            with patch('sys.argv', ['mys', '-d', 'doc', '-v']):
                mys.cli.main()

            self.assert_file_exists('build/doc/html/index.html')
            self.assert_in_file('Foo', 'build/doc/html/index.html')
            self.assert_in_file('foo', 'build/doc/html/index.html')
            self.assert_in_file('add', 'build/doc/html/index.html')
            self.assert_in_file('sub', 'build/doc/html/index.html')
            self.assert_not_in_file('test_add', 'build/doc/html/index.html')
