import shutil
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import remove_build_directory


class Test(TestCase):

    def test_package_and_module_with_same_name(self):
        name = 'test_package_and_module_with_same_name'
        remove_build_directory(name)
        shutil.copytree('tests/files/package_and_module_with_same_name',
                        f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            with patch('sys.argv', ['mys', '-d', 'test', '-v']):
                mys.cli.main()
