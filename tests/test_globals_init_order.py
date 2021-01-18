import shutil
from unittest.mock import patch

import mys.cli
from mys.transpiler import Source
from mys.transpiler import TranspilerError
from mys.transpiler import transpile

from .utils import Path
from .utils import TestCase
from .utils import remove_build_directory
from .utils import transpile_source


class Test(TestCase):

    pass

    # ToDo
    # def test_globals_init_order(self):
    #     name = 'test_globals_init_order'
    #     remove_build_directory(name)
    #     shutil.copytree('tests/files/globals_init_order', f'tests/build/{name}')
    #
    #     with Path(f'tests/build/{name}/mypkg'):
    #         with patch('sys.argv', ['mys', '-d', 'test', '-v']):
    #             mys.cli.main()
