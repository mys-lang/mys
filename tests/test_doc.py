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

            self.assert_in_file('class Foo', 'build/doc/html/lib.html')
            self.assert_in_file('def foo()', 'build/doc/html/lib.html')

            self.assert_in_file('def add(first: i32, second: i32) -&gt; i32',
                                'build/doc/html/lib.html')

            self.assert_in_file('def sub(first: i32, second: i32) -&gt; i32',
                                'build/doc/html/lib.html')

            self.assert_not_in_file('def test_add', 'build/doc/html/lib.html')
