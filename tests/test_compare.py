from .utils import TestCase
from .utils import build_and_test_module
from .utils import transpile_source


class Test(TestCase):

    def test_compare(self):
        with self.assertRaises(SystemExit):
            build_and_test_module('compare')

    def test_assert_between(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    a = 2\n'
            '    assert 1 <= a < 3\n',
            '  File "", line 3\n'
            "        assert 1 <= a < 3\n"
            '               ^\n'
            "CompileError: can only compare two values\n")

    def test_between(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    a = 2\n'
            '    print(1 <= a < 3)\n',
            '  File "", line 3\n'
            "        print(1 <= a < 3)\n"
            '              ^\n'
            "CompileError: can only compare two values\n")

    def test_i64_and_bool(self):
        self.assert_transpile_raises(
            'def foo() -> bool:\n'
            '    return 1 == True',
            '  File "", line 2\n'
            '        return 1 == True\n'
            '               ^\n'
            "CompileError: cannot convert 'i64/i32/i16/i8/u64/u32/u16/u8' "
            "to 'bool'\n")

    def test_mix_of_literals_and_known_types_1(self):
        source = transpile_source('def foo():\n'
                                  '    k: u64 = 1\n'
                                  '    v: i64 = 1\n'
                                  '    if 0xffffffffffffffff == k:\n'
                                  '        pass\n'
                                  '    print(v)\n')

        self.assert_in('18446744073709551615ull', source)

    def test_wrong_types_1(self):
        self.assert_transpile_raises(
            'def foo() -> bool:\n'
            '    return 1 == [""]\n',
            '  File "", line 2\n'
            '        return 1 == [""]\n'
            '               ^\n'
            "CompileError: cannot convert 'i64/i32/i16/i8/u64/u32/u16/u8' to "
            "'[string]'\n")

    def test_wrong_types_2(self):
        self.assert_transpile_raises(
            'def foo() -> bool:\n'
            '    return [""] in 1\n',
            '  File "", line 2\n'
            '        return [""] in 1\n'
            '                       ^\n'
            "CompileError: not an iterable\n")

    def test_wrong_types_3(self):
        self.assert_transpile_raises(
            'def foo() -> bool:\n'
            '    return [""] not in 1\n',
            '  File "", line 2\n'
            '        return [""] not in 1\n'
            '                           ^\n'
            "CompileError: not an iterable\n")

    def test_wrong_types_4(self):
        self.assert_transpile_raises(
            'def foo() -> bool:\n'
            '    return 2.0 == 1\n',
            '  File "", line 2\n'
            '        return 2.0 == 1\n'
            '               ^\n'
            "CompileError: cannot convert 'f64/f32' to "
            "'i64/i32/i16/i8/u64/u32/u16/u8'\n")

    def test_wrong_types_5(self):
        self.assert_transpile_raises(
            'def foo() -> bool:\n'
            '    return 1.0 == [""]\n',
            '  File "", line 2\n'
            '        return 1.0 == [""]\n'
            '               ^\n'
            "CompileError: cannot convert 'f64/f32' to '[string]'\n")

    def test_wrong_types_6(self):
        self.assert_transpile_raises(
            'def foo(a: i32) -> bool:\n'
            '    return a in [""]\n',
            '  File "", line 2\n'
            '        return a in [""]\n'
            '               ^\n'
            "CompileError: types 'i32' and 'string' differs\n")

    def test_wrong_types_7(self):
        self.assert_transpile_raises(
            'def foo(a: i32) -> bool:\n'
            '    return a in a\n',
            '  File "", line 2\n'
            '        return a in a\n'
            '                    ^\n'
            "CompileError: not an iterable\n")

    def test_wrong_types_8(self):
        self.assert_transpile_raises(
            'def foo(a: i32) -> bool:\n'
            '    return 1 in a\n',
            '  File "", line 2\n'
            '        return 1 in a\n'
            '                    ^\n'
            "CompileError: not an iterable\n")

    def test_wrong_types_9(self):
        self.assert_transpile_raises(
            'def foo(a: i32) -> bool:\n'
            '    return "" == a\n',
            '  File "", line 2\n'
            '        return "" == a\n'
            '               ^\n'
            "CompileError: types 'string' and 'i32' differs\n")

    def test_wrong_types_10(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    print(1 is None)\n',
            '  File "", line 2\n'
            '        print(1 is None)\n'
            '                   ^\n'
            "CompileError: 'i64' cannot be None\n")

    def test_wrong_types_11(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    print(1.0 is None)\n',
            '  File "", line 2\n'
            '        print(1.0 is None)\n'
            '                     ^\n'
            "CompileError: 'f64' cannot be None\n")

    def test_wrong_types_12(self):
        self.assert_transpile_raises(
            'def foo(a: i32):\n'
            '    print(a is None)\n',
            '  File "", line 2\n'
            '        print(a is None)\n'
            '              ^\n'
            "CompileError: 'i32' cannot be None\n")

    def test_wrong_types_13(self):
        self.assert_transpile_raises(
            'def foo(a: i32):\n'
            '    print(None is a)\n',
            '  File "", line 2\n'
            '        print(None is a)\n'
            '              ^\n'
            "CompileError: 'i32' cannot be None\n")

    def test_wrong_types_14(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    print(True is None)\n',
            '  File "", line 2\n'
            '        print(True is None)\n'
            '              ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_wrong_types_15(self):
        self.assert_transpile_raises(
            'def foo(a: bool):\n'
            '    print(None is a)\n',
            '  File "", line 2\n'
            '        print(None is a)\n'
            '              ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_wrong_types_16(self):
        self.assert_transpile_raises(
            'def foo(a: bool):\n'
            '    print(a is not 1)\n',
            '  File "", line 2\n'
            '        print(a is not 1)\n'
            '              ^\n'
            "CompileError: cannot convert 'bool' to "
            "'i64/i32/i16/i8/u64/u32/u16/u8'\n")

    def test_wrong_types_17(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    print(None in [1, 5])\n',
            '  File "", line 2\n'
            '        print(None in [1, 5])\n'
            '              ^\n'
            "CompileError: 'i64' cannot be None\n")

    def test_wrong_types_18(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    print(None == "")\n',
            '  File "", line 2\n'
            '        print(None == "")\n'
            '              ^\n'
            "CompileError: use 'is' and 'is not' to compare to None\n")

    def test_wrong_types_20(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    if (1, ("", True)) == (1, ("", 1)):\n'
            '        pass\n',
            # ToDo: Marker in wrong place.
            '  File "", line 2\n'
            '        if (1, ("", True)) == (1, ("", 1)):\n'
            '           ^\n'
            "CompileError: cannot convert 'bool' to "
            "'i64/i32/i16/i8/u64/u32/u16/u8'\n")

    def test_bare_compare(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    1 == 2\n',
            '  File "", line 2\n'
            '        1 == 2\n'
            '        ^\n'
            "CompileError: bare comparision\n")
