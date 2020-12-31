import shutil
import sys
import subprocess
import os
import difflib
from unittest.mock import patch

import mys.cli

from .utils import remove_build_directory
from .utils import remove_ansi
from .utils import create_new_package_with_files
from .utils import build_and_test_module
from .utils import Path
from .utils import TestCase

class Test(TestCase):

    def setUp(self):
        os.makedirs('tests/build', exist_ok=True)

    def test_calc(self):
        build_and_test_module('calc')

    def test_enums(self):
        build_and_test_module('enums')

    def test_hello_world(self):
        build_and_test_module('hello_world')

    def test_loops(self):
        build_and_test_module('loops')

    def test_various_1(self):
        build_and_test_module('various_1')

    def test_various_2(self):
        build_and_test_module('various_2')

    def test_various_3(self):
        build_and_test_module('various_3')

    def test_special_symbols(self):
        build_and_test_module('special_symbols')

    def test_imports(self):
        remove_build_directory('imports')
        shutil.copytree('tests/files/imports', 'tests/build/imports')

        with Path('tests/build/imports/mypkg'):
            with patch('sys.argv', ['mys', 'test', '-v']):
                mys.cli.main()

    def test_print(self):
        module_name = 'print'
        package_name = f'test_{module_name}'
        create_new_package_with_files(package_name, module_name, 'main')
        path = os.getcwd()

        with Path('tests/build/' + package_name):
            env = os.environ
            env['PYTHONPATH'] = path
            proc = subprocess.run([sys.executable, '-m', 'mys', 'run'],
                                  input="Lobster #1\n10\n",
                                  capture_output=True,
                                  text=True,
                                  env=env)

            if proc.returncode != 0:
                print(proc.stdout)
                print(proc.stderr)

                raise Exception("Build error.")

            output = remove_ansi(proc.stdout)

            self.assert_in(
                'A string literal!\n'
                '1\n'
                '1.5\n'
                'False\n'
                'True\n'
                'Foo(v=5)\n'
                '(-500, "Hi!")\n'
                '[1, 2, 3]\n'
                'Bar(a=Foo(v=3), b=True, c="kalle")\n'
                'Foo(v=5)\n'
                '[(Foo(v=3), True), (Foo(v=5), False)]\n'
                'True\n'
                'False\n'
                'True\n'
                'None\n'
                'Fie(a=5, _b=False, _c=None)\n'
                'G\n'
                '7\n'
                "['j', 'u', 'l']\n"
                'Fam(x=None)\n'
                'Fam(x=Foo(v=4))\n'
                'Fam(x=Bar(a=None, b=False, c="kk"))\n'
                'Foo(v=-1)\n'
                'Bar(a=None, b=True, c="")\n'
                '[Foo(v=5), Bar(a=None, b=True, c="fes")]\n'
                'b""\n'
                'b"\\x01\\x02\\x03"!\n'
                '20\n'
                '1\n' # Todo: Should print "Animal.Cow".
                'Name: Lobster #1\n'
                'Age: 10\n',
                output)
            self.assertTrue(('{1: 2, 3: 4}\n' in output)
                            or ('{3: 4, 1: 2}\n' in output))
            self.assertTrue(('{ho: Foo(v=4), hi: Foo(v=5)}\n' in output)
                            or ('{"hi": Foo(v=5), "ho": Foo(v=4)}\n' in output))
