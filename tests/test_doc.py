import re
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

            with open('index.txt', 'w') as fout:
                mo = re.search(
                    r'(The doc package in the Mys programming language.*)© Copyright',
                    html_text.text,
                    re.DOTALL)
                fout.write(mo.group(1).strip())

            self.assert_files_equal('index.txt', '../../files/doc/index.txt')
