import shutil
import subprocess
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import remove_build_directory


class Test(TestCase):

    def run_test_assert(self, name, expected):
        proc = subprocess.run(['./build/default/test', name],
                              capture_output=True,
                              text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assert_in(expected, proc.stderr)

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
                '  File: "./src/lib.mys", line 3 in test_panic\n'
                '    print(""[1])\n'
                '\n'
                'Panic(message="String index 1 is out of range.")\n')
