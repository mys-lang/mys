import glob
import os
import shutil
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import remove_ansi
from .utils import remove_build_directory
from .utils import transpile_source


class Test(TestCase):

    def test_style(self):
        name = 'test_style'
        remove_build_directory(name)

        shutil.copytree('tests/files/style', f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            mod_mtime = os.stat('src/mod.mys').st_mtime

            # Ensure that there are trailing whitespaces in the file.
            with open('src/trailing_whitespaces.mys', 'r') as fin:
                source = fin.read()

            self.assertEqual(source.count(' \n'), len(source.split('\n')) - 1)

            with patch('sys.argv', ['mys', '-d', 'style']):
                mys.cli.main()

            # Files that are already styled should not be written to.
            self.assertEqual(os.stat('src/mod.mys').st_mtime, mod_mtime)

            for path in glob.glob('src/**/*.mys', recursive=True):
                self.assert_files_equal(path, f'../../files/style/styled-{path}')

    def test_tabs_not_allowed_as_indentation(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "\tpass\n")

        self.assertEqual(
            remove_ansi(str(cm.exception).replace('\t', '')),
            '  File "<string>", line 2\n'
            '    pass\n'
            '    ^\n'
            'SyntaxError: indentations must be spaces, not tabs\n')

    def test_indent_2_spaces(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "  pass\n")

        self.assertEqual(
            remove_ansi(str(cm.exception).replace('\t', '')),
            '  File "<string>", line 2\n'
            '    pass\n'
            '    ^\n'
            'SyntaxError: indentations must be 4 spaces\n')

    def test_indent_2_spaces_in_if(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "    if True:\n"
                             "      pass\n")

        self.assertEqual(
            remove_ansi(str(cm.exception).replace('\t', '')),
            '  File "<string>", line 3\n'
            '    pass\n'
            '    ^\n'
            'SyntaxError: indentations must be 4 spaces\n')
