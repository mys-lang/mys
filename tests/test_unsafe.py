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
        proc = subprocess.run(['./build/default/test', name],
                              capture_output=True,
                              text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assert_in('object is None', proc.stderr)

    def run_unsafe_test_none(self, name):
        proc = subprocess.run(['./build/default/test', name],
                              capture_output=True,
                              text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assert_not_in('object is None', proc.stderr)

    def run_safe_test_index(self, name, message):
        proc = subprocess.run(['./build/default/test', name],
                              capture_output=True,
                              text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assert_in(message, proc.stderr)

    def run_unsafe_test_index(self, name, message):
        proc = subprocess.run(['./build/default/test', name],
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
                with patch('sys.argv', ['mys', 'test', '-v']):
                    mys.cli.main()
            except SystemExit:
                pass

            self.run_safe_test_none('test_class_none_1')
            self.run_safe_test_none('test_class_none_2')
            self.run_safe_test_none('test_compare_lists_3')
            self.run_safe_test_none('test_add_lists')
            self.run_safe_test_none('test_list_acces_none')
            self.run_safe_test_none('test_list_len_of_none')
            self.run_safe_test_none('test_compare_tuples_3')
            self.run_safe_test_none('test_tuple_acces_none')
            self.run_safe_test_none('test_tuple_unpack_in_for_loop_none_element')
            self.run_safe_test_none('test_string_none')
            self.run_safe_test_none('test_string_len_of_none')
            self.run_safe_test_none('test_compare_dicts_3')
            self.run_safe_test_none('test_dict_acces_none')
            self.run_safe_test_none('test_dict_len_of_none')
            self.run_safe_test_none('test_set_none')
            self.run_safe_test_index('test_bytes_index', 'bytes index out of range')
            self.run_safe_test_index('test_list_pop_index', 'pop index out of range')
            self.run_safe_test_index('test_negative_list_index',
                                     'list index out of range')
            self.run_safe_test_index('test_string_get_char_at_index',
                                     'string index out of range')

    def test_unsafe(self):
        name = 'test_unsafe'
        remove_build_directory(name)

        shutil.copytree('tests/files/unsafe', f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            try:
                with patch('sys.argv', ['mys', 'test', '-v', '--unsafe']):
                    mys.cli.main()
            except SystemExit:
                pass

            self.run_unsafe_test_none('test_class_none_1')
            self.run_unsafe_test_none('test_compare_lists_3')
            self.run_unsafe_test_none('test_add_lists')
            self.run_unsafe_test_none('test_list_acces_none')
            self.run_unsafe_test_none('test_list_len_of_none')
            self.run_unsafe_test_none('test_compare_tuples_3')
            self.run_unsafe_test_none('test_tuple_acces_none')
            self.run_unsafe_test_none('test_tuple_unpack_in_for_loop_none_element')
            self.run_unsafe_test_none('test_string_none')
            self.run_unsafe_test_none('test_string_len_of_none')
            self.run_unsafe_test_none('test_compare_dicts_3')
            self.run_unsafe_test_none('test_dict_acces_none')
            self.run_unsafe_test_none('test_dict_len_of_none')
            self.run_unsafe_test_none('test_set_none')
            self.run_unsafe_test_index('test_bytes_index', 'bytes index out of range')
            self.run_unsafe_test_index('test_list_pop_index',
                                       'pop index out of range')
            self.run_unsafe_test_index('test_negative_list_index',
                                       'list index out of range')
            self.run_unsafe_test_index('test_string_get_char_at_index',
                                       'string index out of range')

    def test_unsafe_build_run_test(self):
        package_name = 'test_unsafe_build_run_test'
        remove_build_directory(package_name)
        create_new_package(package_name)
        path = os.getcwd()

        with Path(f'tests/build/{package_name}'):
            run_mys_command(['build', '-v', '--unsafe'], path)
            run_mys_command(['run', '-v', '--unsafe'], path)
            run_mys_command(['test', '-v', '--unsafe'], path)
