import shutil
import signal
from unittest.mock import patch

import pexpect

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import remove_build_directory


class Test(TestCase):

    def test_sigint(self):
        name = 'test_signals_sigint'
        remove_build_directory(name)

        shutil.copytree('tests/files/signals', f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            try:
                with patch('sys.argv', ['mys', 'test', 'no-test']):
                    mys.cli.main()
            except SystemExit:
                pass

            test = pexpect.spawn('./build/debug/test test_sigint',
                                 encoding='utf-8',
                                 codec_errors='replace')
            test.expect('test_sigint started')
            test.kill(signal.SIGINT)
            # ToDo: How to fix this?
            # test.expect('InterruptError()')
            test.wait()
            # ToDo: How to fix this?
            # self.assertEqual(test.exitstatus, 0)
