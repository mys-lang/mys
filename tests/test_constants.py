from mys.transpiler import Source
from mys.transpiler import transpile

from .utils import TestCase


def transpile_source(source, filename='', module_hpp='', has_main=False):
    return transpile([Source(source,
                             filename=filename,
                             module_hpp=module_hpp,
                             has_main=has_main)])[0][2]

class Test(TestCase):

    def test_if_string(self):
        source = transpile_source('def foo(v: string):\n'
                                  '    if v == "a":\n'
                                  '        print(v)\n'
                                  '    elif v == "b":\n'
                                  '        print(v)\n'
                                  '    elif "c" == v:\n'
                                  '        print(v)\n')

        self.assert_in('static const String __constant_1 = String("a");', source)
        self.assert_in('static const String __constant_2 = String("b");', source)
        self.assert_in('static const String __constant_3 = String("c");', source)
        self.assert_in('if (Bool(v == __constant_1)) {', source)
        self.assert_in('if (Bool(v == __constant_2)) {', source)
        self.assert_in('if (Bool(__constant_3 == v)) {', source)

    def test_if_in_list(self):
        source = transpile_source('def foo(v: i32):\n'
                                  '    if v in [1, 2]:\n'
                                  '        print(v)\n')

        self.assert_in(
            'static const SharedList<i32> __constant_1 = std::make_shared',
            source)
        self.assert_in('if (Bool(contains(v, __constant_1))) {', source)

    def test_if_mix_of_types(self):
        source = transpile_source('def foo(v: (bool, [string], (u8, i8))):\n'
                                  '    if v != (True, [], (1, -5)):\n'
                                  '        print(v)\n')

        self.assert_in(
            'static const SharedTuple<Bool, SharedList<String>, SharedTuple<u8, i8>> '
            '__constant_1 = std::make_shared',
            source)
        self.assert_in('if (Bool(v != __constant_1)) {', source)

    def test_if_mix_of_types_not_constant(self):
        source = transpile_source('def foo(v: (bool, [string], (u8, i8)), k: bool):\n'
                                  '    if v != (k, [], (1, -5)):\n'
                                  '        print(v)\n')

        self.assertNotIn('static const SharedTuple', source)
        self.assert_in('if (Bool(v != std::make_shared<', source)

    def test_if_primitive_types_not_constant(self):
        source = transpile_source('def foo(v: i64):\n'
                                  '    if v == 1:\n'
                                  '        print(v)\n')

        self.assertNotIn('static const i64', source)
        self.assert_in('if (Bool(v == 1)', source)

    def test_match_string(self):
        source = transpile_source('def foo(v: string):\n'
                                  '    res = 0\n'
                                  '    match v:\n'
                                  '        case "123":\n'
                                  '            res = 1\n'
                                  '        case "hi":\n'
                                  '            res = 2\n'
                                  '    print(res)\n')

        self.assert_in('static const String __constant_2 = String("123");', source)
        self.assert_in('static const String __constant_3 = String("hi");', source)
        self.assert_in('if (__subject_1 == __constant_2) {', source)
        self.assert_in('if (__subject_1 == __constant_3) {', source)
