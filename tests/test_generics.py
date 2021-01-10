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
            # ToDo: Not perfect error message. Should also(?) show the
            # specialization.
            '  File "", line 2\n'
            '    def add(a: T) -> T:\n'
            '               ^\n'
            "CompileError: undefined type 'Foo'\n")

    def test_generic_type_not_supported(self):
        self.assert_transpile_raises(
            '@generic(T)\n'
            'def add(a: T):\n'
            '    a.bar()\n'
            'def foo():\n'
            '    add[u8](1)\n',
            # ToDo: Not perfect error message. Should also(?) show the
            # specialization.
            '  File "", line 3\n'
            '        a.bar()\n'
            '        ^\n'
            "CompileError: primitive type 'u8' do not have methods\n")
