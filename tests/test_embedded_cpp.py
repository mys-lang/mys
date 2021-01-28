import shutil
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import remove_build_directory
from .utils import transpile_source


class Test(TestCase):

    def test_embedded_cpp(self):
        name = 'test_embedded_cpp'
        remove_build_directory(name)
        shutil.copytree('tests/files/embedded_cpp', f'tests/build/{name}')

        with Path(f'tests/build/{name}/mypkg'):
            with patch('sys.argv', ['mys', '-d', 'test', '-v']):
                mys.cli.main()

    def test_mix_bytes_with_embedded_c_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(c"a" b"b")\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            '    print(c"a" b"b")\n'
            "                   ^\n"
            'SyntaxError: cannot mix bytes and nonbytes literals\n')

    def test_mix_bytes_with_embedded_c_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(b"a" c"b")\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            '    print(b"a" c"b")\n'
            "                   ^\n"
            'SyntaxError: cannot mix bytes and nonbytes literals\n')

    def test_mix_string_with_embedded_c_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(c"a" "b")\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            '    print(c"a" "b")\n'
            "                  ^\n"
            'SyntaxError: cannot mix embedded c and bytes, regexp or unicode '
            'literals\n')

    def test_mix_string_with_embedded_c_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print("a" c"b")\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            '    print("a" c"b")\n'
            "                  ^\n"
            'SyntaxError: cannot mix embedded c and bytes, regexp or unicode '
            'literals\n')
