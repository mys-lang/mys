import os

from .utils import Path
from .utils import TestCase
from .utils import create_new_package
from .utils import remove_build_directory
from .utils import run_mys_command


class Test(TestCase):

    def test_unsafe(self):
        package_name = 'test_unsafe'
        remove_build_directory(package_name)
        create_new_package(package_name)
        path = os.getcwd()

        with Path(f'tests/build/{package_name}'):
            run_mys_command(['build', '-v', '--unsafe'], path)
            run_mys_command(['run', '-v', '--unsafe'], path)
            run_mys_command(['test', '-v', '--unsafe'], path)
