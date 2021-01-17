from mys.transpiler import Source
from mys.transpiler import TranspilerError
from mys.transpiler import transpile

from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_generics(self):
        build_and_test_module('generics')

    def test_missing_generic_type(self):
        self.assert_transpile_raises(
            '@generic\n'
            'def foo():\n'
            '    pass\n',
            '  File "", line 1\n'
            '    @generic\n'
            '     ^\n'
            "CompileError: at least one parameter required\n")

    def test_generic_given_more_than_once(self):
        self.assert_transpile_raises(
            '@generic(T1)\n'
            '@generic(T2)\n'
            'def foo(a: T1, b: T2):\n'
            '    pass\n',
            '  File "", line 2\n'
            '    @generic(T2)\n'
            '     ^\n'
            "CompileError: @generic can only be given once\n")

    def test_generic_type_given_more_than_once(self):
        self.assert_transpile_raises(
            '@generic(T1, T1)\n'
            'def foo(a: T1):\n'
            '    pass\n',
            '  File "", line 1\n'
            '    @generic(T1, T1)\n'
            '                 ^\n'
            "CompileError: 'T1' can only be given once\n")

    def test_generic_undefined_type(self):
        self.assert_transpile_raises(
            '@generic(T)\n'
            'def add(a: T) -> T:\n'
            '    return a\n'
            'def foo():\n'
            '    print(add[Foo](None))\n',
            '  File "", line 5\n'
            '        print(add[Foo](None))\n'
            '                  ^\n'
            "CompileError: undefined type 'Foo'\n")

    def test_generic_undefined_type_slice(self):
        self.assert_transpile_raises(
            '@generic(T1, T2)\n'
            'def add() -> T1:\n'
            '    return T2(5)\n'
            'def foo():\n'
            '    print(add[i8, Foo]())\n',
            '  File "", line 5\n'
            '        print(add[i8, Foo]())\n'
            '                      ^\n'
            "CompileError: undefined type 'Foo'\n")

    def test_generic_function_type_not_supported_same_file(self):
        self.assert_transpile_raises(
            '@generic(T)\n'
            'def add(a: T):\n'
            '    a.bar()\n'
            'def foo():\n'
            '    add[u8](1)\n',
            '  File "", line 5\n'
            '        add[u8](1)\n'
            '        ^\n'
            '  File "", line 3\n'
            '        a.bar()\n'
            '        ^\n'
            "CompileError: primitive type 'u8' do not have methods\n")

    def test_generic_function_type_not_supported_different_files(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile([
                Source('@generic(T)\n'
                       'def add(a: T):\n'
                       '    a.bar()\n',
                       module='foo.lib',
                       mys_path='foo/src/lib.mys'),
                Source('from foo import add\n'
                       '# Blank line for different line numbers in foo and bar.\n'
                       'def foo():\n'
                       '    add[u8](1)\n',
                       module='bar.lib',
                       mys_path='bar/src/lib.mys')
            ])

        self.assert_exception_string(
            cm,
            '  File "bar/src/lib.mys", line 4\n'
            '        add[u8](1)\n'
            '        ^\n'
            '  File "foo/src/lib.mys", line 3\n'
            '        a.bar()\n'
            '        ^\n'
            "CompileError: primitive type 'u8' do not have methods\n")

    def test_generic_class_type_not_supported_same_file(self):
        self.assert_transpile_raises(
            '@generic(T)\n'
            'class Add:\n'
            '    def calc(self, a: T) -> u8:\n'
            '        return a.calc()\n'
            'def foo():\n'
            '    a = Add[bool]()\n'
            '    print(a.calc(True))\n',
            '  File "", line 6\n'
            '        a = Add[bool]()\n'
            '            ^\n'
            '  File "", line 4\n'
            '            return a.calc()\n'
            '                   ^\n'
            "CompileError: primitive type 'bool' do not have methods\n")

    def test_generic_class_type_not_supported_different_files(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile([
                Source('@generic(T)\n'
                       'class Add:\n'
                       '    def calc(self, a: T) -> u8:\n'
                       '        return a.calc()\n',
                       module='foo.lib',
                       mys_path='foo/src/lib.mys'),
                Source('from foo import Add\n'
                       'def foo():\n'
                       '    a = Add[bool]()\n'
                       '    print(a.calc(True))\n',
                       module='bar.lib',
                       mys_path='bar/src/lib.mys')
            ])

        self.assert_exception_string(
            cm,
            '  File "bar/src/lib.mys", line 3\n'
            '        a = Add[bool]()\n'
            '            ^\n'
            '  File "foo/src/lib.mys", line 4\n'
            '            return a.calc()\n'
            '                   ^\n'
            "CompileError: primitive type 'bool' do not have methods\n")

    def test_generic_function_type_mismatch(self):
        self.assert_transpile_raises(
            '@generic(T)\n'
            'def bar(v: T):\n'
            '    print(v)\n'
            'def foo():\n'
            '    bar[u8]("hi")\n',
            '  File "", line 5\n'
            '        bar[u8]("hi")\n'
            '                ^\n'
            "CompileError: expected a 'u8', got a 'string'\n")

    def test_generic_class_type_mismatch(self):
        self.assert_transpile_raises(
            '@generic(T)\n'
            'class Add:\n'
            '    def calc(self, a: T) -> u8:\n'
            '        return 2 * a[0].calc()\n'
            'class One:\n'
            '    def calc(self) -> u8:\n'
            '        return 1\n'
            'class Two:\n'
            '    def calc(self) -> u8:\n'
            '        return 2\n'
            'def foo():\n'
            '    x = Add[One]()\n'
            '    assert x.calc(Two()) == 2\n',
            '  File "", line 13\n'
            '        assert x.calc(Two()) == 2\n'
            '                      ^\n'
            "CompileError: expected a 'foo.lib.One', got a 'foo.lib.Two'\n")

    def test_generic_class_wrong_number_of_types(self):
        self.assert_transpile_raises(
            '@generic(T)\n'
            'class Add:\n'
            '    a: T\n'
            'def foo():\n'
            '    print(Add[One, u8](1))\n',
            '  File "", line 5\n'
            '        print(Add[One, u8](1))\n'
            '                  ^\n'
            "CompileError: expected 1 type, got 2\n")

    def test_generic_function_wrong_number_of_types(self):
        self.assert_transpile_raises(
            '@generic(T)\n'
            'def foo(a: T):\n'
            '    print(a[0], a[1])\n'
            'def bar():\n'
            '    foo[i8, string](1, "a")\n',
            '  File "", line 5\n'
            '        foo[i8, string](1, "a")\n'
            '            ^\n'
            "CompileError: expected 1 type, got 2\n")
