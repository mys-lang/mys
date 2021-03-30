import shutil
import subprocess
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import remove_build_directory


class Test(TestCase):

    def run_test_assert(self, name, expected):
        proc = subprocess.run(['./build/debug/test', name],
                              capture_output=True,
                              text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assert_in(expected, proc.stderr + proc.stdout)

    def run_app_assert(self, expected, path, not_expected=None):
        proc = subprocess.run([f'./build/{path}/app'],
                              capture_output=True,
                              text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assert_in(expected, proc.stderr)

        if not_expected is not None:
            self.assert_not_in(not_expected, proc.stderr + proc.stdout)

    def test_traceback(self):
        name = 'test_traceback'
        remove_build_directory(name)

        shutil.copytree('tests/files/traceback', f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            try:
                with patch('sys.argv', ['mys', 'test', '-v']):
                    mys.cli.main()
            except SystemExit:
                pass

            self.run_test_assert(
                'test_panic',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 5 in test_panic\n'
                '    print(""[1])\n'
                '\n'
                'Panic(message="String index 1 is out of range.")\n')

            self.run_test_assert(
                'test_panic_2',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 13 in test_panic_2\n'
                '    panic_2()\n'
                '  File: "./src/lib.mys", line 9 in panic_2\n'
                '    print(""[i])\n'
                '\n'
                'Panic(message="String index 10 is out of range.")\n')

            self.run_test_assert(
                'test_panic_in_except',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 23 in test_panic_in_except\n'
                '    print(b""[11])\n'
                '\n'
                'Panic(message="Bytes index 11 is out of range.")\n')

            self.run_test_assert(
                'test_panic_in_if',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 28 in test_panic_in_if\n'
                '    print(b""[5])\n'
                '\n'
                'Panic(message="Bytes index 5 is out of range.")\n')

            self.run_test_assert(
                'test_panic_in_else',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 35 in test_panic_in_else\n'
                '    print(b""[6])\n'
                '\n'
                'Panic(message="Bytes index 6 is out of range.")\n')

            self.run_test_assert(
                'test_panic_in_for',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 40 in test_panic_in_for\n'
                '    print(b"123"[i])\n'
                '\n'
                'Panic(message="Bytes index 3 is out of range.")\n')

            self.run_test_assert(
                'test_panic_in_while',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 45 in test_panic_in_while\n'
                '    print(b""[10])\n'
                '\n'
                'Panic(message="Bytes index 10 is out of range.")\n')

            self.run_test_assert(
                'test_panic_in_match',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 51 in test_panic_in_match\n'
                '    print(b""[-1])\n'
                '\n'
                'Panic(message="Bytes index -1 is out of range.")\n')

            self.run_test_assert(
                'test_error_in_runtime',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 59 in test_error_in_runtime\n'
                '    raise MyError(1, 2)\n'
                '\n'
                'MyError(x=1, y=2)\n')

            self.run_test_assert(
                'test_error_in_fiber',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 64 in run\n'
                '    raise MyError(2, 3)\n'
                '\n'
                'MyError(x=2, y=3)\n')

            self.run_test_assert(
                'test_modulo_zero',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 78 in test_modulo_zero\n'
                '    assert modulo(10, 0) == 0\n'
                '  File: "./src/lib.mys", line 73 in modulo\n'
                '    return a % b\n'
                '\n'
                'ValueError(message="cannot divide or modulo by zero")\n')

            self.run_test_assert(
                'test_division_by_zero',
                'Traceback (most recent call last):\n'
                '  File: "./src/lib.mys", line 86 in test_division_by_zero\n'
                '    assert divide(10, 0) == 5\n'
                '  File: "./src/lib.mys", line 81 in divide\n'
                '    return a / b\n'
                '\n'
                'ValueError(message="cannot divide or modulo by zero")\n')

            # Debug build.
            with patch('sys.argv', ['mys', 'build', '-o', 'debug']):
                mys.cli.main()

            self.run_app_assert(
                'Traceback (most recent call last):\n'
                '  File: "./src/main.mys", line 5 in main\n'
                '    raise AnError("hi")\n'
                '\n'
                'AnError(message="hi")\n',
                'debug')

            with patch('sys.argv', ['mys', 'clean']):
                mys.cli.main()

            # Speed build, no tracebacks.
            with patch('sys.argv', ['mys', 'build']):
                mys.cli.main()

            self.run_app_assert('AnError(message="hi")\n',
                                'speed',
                                'Traceback (most recent call last):\n'
                                '  File: "./src/main.mys", line 5 in main\n'
                                '    raise AnError("hi")\n')
