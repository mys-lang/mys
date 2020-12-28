import difflib
from mys.parser import ast
import sys
import unittest
from mys.transpile import transpile
from mys.transpile import Source
from mys.transpile.definitions import find_definitions

from .utils import read_file
from .utils import remove_ansi

def transpile_header(source, filename='', module_hpp=''):
    return transpile([Source(source,
                             filename=filename,
                             module_hpp=module_hpp)])[0][0]

def transpile_source(source, filename='', module_hpp='', has_main=False):
    return transpile([Source(source,
                             filename=filename,
                             module_hpp=module_hpp,
                             has_main=has_main)])[0][1]


class Test(unittest.TestCase):

    maxDiff = None

    def assert_in(self, needle, haystack):
        try:
            self.assertIn(needle, haystack)
        except AssertionError:
            differ = difflib.Differ()
            diff = differ.compare(needle.splitlines(), haystack.splitlines())

            raise AssertionError(
                '\n' + '\n'.join([diffline.rstrip('\n') for diffline in diff]))

    def test_if_string(self):
        source = transpile_source('def foo(v: string):\n'
                                  '    if v == "a":\n'
                                  '        print(v)\n'
                                  '    elif v == "b":\n'
                                  '        print(v)\n'
                                  '    elif "c" == v:\n'
                                  '        print(v)\n')

        self.assert_in('static String __constant_1 = String("a");', source)
        self.assert_in('static String __constant_2 = String("b");', source)
        self.assert_in('static String __constant_3 = String("c");', source)
        self.assert_in('if (Bool(v == __constant_1)) {', source)
        self.assert_in('if (Bool(v == __constant_2)) {', source)
        self.assert_in('if (Bool(__constant_3 == v)) {', source)

    # ToDo
    # def test_if_in_list(self):
    #     source = transpile_source('def foo(v: i32):\n'
    #                               '    if v in [1, 2]:\n'
    #                               '        print(v)\n')
    #
    #     self.assert_in(
    #         'static SharedList<i32> __constant_1 = std::make_shared',
    #         source)
    #     self.assert_in('if (Bool(v == __constant_1)) {', source)

    def test_match_string(self):
        source = transpile_source('def foo(v: string):\n'
                                  '    res = 0\n'
                                  '    match v:\n'
                                  '        case "123":\n'
                                  '            res = 1\n'
                                  '        case "hi":\n'
                                  '            res = 2\n'
                                  '    print(res)\n')

        self.assert_in('static String __constant_2 = String("123");', source)
        self.assert_in('static String __constant_3 = String("hi");', source)
        self.assert_in('if (__subject_1 == __constant_2) {', source)
        self.assert_in('if (__subject_1 == __constant_3) {', source)

    # ToDo: Test for more kinds of constants. Tuples, dicts, classes?
