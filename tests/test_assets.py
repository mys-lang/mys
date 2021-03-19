import shutil
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import remove_build_directory


class Test(TestCase):

    def test_assets(self):
        name = 'test_assets'
        remove_build_directory(name)
        shutil.copytree('tests/files/assets', f'tests/build/{name}')

        with Path(f'tests/build/{name}/mypkg'):
            with patch('sys.argv', ['mys', '-d', 'test', '-v']):
                mys.cli.main()

        self.assert_files_equal(
            f'tests/build/{name}/mypkg/build/debug/test-assets/mypkg/foo.txt',
            'tests/files/assets/mypkg/assets/foo.txt')
        self.assert_files_equal(
            f'tests/build/{name}/mypkg/build/debug/test-assets/mypkg/bar/bar.txt',
            'tests/files/assets/mypkg/assets/bar/bar.txt')
        self.assert_files_equal(
            f'tests/build/{name}/mypkg/build/debug/test-assets/mypkg1/foo.txt',
            'tests/files/assets/mypkg1/assets/foo.txt')
