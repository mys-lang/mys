import shutil
import os
from .utils import build_and_test_module
from .utils import TestCase
from .utils import transpile_source
from .utils import remove_ansi


class Test(TestCase):

    def setUp(self):
        os.makedirs('tests/build', exist_ok=True)

    def test_classes(self):
        build_and_test_module('classes')

    def test_class_in_function_should_fail(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main():\n'
                             '    class A:\n'
                             '        pass\n',
                             mys_path='<unknown>',
                             has_main=True)

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<unknown>", line 2\n'
            '        class A:\n'
            '        ^\n'
            'CompileError: class definitions are only allowed on module level\n')

    def test_comaprsion_operator_return_types(self):
        ops = ['eq', 'ne', 'gt', 'ge', 'lt', 'le']

        for op in ops:
            with self.assertRaises(Exception) as cm:
                transpile_source('class Foo:\n'
                                 f'    def __{op}__(self, other: Foo):\n'
                                 '        return True\n',
                                 mys_path='src/mod.mys',
                                 module_hpp='pkg/mod.mys.hpp')

            self.assertEqual(
                remove_ansi(str(cm.exception)),
                '  File "src/mod.mys", line 2\n'
                f'        def __{op}__(self, other: Foo):\n'
                '        ^\n'
                f'CompileError: __{op}__() must return bool\n')

    def test_arithmetic_operator_return_types(self):
        ops = ['add', 'sub']

        for op in ops:
            with self.assertRaises(Exception) as cm:
                transpile_source('class Foo:\n'
                                 f'    def __{op}__(self, other: Foo) -> bool:\n'
                                 '        return True\n',
                                 'src/mod.mys',
                                 'pkg/mod.mys.hpp')

            self.assertEqual(
                remove_ansi(str(cm.exception)),
                '  File "src/mod.mys", line 2\n'
                f'        def __{op}__(self, other: Foo) -> bool:\n'
                '        ^\n'
                f'CompileError: __{op}__() must return Foo\n')

    def test_undefined_class(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    Bar()\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        Bar()\n'
            '        ^\n'
            "CompileError: undefined class/trait/enum 'Bar'\n")

    def test_test_decorator_only_allowed_on_functions(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Class1:\n'
                             '    @test\n'
                             '    def foo(self):\n'
                             '        pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        @test\n'
            '         ^\n'
            "CompileError: invalid decorator 'test'\n")

    def test_non_snake_case_class_member(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class A:\n'
                             '    Aa: i32')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        Aa: i32\n'
            '        ^\n'
            "CompileError: class member names must be snake case\n")

    def test_non_pascal_case_class(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class apa:\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    class apa:\n'
            '    ^\n'
            "CompileError: class names must be pascal case\n")

    def test_invalid_decorator(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@foobar\n'
                             'class Foo:\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @foobar\n'
            '     ^\n'
            "CompileError: invalid decorator 'foobar'\n")

    def test_wrong_method_parameter_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def foo(self, a: string):\n'
                             '        pass\n'
                             'def bar():\n'
                             '    Foo().foo(True)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        Foo().foo(True)\n'
            '                  ^\n'
            "CompileError: expected a 'string', got a 'bool'\n")

    def test_call_member_method(self):
        source = transpile_source('class Foo:\n'
                                  '    def fam(self):\n'
                                  '        pass\n'
                                  'class Bar:\n'
                                  '    foo: Foo\n'
                                  'def foo2(bar: Bar):\n'
                                  '    bar.foo.fam()')

        self.assert_in(
            'shared_ptr_not_none(shared_ptr_not_none(bar)->foo)->fam();',
            source)

    def test_assign_to_self_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def foo(self):\n'
                             '        self = Foo()\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '            self = Foo()\n'
            '            ^\n'
            "CompileError: it's not allowed to assign to 'self'\n")

    def test_assign_to_self_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def foo(self):\n'
                             '        self: u8 = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '            self: u8 = 1\n'
            '            ^\n'
            "CompileError: redefining variable 'self'\n")

    def test_class_functions_not_implemented(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def foo():\n'
                             '        pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            "        def foo():\n"
            '        ^\n'
            "CompileError: class functions are not yet implemented\n")

    def test_compare_wrong_types_19(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    pass\n'
                             'class Bar:\n'
                             '    pass\n'
                             'def foo():\n'
                             '    if Foo() is Bar():\n'
                             '        pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 6\n'
            "        if Foo() is Bar():\n"
            '           ^\n'
            "CompileError: types 'foo.lib.Foo' and 'foo.lib.Bar' differs\n")

    def test_class_has_no_member_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    value: i32\n'
                             'def foo(v: Foo):\n'
                             '    print(v.missing)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(v.missing)\n'
            '              ^\n'
            "CompileError: class 'foo.lib.Foo' has no member 'missing'\n")

    def test_class_has_no_member_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    value: i32\n'
                             '    def foo(self):\n'
                             '        print(self.missing)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '            print(self.missing)\n'
            '                  ^\n'
            "CompileError: class 'foo.lib.Foo' has no member 'missing'\n")

    def test_class_has_no_member_3(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    a: i32\n'
                             'def foo():\n'
                             '    print(Foo(1).b)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(Foo(1).b)\n'
            '              ^\n'
            "CompileError: class 'foo.lib.Foo' has no member 'b'\n")

    def test_class_private_member(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    _a: i32\n'
                             'def foo():\n'
                             '    print(Foo()._a)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(Foo()._a)\n'
            '              ^\n'
            "CompileError: class 'foo.lib.Foo' member '_a' is private\n")

    def test_unknown_class_member_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    a: Bar\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        a: Bar\n'
            '           ^\n'
            "CompileError: undefined type 'Bar'\n")

    def test_class_init_too_many_parameters(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    a: i32\n'
                             'def foo():\n'
                             '    print(Foo(1, 2))\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(Foo(1, 2))\n'
            '              ^\n'
            "CompileError: expected 1 parameter, got 2\n")

    def test_class_init_wrong_parameter_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    a: (bool, string)\n'
                             'def foo():\n'
                             '    print(Foo(("", 1)))\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(Foo(("", 1)))\n'
            '                   ^\n'
            "CompileError: expected a 'bool', got a 'string'\n")

    def test_assign_to_class_call(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def bar() -> i32:\n'
                             '        return 1\n'
                             'def foo():\n'
                             '    Foo() = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<string>", line 5\n'
            '    Foo() = 1\n'
            '    ^\n'
            "SyntaxError: cannot assign to function call\n")

    def test_assign_to_method_call(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def bar() -> i32:\n'
                             '        return 1\n'
                             'def foo():\n'
                             '    Foo().bar() = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<string>", line 5\n'
            '    Foo().bar() = 1\n'
            '    ^\n'
            "SyntaxError: cannot assign to function call\n")

    def test_class_member_default(self):
        with self.assertRaises(Exception) as cm:
            source = transpile_source('class Foo:\n'
                                      '    a: i32 = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        a: i32 = 1\n'
            '                 ^\n'
            "CompileError: class members cannot have default values\n")

    def test_wrong_class_method_parameter_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def foo(self, v: bool):\n'
                             '        pass\n'
                             'def foo(v: Foo):\n'
                             '    v.foo("")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        v.foo("")\n'
            '              ^\n'
            "CompileError: expected a 'bool', got a 'string'\n")

    def test_positive_class(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    pass\n'
                             'def foo():\n'
                             '    print(+Foo())\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(+Foo())\n'
            '              ^\n'
            "CompileError: unary '+' can only operate on numbers\n")

    def test_method_call_in_assert(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def get_self(self) -> Foo:\n'
                             '        return self\n'
                             '    def get_same(self, this: Foo) -> Foo:\n'
                             '        return this\n'
                             'def foo():\n'
                             '    x = Foo()\n'
                             '    assert x is x.get_self().same(x)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 8\n'
            '        assert x is x.get_self().same(x)\n'
            '                    ^\n'
            "CompileError: class 'foo.lib.Foo' has no method 'same'\n")

    def test_import_after_class_definition(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    pass\n'
                             'from bar import fie\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '    from bar import fie\n'
            '    ^\n'
            "CompileError: imports must be at the beginning of the file\n")
