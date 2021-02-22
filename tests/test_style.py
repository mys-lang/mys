# import os
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
            # ToDo: Uncomment.
            # mod_mtime = os.stat('src/mod.mys').st_mtime

            with patch('sys.argv', ['mys', '-d', 'style']):
                mys.cli.main()

            self.assert_files_equal('src/lib.mys',
                                    '../../files/style/styled-src/lib.mys')

            # Files that are already styled should not be written to.

            # ToDo: Uncomment.
            # self.assertEqual(os.stat('src/mod.mys').st_mtime, mod_mtime)
            self.assert_files_equal('src/mod.mys',
                                    '../../files/style/styled-src/mod.mys')

            self.assert_files_equal('src/f/mod.mys',
                                    '../../files/style/styled-src/f/mod.mys')


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
