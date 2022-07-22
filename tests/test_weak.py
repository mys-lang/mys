import subprocess
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import build_and_test_module
from .utils import create_new_package_with_files


class Test(TestCase):

    def run_test_panic(self, name, expected_output):
        proc = subprocess.run(['./build/debug/test', name],
                              capture_output=True,
                              text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assert_in(expected_output, proc.stderr)

    def test_weak(self):
        build_and_test_module('weak')

    def test_weak_panic(self):
        module_name = 'weak_panic'
        package_name = f'test_{module_name}'
        create_new_package_with_files(package_name, module_name)

        with Path('tests/build/' + package_name):
            with patch('sys.argv', ['mys', '--debug', 'test', '--no-run']):
                mys.cli.main()

            self.run_test_panic('is_none', 'Object is None.')
            self.run_test_panic('no_object',
                                'Cannot lock weak pointer with no object.')

    def test_weak_integer_type(self):
        self.assert_transpile_raises(
            'class Foo:\n'
            '    a: weak[i64]\n',
            '  File "", line 2\n'
            '        a: weak[i64]\n'
            '           ^\n'
            "CompileError: builtin type 'i64' cannot be weak\n")

    def test_weak_string_type(self):
        self.assert_transpile_raises(
            'class Foo:\n'
            '    a: weak[string]\n',
            '  File "", line 2\n'
            '        a: weak[string]\n'
            '           ^\n'
            "CompileError: builtin type 'string' cannot be weak\n")

    def test_weak_enum_type(self):
        self.assert_transpile_raises(
            'enum En:\n'
            '    A\n'
            'class Foo:\n'
            '    a: weak[En]\n',
            '  File "", line 4\n'
            '        a: weak[En]\n'
            '           ^\n'
            "CompileError: enum 'foo.lib.En' cannot be weak\n")
