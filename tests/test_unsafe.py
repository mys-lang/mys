import os
import shutil
import subprocess
from unittest.mock import patch

import mys.cli

from .utils import Path
from .utils import TestCase
from .utils import create_new_package
from .utils import remove_build_directory
from .utils import run_mys_command


class Test(TestCase):

    def run_safe_test_none(self, name):
        proc = subprocess.run(['./build/debug/test', name],
                              capture_output=True,
                              text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assert_in('Object is None.', proc.stderr)

    def run_unsafe_test_none(self, name):
        proc = subprocess.run(['./build/debug-unsafe/test', name],
                              capture_output=True,
                              text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assert_not_in('Object is None.', proc.stderr)

    def run_safe_test_index(self, name, message):
        proc = subprocess.run(['./build/debug/test', name],
                              capture_output=True,
                              text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assert_in(message, proc.stderr)

    def run_unsafe_test_index(self, name, message):
        proc = subprocess.run(['./build/debug-unsafe/test', name],
                              capture_output=True,
                              text=True)

        # The index tests in unsafe builds may or may not crash...
        if proc.returncode != 0:
            self.assert_not_in(message, proc.stderr)

    def test_safe(self):
        name = 'test_safe'
        remove_build_directory(name)

        shutil.copytree('tests/files/unsafe', f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            try:
                with patch('sys.argv', ['mys', 'test']):
                    mys.cli.main()
            except SystemExit:
                pass

            self.run_safe_test_none('class_none_1')
            self.run_safe_test_none('class_none_2')
            self.run_safe_test_none('compare_lists_3')
            self.run_safe_test_none('add_lists')
            self.run_safe_test_none('list_acces_none')
            self.run_safe_test_none('list_len_of_none')
            self.run_safe_test_none('compare_tuples_3')
            self.run_safe_test_none('tuple_acces_none')
            self.run_safe_test_none('tuple_unpack_in_for_loop_none_element')
            self.run_safe_test_none('string_none')
            self.run_safe_test_none('string_len_of_none')
            self.run_safe_test_none('compare_dicts_3')
            self.run_safe_test_none('dict_acces_none')
            self.run_safe_test_none('dict_len_of_none')
            self.run_safe_test_none('set_none')
            self.run_safe_test_index('bytes_index',
                                     'Bytes index -99997 is out of range.')
            self.run_safe_test_index('list_pop_index',
                                     'Pop index 1000 is out of range.')
            self.run_safe_test_index('negative_list_index',
                                     'List index -99996 is out of range.')
            self.run_safe_test_index('string_get_char_at_index',
                                     'String index -99994 is out of range.')

    def test_unsafe(self):
        name = 'test_unsafe'
        remove_build_directory(name)

        shutil.copytree('tests/files/unsafe', f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            try:
                with patch('sys.argv', ['mys', 'test', '--unsafe']):
                    mys.cli.main()
            except SystemExit:
                pass

            self.run_unsafe_test_none('class_none_1')
            self.run_unsafe_test_none('compare_lists_3')
            self.run_unsafe_test_none('add_lists')
            self.run_unsafe_test_none('list_acces_none')
            self.run_unsafe_test_none('list_len_of_none')
            self.run_unsafe_test_none('compare_tuples_3')
            self.run_unsafe_test_none('tuple_acces_none')
            self.run_unsafe_test_none('tuple_unpack_in_for_loop_none_element')
            self.run_unsafe_test_none('string_none')
            self.run_unsafe_test_none('string_len_of_none')
            self.run_unsafe_test_none('compare_dicts_3')
            self.run_unsafe_test_none('dict_acces_none')
            self.run_unsafe_test_none('dict_len_of_none')
            self.run_unsafe_test_none('set_none')
            self.run_unsafe_test_index('bytes_index', 'bytes index out of range')
            self.run_unsafe_test_index('list_pop_index',
                                       'pop index out of range')
            self.run_unsafe_test_index('negative_list_index',
                                       'list index out of range')
            self.run_unsafe_test_index('string_get_char_at_index',
                                       'string index out of range')

    def test_unsafe_build_run_test(self):
        package_name = 'test_unsafe_build_run_test'
        remove_build_directory(package_name)
        create_new_package(package_name)
        path = os.getcwd()

        with Path(f'tests/build/{package_name}'):
            run_mys_command(['build', '--unsafe'], path)
            run_mys_command(['run', '--unsafe'], path)
            run_mys_command(['test', '--unsafe'], path)
