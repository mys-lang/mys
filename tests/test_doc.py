import shutil
from html.parser import HTMLParser
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import read_file
from .utils import remove_build_directory


class HTMLText(HTMLParser):

    def __init__(self):
        super().__init__()
        self.text = ''

    def handle_data(self, data):
        self.text += data


class Test(TestCase):

    def test_doc(self):
        name = 'test_doc'
        remove_build_directory(name)

        shutil.copytree('tests/files/doc', f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            with patch('sys.argv', ['mys', '-d', 'doc', '-v']):
                mys.cli.main()

            self.assert_file_exists('build/doc/html/index.html')

            html_text = HTMLText()
            html_text.feed(read_file('build/doc/html/index.html'))
            text = html_text.text

            self.assert_in('class Foo:', text)
            self.assert_in('Ops.', text)
            self.assert_in('foo', text)
            self.assert_in('a_member', text)
            self.assert_not_in('_a_private_member', text)
            self.assert_in('def add(first: i32, second: i32) -> i32:', text)
            self.assert_in('def sub(first: i32, second: i32) -> i32:', text)
            self.assert_in('__mul__', text)
            self.assert_in('__idiv__', text)
            self.assert_in('Some base doc.', text)
            self.assert_in('This is foo!', text)
            self.assert_in('This is bar!', text)
            self.assert_in('Special div op', text)
            self.assert_in('__init__', text)
            self.assert_not_in('test_add', text)
            self.assert_in('a: i32 = 77777', text)
            self.assert_in(
                'b: [{string: (Foo, char)}] = [{"hi": (Foo(99999), \'5\')}, {}]',
                text)
