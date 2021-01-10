import difflib
import os
import re
import shutil
import subprocess
import sys
import unittest
from unittest.mock import patch

import mys.cli
from mys.transpiler import Source
from mys.transpiler import TranspilerError
from mys.transpiler import transpile


class TestCase(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        os.makedirs('tests/build', exist_ok=True)

    def assert_in(self, needle, haystack):
        try:
            self.assertIn(needle, haystack)
        except AssertionError:
            differ = difflib.Differ()
            diff = differ.compare(needle.splitlines(), haystack.splitlines())

            raise AssertionError(
                '\n' + '\n'.join([diffline.rstrip('\n') for diffline in diff]))

    def assert_exception_string(self, cm, expected):
        self.assertEqual(expected, remove_ansi(str(cm.exception)))

    def assert_transpile_raises(self, source, error):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source(source)

        self.assert_exception_string(cm, error)


def read_file(filename):
    with open(filename, 'r') as fin:
        return fin.read()


def remove_directory(name):
    if os.path.exists(name):
        shutil.rmtree(name)


def remove_ansi(string):
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')

    return ansi_escape.sub('', string)


def remove_build_directory(name):
    remove_directory('tests/build/' + name)


def create_new_package(package_name):
    with Path('tests/build'):
        remove_directory(package_name)

        command = [
            'mys', '-d', 'new',
            '--author', 'Test Er <test.er@mys.com>',
            package_name
        ]

        with patch('sys.argv', command):
            mys.cli.main()


def create_new_package_with_files(package_name, module_name, src_module_name=None):
    if src_module_name is None:
        src_module_name = module_name

    create_new_package(package_name)

    with Path('tests/build'):
        os.remove(f'{package_name}/src/lib.mys')
        os.remove(f'{package_name}/src/main.mys')
        shutil.copyfile(f'../../tests/files/{module_name}.mys',
                        f'{package_name}/src/{src_module_name}.mys')


def test_package(package_name):
    with Path('tests/build/' + package_name):
        with patch('sys.argv', ['mys', '--debug', 'test', '--verbose']):
            mys.cli.main()


def build_and_test_module(module_name):
    package_name = f'test_{module_name}'
    create_new_package_with_files(package_name, module_name)
    test_package(package_name)


class Path:

    def __init__(self, new_dir):
        self.new_dir = new_dir
        self.old_dir = None

    def __enter__(self):
        self.old_dir = os.getcwd()
        os.chdir(self.new_dir)

        return self

    def __exit__(self, *args, **kwargs):
        os.chdir(self.old_dir)

        return False


def run_mys_command(command, path):
    env = os.environ
    env['PYTHONPATH'] = path
    proc = subprocess.run([sys.executable, '-m', 'mys'] + command,
                          capture_output=True,
                          text=True,
                          close_fds=False,
                          env=env)

    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)

        raise Exception("Build error.")

    return proc.stdout, proc.stderr


def transpile_early_header(source, mys_path='', module_hpp=''):
    return transpile([Source(source,
                             mys_path=mys_path,
                             module_hpp=module_hpp)])[0][0]


def transpile_header(source, mys_path='', module_hpp=''):
    return transpile([Source(source,
                             mys_path=mys_path,
                             module_hpp=module_hpp)])[0][1]


def transpile_source(source,
                     mys_path='',
                     module='foo.lib',
                     module_hpp='foo/lib.mys.hpp',
                     has_main=False):
    return transpile([Source(source,
                             mys_path=mys_path,
                             module=module,
                             module_hpp=module_hpp,
                             has_main=has_main)])[0][2]
