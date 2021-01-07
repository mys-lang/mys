import difflib
from mys.parser import ast
from mys.transpile import transpile
from mys.transpile import Source
from mys.transpile.definitions import find_definitions

from .utils import remove_ansi
from .utils import TestCase

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


class Test(TestCase):

    def test_invalid_main_argument(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main(argv: i32): pass',
                             has_main=True)

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "", line 1\n'
                         '    def main(argv: i32): pass\n'
                         '    ^\n'
                         "CompileError: main() takes 'argv: [string]' or no arguments\n")

    def test_main_no_argv(self):
        transpile_source('def main():\n'
                         '    pass\n',
                         has_main=True)

    def test_main_argv(self):
        transpile_source('def main(argv: [string]):\n'
                         '    pass\n',
                         has_main=True)

    def test_invalid_main_return_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main() -> i32: pass',
                             has_main=True)

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "", line 1\n'
                         '    def main() -> i32: pass\n'
                         '    ^\n'
                         "CompileError: main() must not return any value\n")

    def test_return_nothing_in_main(self):
        source = transpile_source('def main():\n'
                                  '    return\n',
                                  has_main=True)

        # main() must return void.
        self.assert_in('void main(int __argc, const char *__argv[])\n'
                       '{\n'
                       '    (void)__argc;\n'
                       '    (void)__argv;\n'
                       '    return;\n'
                       '}\n',
                       source)

    def test_lambda_not_supported(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main(): print((lambda x: x)(1))',
                             mys_path='foo.py',
                             has_main=True)

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "foo.py", line 1\n'
                         '    def main(): print((lambda x: x)(1))\n'
                         '                       ^\n'
                         'CompileError: lambda functions are not supported\n')

    def test_bad_syntax(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('DEF main(): pass',
                             mys_path='<unknown>',
                             has_main=True)

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "<unknown>", line 1\n'
                         '    DEF main(): pass\n'
                         '        ^\n'
                         'SyntaxError: invalid syntax\n')

    def test_import_in_function_should_fail(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main():\n'
                             '    import foo\n',
                             mys_path='<unknown>',
                             has_main=True)

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<unknown>", line 2\n'
            '        import foo\n'
            '        ^\n'
            'CompileError: imports are only allowed on module level\n')

    def test_import_from_in_function_should_fail(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main():\n'
                             '    from foo import bar\n',
                             has_main=True)

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        from foo import bar\n'
            '        ^\n'
            'CompileError: imports are only allowed on module level\n')

    def test_import(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('import foo\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    import foo\n'
            '    ^\n'
            "CompileError: only 'from <module> import ...' is allowed\n")

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

    def test_empty_function(self):
        source = transpile_source('def foo():\n'
                                  '    pass\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '\n'
                       '}\n',
                       source)

    def test_multiple_imports_failure(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('from foo import bar, fie\n',
                             mys_path='<unknown>')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<unknown>", line 1\n'
            '    from foo import bar, fie\n'
            '    ^\n'
            'CompileError: only one import is allowed, found 2\n')

    def test_relative_import_outside_package(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('from .. import fie\n',
                             mys_path='src/mod.mys',
                             module_hpp='pkg/mod.mys.hpp')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "src/mod.mys", line 1\n'
            '    from .. import fie\n'
            '    ^\n'
            'CompileError: relative import is outside package\n')

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

    def test_basic_print_function(self):
        source = transpile_source('def main():\n'
                                  '    print(1)\n',
                                  has_main=True)

        self.assert_in('std::cout << 1 << std::endl;', source)

    def test_print_function_with_flush_true(self):
        source = transpile_source('def main():\n'
                                  '    print(1, flush=True)\n',
                                  has_main=True)

        self.assert_in('    std::cout << 1 << std::endl;\n'
                       '    if (Bool(true)) {\n'
                       '        std::cout << std::flush;\n'
                       '    }',
                       source)

    def test_print_function_with_flush_false(self):
        source = transpile_source('def main():\n'
                                  '    print(1, flush=False)\n',
                                  has_main=True)

        self.assert_in('std::cout << 1 << std::endl;', source)

    def test_print_function_with_and_and_flush(self):
        source = transpile_source('def main():\n'
                                  '    print(1, end="!!", flush=True)\n',
                                  has_main=True)

        self.assert_in('std::cout << std::flush;\n',
                       source)

    def test_print_function_i8_u8_as_integers_not_char(self):
        source = transpile_source('def main():\n'
                                  '    print(i8(-1), u8(1), u16(1))\n',
                                  has_main=True)

        self.assert_in(
            '    std::cout << (int)i8(-1) << " " << (unsigned)u8(1) '
            '<< " " << u16(1) << std::endl;\n',
            source)

    def test_print_function_invalid_keyword(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main():\n'
                             '    print("Hi!", foo=True)\n',
                             'src/mod.mys',
                             'pkg/mod.mys.hpp',
                             has_main=True)

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "src/mod.mys", line 2\n'
            '        print("Hi!", foo=True)\n'
            '        ^\n'
            "CompileError: invalid keyword argument 'foo' to print(), only "
            "'end' and 'flush' are allowed\n")

    def test_undefined_variable_1(self):
        # Everything ok, 'value' defined.
        transpile_source('def foo(value: bool) -> bool:\n'
                         '    return value\n')

        # Error, 'value' is not defined.
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return value\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return value\n'
            '               ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_variable_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> i32:\n'
                             '    return 2 * value\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return 2 * value\n'
            '                   ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_variable_3(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(v1: i32, v2: i32) -> i32:\n'
                             '    return v1 + v2\n'
                             'def bar() -> i32:\n'
                             '    a: i32 = 1\n'
                             '    return foo(a, value)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        return foo(a, value)\n'
            '                      ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_variable_5(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a: i8 = a\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            "        a: i8 = a\n"
            '                ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_undefined_variable_6(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a: [i8] = a\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            "        a: [i8] = a\n"
            '                  ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_undefined_variable_7(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    if a == "":\n'
                             '        print("hej")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        if a == "":\n'
            '           ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_undefined_variable_in_fstring(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def bar():\n'
                             '    print(f"{value}")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(f"{value}")\n'
            '                 ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_undefined_function(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    bar()\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        bar()\n'
            '        ^\n'
            "CompileError: undefined function 'bar'\n")

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

    def test_undefined_variable_index(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    bar[0] = True\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        bar[0] = True\n'
            '        ^\n'
            "CompileError: undefined variable 'bar'\n")

    def test_only_global_defined_in_callee(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('GLOB: bool = True\n'
                             'def bar() -> i32:\n'
                             '    a: i32 = 1\n'
                             '    print(a)\n'
                             'def foo() -> i32:\n'
                             '    return GLOB + a\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 6\n'
            '        return GLOB + a\n'
            '                      ^\n'
            "CompileError: undefined variable 'a'\n")

    def test_imported_variable_usage(self):
        transpile([
            Source('from foo import BAR\n'
                   '\n'
                   'def fie() -> i32:\n'
                   '    return 2 * BAR\n'),
            Source('BAR: i32 = 1', module='foo.lib')
        ])

    def test_imported_module_does_not_exist(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('from kalle import bar\n'
                             '\n'
                             'def fie() -> i32:\n'
                             '    return 2 * bar\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    from kalle import bar\n'
            '    ^\n'
            "CompileError: imported module 'kalle.lib' does not exist\n")

    def test_imported_module_does_not_contain(self):
        with self.assertRaises(Exception) as cm:
            transpile([
                Source('from foo import bar\n'
                       '\n'
                       'def fie() -> i32:\n'
                       '    return 2 * bar\n'),
                Source('BOO: i32 = 1', module='foo.lib')
            ])

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    from foo import bar\n'
            '    ^\n'
            "CompileError: imported module 'foo.lib' does not contain 'bar'\n")

    def test_import_private_function_fails(self):
        with self.assertRaises(Exception) as cm:
            transpile([
                Source('from foo import _BAR\n'
                       '\n'
                       'def fie() -> i32:\n'
                       '    return 2 * _BAR\n'),
                Source('_BAR: i32 = 1', module='foo.lib')
            ])

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    from foo import _BAR\n'
            '    ^\n'
            "CompileError: cannot import private definition '_BAR'\n")

    def test_import_function_ok(self):
        transpile([
            Source('from foo import bar\n'
                   'def fie():\n'
                   '    bar()\n'),
            Source('def bar():\n'
                   '    pass\n',
                   module='foo.lib')
        ])

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

    def test_missing_generic_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@generic\n'
                             'def foo():\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @generic\n'
            '     ^\n'
            "CompileError: at least one parameter required\n")

    def test_missing_errors_in_raises(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@raises()\n'
                             'def foo():\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @raises()\n'
            '     ^\n'
            "CompileError: @raises requires at least one error\n")

    def test_generic_given_more_than_once(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@generic(T1)\n'
                             '@generic(T2)\n'
                             'def foo(a: T1, b: T2):\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '    @generic(T2)\n'
            '     ^\n'
            "CompileError: @generic can only be given once\n")

    def test_generic_type_given_more_than_once(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@generic(T1, T1)\n'
                             'def foo(a: T1):\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @generic(T1, T1)\n'
            '                 ^\n'
            "CompileError: 'T1' can only be given once\n")

    def test_test_can_not_take_any_values(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@test(H)\n'
                             'def foo():\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @test(H)\n'
            '     ^\n'
            "CompileError: no parameters expected\n")

    def test_non_snake_case_function(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def Apa():\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    def Apa():\n'
            '    ^\n'
            "CompileError: function names must be snake case\n")

    def test_non_snake_case_global_variable(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('Aa: i32 = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    Aa: i32 = 1\n'
            '    ^\n'
            "CompileError: global variable names must be upper case snake case\n")

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

    def test_non_snake_case_function_parameter_name(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(A: i32):\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    def foo(A: i32):\n'
            '            ^\n'
            "CompileError: parameter names must be snake case\n")

    def test_non_snake_case_local_variable(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    A: i32 = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        A: i32 = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_for_loop_underscore_variable(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for _ in [1, 4]:\n'
                             '        print(_)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '            print(_)\n'
            '                  ^\n'
            "CompileError: undefined variable '_'\n")

    def test_underscore_variable_name(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    _: i32 = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        _: i32 = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_underscore_inferred_variable_name(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    _ = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        _ = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_non_snake_case_local_inferred_variable(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    A = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        A = 1\n'
            '        ^\n'
            "CompileError: local variable names must be snake case\n")

    def test_missing_function_parameter_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(x):\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    def foo(x):\n'
            '            ^\n'
            "CompileError: parameters must have a type\n")

    def test_invalid_decorator_value(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@raises(A(B))\n'
                             'def foo():\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @raises(A(B))\n'
            '            ^\n'
            "CompileError: invalid decorator value\n")

    def test_invalid_decorator_value_syntax(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@raises[A]\n'
                             'def foo():\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @raises[A]\n'
            '     ^\n'
            "CompileError: decorators must be @name or @name()\n")

    def test_invalid_string_enum_member_value(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A = "s"\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        A = "s"\n'
            '            ^\n'
            "CompileError: invalid enum member value\n")

    def test_invalid_enum_member_name(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    V1, V2 = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        V1, V2 = 1\n'
            '        ^\n'
            "CompileError: invalid enum member syntax\n")

    def test_invalid_enum_member_value_plus_sign(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A = +1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        A = +1\n'
            '            ^\n'
            "CompileError: invalid enum member value\n")

    def test_invalid_enum_member_value_variable(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A = b\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        A = b\n'
            '            ^\n'
            "CompileError: invalid enum member value\n")

    def test_non_pascal_case_enum_member_name(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    aB = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        aB = 1\n'
            '        ^\n'
            "CompileError: enum member names must be pascal case\n")

    def test_invalid_enum_member_syntax(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    1 + 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        1 + 1\n'
            '        ^\n'
            "CompileError: invalid enum member syntax\n")

    def test_empty_enum_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum()\n'
                             'class Foo:\n'
                             '    Ab = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @enum()\n'
            '     ^\n'
            "CompileError: one parameter expected, got 0\n")

    def test_bad_enum_type_f32(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum(f32)\n'
                             'class Foo:\n'
                             '    Ab = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @enum(f32)\n'
            '          ^\n'
            "CompileError: integer type expected, not 'f32'\n")

    def test_define_empty_trait(self):
        header = transpile_early_header('@trait\n'
                                        'class Foo:\n'
                                        '    pass\n')
        self.assert_in('class Foo : public Object {\n'
                       'public:\n'
                       '};\n',
                       header)

    def test_define_trait_with_member(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@trait\n'
                             'class Foo:\n'
                             '    a: i32\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        a: i32\n'
            '        ^\n'
            "CompileError: traits cannot have members\n")

    def test_define_trait_with_parameter(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@trait(u32)\n'
                             'class Foo:\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    @trait(u32)\n'
            '     ^\n'
            "CompileError: no parameters expected\n")

    def test_define_trait_with_same_name_twice(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@trait\n'
                             'class Foo:\n'
                             '    pass\n'
                             '@trait\n'
                             'class Foo:\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '    class Foo:\n'
            '    ^\n'
            "CompileError: there is already a trait called 'Foo'\n")

    def test_define_trait_with_same_name_as_class(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    pass\n'
                             '@trait\n'
                             'class Foo:\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '    class Foo:\n'
            '    ^\n'
            "CompileError: there is already a class called 'Foo'\n")

    def test_trait_does_not_exist(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo(Bar):\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    class Foo(Bar):\n'
            '              ^\n'
            "CompileError: trait does not exist\n")

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

    def test_match_class(self):
        # Should probably be supported eventually.
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    x: i32\n'
                             'def foo(v: Foo):\n'
                             '    match v:\n'
                             '        case Foo(x=1):\n'
                             '            pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        match v:\n'
            '              ^\n'
            "CompileError: matching classes if not supported\n")

    def test_match_wrong_case_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(v: i32):\n'
                             '    match v:\n'
                             '        case 1:\n'
                             '            pass\n'
                             '        case "":\n'
                             '            pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '            case "":\n'
            '                 ^\n'
            "CompileError: expected a 'i32', got a 'string'\n")

    def test_match_pattern_condition(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(x: i32, y: u8):\n'
                             '    match x:\n'
                             '        case 1 if y == 2:\n'
                             '            pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '            case 1 if y == 2:\n'
            '                      ^\n'
            "CompileError: guards are not supported\n")

    def test_match_trait_pattern_condition(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@trait\n'
                             'class Base:\n'
                             '    pass\n'
                             'class Foo(Base):\n'
                             '    pass\n'
                             'def foo(base: Base):\n'
                             '    match base:\n'
                             '        case Foo() if False:\n'
                             '            print("foo")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 8\n'
            '            case Foo() if False:\n'
            '                          ^\n'
            "CompileError: guards are not supported\n")

    def test_inferred_type_combined_integers_assignment_too_big(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    value = (0xffffffffffffffff + 1)\n'
                             '    print(value)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        value = (0xffffffffffffffff + 1)\n'
            '                 ^\n'
            "CompileError: integer literal out of range for 'i64'\n")

    def test_test_functions_not_in_header(self):
        header = transpile_header('@test\n'
                                  'def test_foo():\n'
                                  '    pass\n',
                                  module_hpp='foo/lib.mys.hpp')

        self.assertNotIn('test_foo', header)

    def test_enum_as_function_parameter_and_return_value(self):
        source = transpile_source(
            '@enum\n'
            'class City:\n'
            '\n'
            '    Linkoping = 5\n'
            '    Norrkoping = 8\n'
            '    Vaxjo = 10\n'
            'def enum_foo(source: City, destination: City) -> City:\n'
            '    return City.Vaxjo\n')

        self.assert_in(
            'i64 enum_foo(i64 source, i64 destination)\n'
            '{\n'
            '    return (i64)City::Vaxjo;\n'
            '}\n',
            source)

    def test_return_i64_from_function_returning_string(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> string:\n'
                             '    return True')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return True\n'
            '               ^\n'
            "CompileError: expected a 'string', got a 'bool'\n")

    def test_return_list_from_function_returning_tuple(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> (bool, i64):\n'
                             '    return [1]')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return [1]\n'
            '               ^\n'
            "CompileError: cannot convert list to '(bool, i64)'\n")

    def test_return_tuple_from_function_returning_list(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> [bool]:\n'
                             '    return (1, True)')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return (1, True)\n'
            '               ^\n'
            "CompileError: cannot convert tuple to '[bool]'\n")

    def test_return_dict_from_function_returning_list(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    pass\n'
                             'def foo() -> [(string, Foo)]:\n'
                             '    return {1: 2}')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        return {1: 2}\n'
            '               ^\n'
            "CompileError: cannot convert dict to '[(string, foo.lib.Foo)]'\n")

    def test_wrong_number_of_function_parameters(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    pass\n'
                             'def bar():\n'
                             '    foo(1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        foo(1)\n'
            '        ^\n'
            "CompileError: expected 0 parameters, got 1\n")

    def test_wrong_function_parameter_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: string):\n'
                             '    pass\n'
                             'def bar():\n'
                             '    foo(True)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        foo(True)\n'
            '            ^\n'
            "CompileError: expected a 'string', got a 'bool'\n")

    def test_wrong_function_parameter_type_trait(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@trait\n'
                             'class Base:\n'
                             '    pass\n'
                             '@trait\n'
                             'class WrongBase:\n'
                             '    pass\n'
                             'class Foo(Base):\n'
                             '    pass\n'
                             'def foo(a: WrongBase):\n'
                             '    pass\n'
                             'def bar():\n'
                             '    foo(Foo())\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 12\n'
            '        foo(Foo())\n'
            '            ^\n'
            "CompileError: 'foo.lib.Foo' does not implement trait "
            "'foo.lib.WrongBase'\n")

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

    def test_compare_i64_and_bool(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return 1 == True')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return 1 == True\n'
            '               ^\n'
            "CompileError: cannot convert 'i64/i32/i16/i8/u64/u32/u16/u8' to 'bool'\n")

    def test_compare_mix_of_literals_and_known_types_1(self):
        source = transpile_source('def foo():\n'
                                  '    k: u64 = 1\n'
                                  '    v: i64 = 1\n'
                                  '    if 0xffffffffffffffff == k:\n'
                                  '        pass\n'
                                  '    print(v)\n')

        self.assert_in('18446744073709551615ull', source)

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

    def test_assign_256_to_u8(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('A: u8 = 256\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    A: u8 = 256\n'
            '            ^\n'
            "CompileError: integer literal out of range for 'u8'\n")

    def test_assign_over_max_to_u64(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('A: u64 = 0x1ffffffffffffffff\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    A: u64 = 0x1ffffffffffffffff\n'
            '             ^\n'
            "CompileError: integer literal out of range for 'u64'\n")

    def test_assign_max_to_i64(self):
        source = transpile_source('A: i64 = 0x7fffffffffffffff\n')

        self.assert_in('i64 A = 9223372036854775807;', source)

    def test_assign_over_max_to_i64(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('A: i64 = 0xffffffffffffffff\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    A: i64 = 0xffffffffffffffff\n'
            '             ^\n'
            "CompileError: integer literal out of range for 'i64'\n")

    def test_assign_float_to_u8(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('A: u8 = 2.0\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    A: u8 = 2.0\n'
            '            ^\n'
            "CompileError: cannot convert float to 'u8'\n")

    def test_global_variables_can_not_be_redefeined(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('A: u8 = 1\n'
                             'A: u8 = 2\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '    A: u8 = 2\n'
            '    ^\n'
            "CompileError: there is already a variable called 'A'\n")

    def test_global_variable_types_can_not_be_inferred(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('a = 2\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    a = 2\n'
            '    ^\n'
            "CompileError: global variable types cannot be inferred\n")

    def test_arithmetics_on_mix_of_literals_and_known_types_5(self):
        source = transpile_source('def foo():\n'
                                  '    k: i32 = -1\n'
                                  '    v: u8 = 1\n'
                                  '    value = ((-1 / 2) - 2 * k)\n'
                                  '    print(value, v)\n')

        self.assert_in('value = ((-1 / 2) - (2 * k));', source)

    def test_assign_negative_number_to_u32(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    k: u32 = -1\n'
                             '    print(k)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        k: u32 = -1\n'
            '                 ^\n'
            "CompileError: integer literal out of range for 'u32'\n")

    def test_assign_positive_number_to_u32(self):
        # Not sure if --1 should be allowed.
        source = transpile_source('def foo():\n'
                                  '    i: u32 = +1\n'
                                  '    j: u32 = --1\n'
                                  '    print(i, j)\n')

        self.assert_in('u32 i = 1;', source)
        self.assert_in('u32 j = 1;', source)

    def test_reassign_negative_number_to_u32(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    i: u32 = 0\n'
                             '    i = -1\n'
                             '    print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        i = -1\n'
            '            ^\n'
            "CompileError: integer literal out of range for 'u32'\n")

    def test_arithmetics_on_mix_of_literals_and_known_types_too_big(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    k: i64 = 1\n'
                             '    value = (0xffffffffffffffff + k)\n'
                             '    print(value)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        value = (0xffffffffffffffff + k)\n'
            '                 ^\n'
            "CompileError: integer literal out of range for 'i64'\n")

    def test_arithmetics_on_mix_of_literals_and_known_types_negative(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    value: u8 = (-1 * 5)\n'
                             '    print(value)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        value: u8 = (-1 * 5)\n'
            '                     ^\n'
            "CompileError: integer literal out of range for 'u8'\n")

    def test_arithmetics_and_compare(self):
        source = transpile_source('def foo():\n'
                                  '    k: i32 = -1\n'
                                  '    if ((-1 / 2) - 2 * k) == k:\n'
                                  '        pass\n')

        self.assert_in('if (Bool(((-1 / 2) - (2 * k)) == k)) {', source)

    def test_change_integer_type(self):
        source = transpile_source('def foo():\n'
                                  '    value = (i8(-1) * i8(u32(5)))\n'
                                  '    print(value)\n')

        self.assert_in('value = (i8(-1) * i8(u32(5)));', source)

    def test_change_integer_type_error(self):
        return
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    value = (i8(-1) * u32(5))\n'
                             '    print(value)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        value = (i8(-1) * u32(5))\n'
            '                 ^\n'
            "CompileError: cannot compare 'i8' and 'u32'\n")

    def test_function_call(self):
        source = transpile_source('def foo(a: i32, b: f32):\n'
                                  '    print(a, b)\n'
                                  'def bar():\n'
                                  '    foo(1, 2.1)\n')

        self.assert_in('foo(1, 2.1);', source)

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

    def test_tuple_unpack_variable_defined_other_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def foo(self) -> (bool, i64):\n'
                             '        return (True, -5)\n'
                             'def foo():\n'
                             '    v = Foo()\n'
                             '    b: string = ""\n'
                             '    a, b = v.foo()\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 7\n'
            '        a, b = v.foo()\n'
            '           ^\n'
            "CompileError: expected a 'string', got a 'i64'\n")

    def test_tuple_unpack_integer(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a, b = 1\n'
                             '    print(a, b)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        a, b = 1\n'
            '               ^\n'
            "CompileError: only tuples can be unpacked\n")

    def test_no_variable_init(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "    a: u8\n"
                             '    a = 1\n'
                             '    print(a)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            "        a: u8\n"
            '        ^\n'
            "CompileError: variables must be initialized when declared\n")

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

    def test_assert_between(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a = 2\n'
                             '    assert 1 <= a < 3\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            "        assert 1 <= a < 3\n"
            '               ^\n'
            "CompileError: can only compare two values\n")

    def test_compare_between(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a = 2\n'
                             '    print(1 <= a < 3)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            "        print(1 <= a < 3)\n"
            '              ^\n'
            "CompileError: can only compare two values\n")

    def test_iterate_over_tuple(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i in (5, 1):\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i in (5, 1):\n'
            '                 ^\n'
            "CompileError: iteration over tuples not allowed\n")

    def test_iterate_over_enumerate_not_tuple(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    values: [u32] = [3, 8]\n'
                             '    for i in enumerate(values):\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        for i in enumerate(values):\n'
            '            ^\n'
            "CompileError: can only unpack enumerate into two variables, got 1\n")

    def test_iterate_over_slice_with_different_types_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i in slice([1], 1, u16(2)):\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i in slice([1], 1, u16(2)):\n'
            '                               ^\n'
            "CompileError: types 'u16' and 'i64' differs\n")

    def test_iterate_over_slice_with_different_types_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i in slice(range(4), 1, 2, i8(-1)):\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i in slice(range(4), 1, 2, i8(-1)):\n'
            '                                       ^\n'
            "CompileError: types 'i8' and 'i64' differs\n")

    def test_iterate_over_slice_no_params(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i in slice(range(2)):\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i in slice(range(2)):\n'
            '                 ^\n'
            "CompileError: expected 2 to 4 parameters, got 1\n")

    def test_iterate_over_range_with_different_types_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i in range(i8(1), u16(2)):\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i in range(i8(1), u16(2)):\n'
            '                              ^\n'
            "CompileError: types 'u16' and 'i8' differs\n")

    def test_iterate_over_range_with_different_types_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i in range(1, i8(2), 2):\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i in range(1, i8(2), 2):\n'
            '                          ^\n'
            "CompileError: types 'i8' and 'i64' differs\n")

    def test_iterate_over_range_with_too_many_parameters(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i in range(1, 2, 2, 2):\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i in range(1, 2, 2, 2):\n'
            '                 ^\n'
            "CompileError: expected 1 to 3 parameters, got 4\n")

    def test_iterate_over_range_string(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i in range("a"):\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i in range("a"):\n'
            '                       ^\n'
            "CompileError: parameter type must be an integer, not 'string'\n")

    def test_iterate_over_enumerate_string(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i, j in enumerate(range(2), ""):\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i, j in enumerate(range(2), ""):\n'
            '                                        ^\n'
            "CompileError: initial value must be an integer, not 'string'\n")

    def test_iterate_over_enumerate_no_parameters(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i, j in enumerate():\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i, j in enumerate():\n'
            '                    ^\n'
            "CompileError: expected 1 or 2 parameters, got 0\n")

    def test_iterate_over_zip_wrong_unpack(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i in zip(range(2), range(2)):\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i in zip(range(2), range(2)):\n'
            '            ^\n'
            "CompileError: cannot unpack 2 values into 1\n")

    def test_iterate_over_reversed_no_parameter(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i in reversed():\n'
                             '        print(i)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for i in reversed():\n'
            '                 ^\n'
            "CompileError: expected 1 parameter, got 0\n")

    def test_type_error_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a: u16 = 1\n'
                             '    b: u32 = 1\n'
                             '    c = b - a\n'
                             '    print(c)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        c = b - a\n'
            '            ^\n'
            "CompileError: types 'u32' and 'u16' differs\n")

    def test_type_error_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: i64):\n'
                             '    b: u64 = a\n'
                             '    print(b)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        b: u64 = a\n'
            '                 ^\n'
            "CompileError: expected a 'u64', got a 'i64'\n")

    def test_type_error_3(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def bar() -> string:\n'
                             '    return ""\n'
                             'def foo():\n'
                             '    b: u64 = bar()\n'
                             '    print(b)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        b: u64 = bar()\n'
            '                 ^\n'
            "CompileError: expected a 'u64', got a 'string'\n")

    def test_type_error_4(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a: u32 = 1\n'
                             '    b = a - [1]\n'
                             '    print(b)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        b = a - [1]\n'
            '            ^\n'
            "CompileError: types 'u32' and '[i64]' differs\n")

    def test_type_error_4(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a: u32 = [1.0]\n'
                             '    print(a)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        a: u32 = [1.0]\n'
            '                 ^\n'
            "CompileError: cannot convert list to 'u32'\n")

    def test_type_error_5(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return\n'
            '        ^\n'
            "CompileError: return value missing\n")

    def test_type_error_6(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    return 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return 1\n'
            '               ^\n'
            "CompileError: function does not return any value\n")

    def test_compare_wrong_types_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return 1 == [""]\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return 1 == [""]\n'
            '               ^\n'
            "CompileError: cannot convert 'i64/i32/i16/i8/u64/u32/u16/u8' to "
            "'[string]'\n")

    def test_compare_wrong_types_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return [""] in 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return [""] in 1\n'
            '                       ^\n'
            "CompileError: not an iterable\n")

    def test_compare_wrong_types_3(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return [""] not in 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return [""] not in 1\n'
            '                           ^\n'
            "CompileError: not an iterable\n")

    def test_compare_wrong_types_4(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return 2.0 == 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return 2.0 == 1\n'
            '               ^\n'
            "CompileError: cannot convert 'f64/f32' to "
            "'i64/i32/i16/i8/u64/u32/u16/u8'\n")

    def test_compare_wrong_types_5(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return 1.0 == [""]\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return 1.0 == [""]\n'
            '               ^\n'
            "CompileError: cannot convert 'f64/f32' to '[string]'\n")

    def test_compare_wrong_types_6(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: i32) -> bool:\n'
                             '    return a in [""]\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return a in [""]\n'
            '               ^\n'
            "CompileError: types 'i32' and 'string' differs\n")

    def test_compare_wrong_types_7(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: i32) -> bool:\n'
                             '    return a in a\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return a in a\n'
            '                    ^\n'
            "CompileError: not an iterable\n")

    def test_compare_wrong_types_8(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: i32) -> bool:\n'
                             '    return 1 in a\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return 1 in a\n'
            '                    ^\n'
            "CompileError: not an iterable\n")

    def test_compare_wrong_types_9(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: i32) -> bool:\n'
                             '    return "" == a\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return "" == a\n'
            '               ^\n'
            "CompileError: types 'string' and 'i32' differs\n")

    def test_compare_wrong_types_10(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(1 is None)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(1 is None)\n'
            '                   ^\n'
            "CompileError: 'i64' cannot be None\n")

    def test_compare_wrong_types_11(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(1.0 is None)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(1.0 is None)\n'
            '                     ^\n'
            "CompileError: 'f64' cannot be None\n")

    def test_compare_wrong_types_12(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: i32):\n'
                             '    print(a is None)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(a is None)\n'
            '              ^\n'
            "CompileError: 'i32' cannot be None\n")

    def test_compare_wrong_types_13(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: i32):\n'
                             '    print(None is a)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(None is a)\n'
            '              ^\n'
            "CompileError: 'i32' cannot be None\n")

    def test_compare_wrong_types_14(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(True is None)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(True is None)\n'
            '              ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_compare_wrong_types_15(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: bool):\n'
                             '    print(None is a)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(None is a)\n'
            '              ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_compare_wrong_types_16(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: bool):\n'
                             '    print(a is not 1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(a is not 1)\n'
            '              ^\n'
            "CompileError: cannot convert 'bool' to 'i64/i32/i16/i8/u64/u32/u16/u8'\n")

    def test_compare_wrong_types_17(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(None in [1, 5])\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(None in [1, 5])\n'
            '              ^\n'
            "CompileError: 'i64' cannot be None\n")

    def test_compare_wrong_types_18(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(None == "")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(None == "")\n'
            '              ^\n'
            "CompileError: use 'is' and 'is not' to compare to None\n")

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

    def test_compare_wrong_types_20(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    if (1, ("", True)) == (1, ("", 1)):\n'
                             '        pass\n')

        # ToDo: Marker in wrong place.
        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        if (1, ("", True)) == (1, ("", 1)):\n'
            '           ^\n'
            "CompileError: cannot convert 'bool' to 'i64/i32/i16/i8/u64/u32/u16/u8'\n")

    def test_bool_op_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    if True or None:\n'
                             '        pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            "        if True or None:\n"
            '                   ^\n'
            "CompileError: None is not a 'bool'\n")

    def test_bool_op_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    if True or False and 1:\n'
                             '        pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            "        if True or False and 1:\n"
            '                             ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

    def test_while_non_bool(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    while 1:\n'
                             '        pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            "        while 1:\n"
            '              ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

    def test_inferred_type_none(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a = None\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            "        a = None\n"
            '        ^\n'
            "CompileError: cannot infer type from None\n")

    def test_docstring(self):
        source = transpile_source('def foo():\n'
                                  '    "Hi!"\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '}\n',
                       source)

    def test_docstring_embedded_cpp(self):
        source = transpile_source('def foo():\n'
                                  '    "mys-embedded-c++ print();"\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    /* mys-embedded-c++ start */\n'
                       '    print();\n'
                       '    /* mys-embedded-c++ stop */;\n'
                       '}\n',
                       source)

    def test_global_integer_out_of_range(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('V: i8 = 1000\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            "    V: i8 = 1000\n"
            '            ^\n'
            "CompileError: integer literal out of range for 'i8'\n")

    def test_global_wrong_value_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('V: i8 = ""\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    V: i8 = ""\n'
            '            ^\n'
            "CompileError: expected a 'i8', got a 'string'\n")

    def test_global_undefined_variable(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('V: i8 = (1 << K)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    V: i8 = (1 << K)\n'
            '                  ^\n'
            "CompileError: undefined variable 'K'\n")

    def test_global_use_variable_of_wrong_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('K: u8 = 1\n'
                             'V: i8 = (1 << K)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '    V: i8 = (1 << K)\n'
            '             ^\n'
            "CompileError: expected a 'i8', got a 'u8'\n")

    def test_global_string(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('"Hello!"\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    "Hello!"\n'
            '    ^\n'
            "CompileError: syntax error\n")

    def test_global_integer(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    1\n'
            '    ^\n'
            "CompileError: syntax error\n")

    def test_enum(self):
        source = transpile_source('@enum\n'
                                  'class Foo:\n'
                                  '    A = 1\n'
                                  '    B = 2\n'
                                  '    C = 3\n'
                                  '    D = 100\n'
                                  '    E = 200\n')

        self.assert_in(
            'enum class Foo : i64 {\n'
            '    A = 1,\n'
            '    B = 2,\n'
            '    C = 3,\n'
            '    D = 100,\n'
            '    E = 200,\n'
            '};\n',
            source)

    def test_enum_float_value(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A = 1\n'
                             'def foo():\n'
                             '    print(Foo(0.0))\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        print(Foo(0.0))\n'
            '                  ^\n'
            "CompileError: cannot convert float to 'i64'\n")

    def test_enum_too_many_parameters(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A = 1\n'
                             'def foo():\n'
                             '    print(Foo(1, 2))\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        print(Foo(1, 2))\n'
            '              ^\n'
            "CompileError: expected 1 parameter, got 2\n")

    def test_assign_to_wrong_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a = 1\n'
                             '    a = ""\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        a = ""\n'
            '            ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_format_string_i8_u8(self):
        source = transpile_source('def foo():\n'
                                  '    print(f"{i8(1)} {u8(1)} {u16(1)}")\n')

        self.assert_in('String((int)i8(1))', source)
        self.assert_in('String((unsigned)u8(1))', source)
        self.assert_in('String(u16(1))', source)

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

    def test_min_wrong_types(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(min(u8(1), u8(2), i8(2)))\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(min(u8(1), u8(2), i8(2)))\n'
            '                                ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_min_no_args(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(min())\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(min())\n'
            '              ^\n'
            "CompileError: expected at least one parameter\n")

    def test_min_wrong_return_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    assert min(1, 2) == i8(1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        assert min(1, 2) == i8(1)\n'
            '               ^\n'
            "CompileError: types 'i64' and 'i8' differs\n")

    def test_max_wrong_types(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(max(i8(1), i8(2), u8(2)))\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(max(i8(1), i8(2), u8(2)))\n'
            '                                ^\n'
            "CompileError: expected a 'i8', got a 'u8'\n")

    def test_max_no_args(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(max())\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(max())\n'
            '              ^\n'
            "CompileError: expected at least one parameter\n")

    def test_max_wrong_return_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    assert max(u8(1), 2) == i8(1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        assert max(u8(1), 2) == i8(1)\n'
            '               ^\n'
            "CompileError: types 'u8' and 'i8' differs\n")

    def test_len_no_params(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(len())\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(len())\n'
            '              ^\n'
            "CompileError: expected 1 parameter, got 0\n")

    def test_len_two_params(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(len(1, 2))\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(len(1, 2))\n'
            '              ^\n'
            "CompileError: expected 1 parameter, got 2\n")

    def test_len_compare_to_non_u64(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    assert len("") == i8(0)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        assert len("") == i8(0)\n'
            '               ^\n'
            "CompileError: types 'u64' and 'i8' differs\n")

    def test_str_compare_to_non_string(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    assert str(0) == i8(0)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        assert str(0) == i8(0)\n'
            '               ^\n'
            "CompileError: types 'string' and 'i8' differs\n")

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

    def test_unknown_local_variable_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a: u9 = 0\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        a: u9 = 0\n'
            '           ^\n'
            "CompileError: undefined type 'u9'\n")

    def test_unknown_global_variable_type_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('A: i9 = 0\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    A: i9 = 0\n'
            '       ^\n'
            "CompileError: undefined type 'i9'\n")

    def test_unknown_global_variable_type_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('A: [(bool, i9)] = None\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    A: [(bool, i9)] = None\n'
            '       ^\n'
            "CompileError: undefined type '[(bool, i9)]'\n")

    def test_unknown_global_variable_type_3(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('A: i10 = a\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    A: i10 = a\n'
            '       ^\n'
            "CompileError: undefined type 'i10'\n")

    def test_tuple_index_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a = 1\n'
                             '    v = (1, "b")\n'
                             '    print(v[a])\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(v[a])\n'
            '                ^\n'
            "CompileError: tuple indexes must be compile time known integers\n")

    def test_tuple_index_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v = (1, "b")\n'
                             '    print(v[1 / 2])\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        print(v[1 / 2])\n'
            '                ^\n'
            "CompileError: tuple indexes must be compile time known integers\n")

    def test_tuple_item_assign_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v = (1, "b")\n'
                             '    v[0] = "ff"\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        v[0] = "ff"\n'
            '               ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_tuple_item_assign_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a, b, c = (1, "b")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        a, b, c = (1, "b")\n'
            '        ^\n'
            "CompileError: expected 3 values to unpack, got 2\n")

    def test_return_nones_as_bool_in_tuple(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> (bool, bool):\n'
                             '    return (None, None)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return (None, None)\n'
            '                ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_return_wrong_integer_in_tuple(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> (bool, u8, string):\n'
                             '    return (True, i8(1), "")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return (True, i8(1), "")\n'
            '                      ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_return_wrong_list_type_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> [u8]:\n'
                             '    return [i8(1), -1]\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return [i8(1), -1]\n'
            '                ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_return_wrong_list_type_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> [u8]:\n'
                             '    return [1, i8(-1)]\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return [1, i8(-1)]\n'
            '                   ^\n'
            "CompileError: expected a 'u8', got a 'i8'\n")

    def test_return_none_as_bool(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return None\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return None\n'
            '               ^\n'
            "CompileError: 'bool' cannot be None\n")

    def test_assign_none_to_i32(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('A: i32 = None\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    A: i32 = None\n'
            '             ^\n'
            "CompileError: 'i32' cannot be None\n")

    def test_return_short_tuple(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> (bool, bool):\n'
                             '    return (True, )\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return (True, )\n'
            '               ^\n'
            "CompileError: expected a '(bool, bool)', got a '(bool, )'\n")

    def test_wrong_dict_key_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v = {1: 5}\n'
                             '    v["a"] = 4\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        v["a"] = 4\n'
            '          ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_bad_dict_key_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v: {Foo: bool} = None\n')

        # Should probably say that Foo is not defined.
        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        v: {Foo: bool} = None\n'
            '           ^\n'
            "CompileError: undefined type '{Foo: bool}'\n")

    def test_dict_value_type_not_defined(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v: {bool: Foo} = None\n')

        # Should probably say that Foo is not defined.
        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        v: {bool: Foo} = None\n'
            '           ^\n'
            "CompileError: undefined type '{bool: Foo}'\n")

    def test_wrong_dict_value_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v = {1: 5}\n'
                             '    v[2] = 2.5\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        v[2] = 2.5\n'
            '               ^\n'
            "CompileError: cannot convert float to 'i64'\n")

    def test_dict_init_key_types_mismatch_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v: {i64: i64} = {1: 5, True: 0}\n'
                             '    print(v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        v: {i64: i64} = {1: 5, True: 0}\n'
            '                               ^\n'
            "CompileError: expected a 'i64', got a 'bool'\n")

    def test_dict_init_key_types_mismatch_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v = {True: 5, 1: 4}\n'
                             '    print(v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        v = {True: 5, 1: 4}\n'
            '                      ^\n'
            "CompileError: cannot convert integer to 'bool'\n")

    def test_dict_init_value_types_mismatch_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v: {bool: i64} = {True: 5, False: "a"}\n'
                             '    print(v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        v: {bool: i64} = {True: 5, False: "a"}\n'
            '                                          ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_dict_class_key_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    pass\n'
                             'def foo():\n'
                             '    v: {Foo: i64} = {}\n'
                             '    print(v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        v: {Foo: i64} = {}\n'
            '                        ^\n'
            "CompileError: invalid key type\n")

    def test_dict_init_value_types_mismatch_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v = {True: i8(5), False: u8(4)}\n'
                             '    print(v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        v = {True: i8(5), False: u8(4)}\n'
            '                                 ^\n'
            "CompileError: expected a 'i8', got a 'u8'\n")

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

    def test_tuple_index_out_of_range(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v = ("", 1)\n'
                             '    print(v[2])\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        print(v[2])\n'
            '                ^\n'
            "CompileError: tuple index out of range\n")

    def test_assign_to_function_call(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def bar() -> i32:\n'
                             '    return 1\n'
                             'def foo():\n'
                             '    bar() = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<string>", line 4\n'
            '    bar() = 1\n'
            '    ^\n'
            "SyntaxError: cannot assign to function call\n")

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

    def test_call_iter_functions_outside_for(self):
        # At least true for now...
        for name in ['range', 'enumerate', 'zip', 'slice', 'reversed']:
            with self.assertRaises(Exception) as cm:
                transpile_source('def foo():\n'
                                 f'    v = {name}([1, 4])\n'
                                 '    print(v)')

            self.assertEqual(
                remove_ansi(str(cm.exception)),
                '  File "", line 2\n'
                f'        v = {name}([1, 4])\n'
                '            ^\n'
                "CompileError: function can only be used in for-loops\n")

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

    def test_list_of_integer(self):
        with self.assertRaises(Exception) as cm:
            source = transpile_source('def foo():\n'
                                      '    a = list("")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        a = list("")\n'
            '            ^\n'
            "CompileError: list('string') not supported\n")

    def test_class_member_list_two_types(self):
        with self.assertRaises(Exception) as cm:
            source = transpile_source('class Foo:\n'
                                      '    a: [i32, u32]\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        a: [i32, u32]\n'
            '           ^\n'
            "CompileError: expected 1 type in list, got 2\n")

    def test_trait_init(self):
        with self.assertRaises(Exception) as cm:
            source = transpile_source('@trait\n'
                                      'class Foo:\n'
                                      '    def __init__(self):\n'
                                      '        pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        def __init__(self):\n'
            '        ^\n'
            "CompileError: traits cannot have an __init__ method\n")

    def test_trait_method_not_implemented_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@trait\n'
                             'class Base:\n'
                             '    def foo(self):\n'
                             '        pass\n'
                             'class Foo(Base):\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '    class Foo(Base):\n'
            '              ^\n'
            "CompileError: trait method 'foo' is not implemented\n")

    def test_trait_method_not_implemented_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@trait\n'
                             'class Base:\n'
                             '    def foo(self):\n'
                             '        "Doc"\n'
                             'class Foo(Base):\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '    class Foo(Base):\n'
            '              ^\n'
            "CompileError: trait method 'foo' is not implemented\n")

    # ToDo
    # def test_imported_traits_method_not_implemented(self):
    #     with self.assertRaises(Exception) as cm:
    #         transpile([
    #             Source('@trait\n'
    #                    'class Base:\n'
    #                    '    def foo(self):\n'
    #                    '        pass\n',
    #                    module='foo.lib'),
    #             Source('from foo import Base\n'
    #                    'class Foo(Base):\n'
    #                    '    pass\n')
    #         ])
    #
    #     self.assertEqual(
    #         remove_ansi(str(cm.exception)),
    #         '  File "", line 2\n'
    #         '    class Foo(Base):\n'
    #         '              ^\n'
    #         "CompileError: trait method 'foo' is not implemented\n")

    def test_trait_member_access(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@trait\n'
                             'class Base:\n'
                             '    pass\n'
                             'def foo(v: Base):\n'
                             '    v.a = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        v.a = 1\n'
            '        ^\n'
            "CompileError: 'Base' has no member 'a'\n")

    def test_string_member_access(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(v: string):\n'
                             '    v.a = 1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        v.a = 1\n'
            '        ^\n'
            "CompileError: 'string' has no member 'a'\n")

    def test_main_in_non_main_file(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main():\n'
                             '    pass\n')

        self.assertEqual(str(cm.exception), 'main() is only allowed in main.mys')

    def test_no_main_in_main_file(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    pass\n',
                             has_main=True)

        self.assertEqual(str(cm.exception), 'main() not found in main.mys')

    def test_bad_char_literal(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "    print('foo')\n")

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            "        print('foo')\n"
            "              ^\n"
            'CompileError: bad character literal\n')

    def test_string_to_utf8_too_many_parameters(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    "".to_utf8(1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        "".to_utf8(1)\n'
            "        ^\n"
            'CompileError: expected 0 parameters, got 1\n')

    def test_string_upper_too_many_parameters(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    "".upper(1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        "".upper(1)\n'
            "        ^\n"
            'CompileError: expected 0 parameters, got 1\n')

    def test_string_lower_too_many_parameters(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    "".lower(1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        "".lower(1)\n'
            "        ^\n"
            'CompileError: expected 0 parameters, got 1\n')

    def test_string_bad_method(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    "".foobar()\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        "".foobar()\n'
            "        ^\n"
            'CompileError: string method not implemented\n')

    def test_trait_member_access(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def foo(self, v: bool):\n'
                             '        pass\n'
                             'def foo(v: Foo):\n'
                             '    v.foo()\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        v.foo()\n'
            '        ^\n'
            "CompileError: expected 1 parameter, got 0\n")

    def test_call_void(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    pass\n'
                             'def bar():\n'
                             '    foo().bar()\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        foo().bar()\n'
            '        ^\n'
            "CompileError: None has no methods\n")

    def test_call_void(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    pass\n'
                             'def bar():\n'
                             '    print(foo())\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(foo())\n'
            '              ^\n'
            "CompileError: None cannot be printed\n")

    def test_value_if_cond_else_value_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(1 if 1 else 2)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(1 if 1 else 2)\n'
            '                   ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

    def test_value_if_cond_else_value_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(1 if True else "")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(1 if True else "")\n'
            '                             ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_list_comprehension(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print([v for v in ""])\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print([v for v in ""])\n'
            '              ^\n'
            "CompileError: list comprehension is not implemented\n")

    def test_if_cond_as_non_bool(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    if 1:\n'
                             '        pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        if 1:\n'
            '           ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

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

    def test_wrong_trait_method_parameter_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@trait\n'
                             'class Foo:\n'
                             '    def foo(self, v: bool):\n'
                             '        pass\n'
                             'def foo(v: Foo):\n'
                             '    v.foo(b"")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 6\n'
            '        v.foo(b"")\n'
            '              ^\n'
            "CompileError: expected a 'bool', got a 'bytes'\n")

    def test_bare_compare(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    1 == 2\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        1 == 2\n'
            '        ^\n'
            "CompileError: bare comparision\n")

    def test_bare_integer(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        1\n'
            '        ^\n'
            "CompileError: bare integer\n")

    def test_bare_float(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    2.0\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        2.0\n'
            '        ^\n'
            "CompileError: bare float\n")

    def test_bare_not(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    not True\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        not True\n'
            '        ^\n'
            "CompileError: bare unary operation\n")

    def test_bare_add(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    1 + 2\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        1 + 2\n'
            '        ^\n'
            "CompileError: bare binary operation\n")

    def test_bare_name(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a: i32 = 0\n'
                             '    a\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        a\n'
            '        ^\n'
            "CompileError: bare name\n")

    def test_bare_name_in_if(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a: i32 = 0\n'
                             '    if True:\n'
                             '        a\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_bare_name_in_else(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a: i32 = 0\n'
                             '    if True:\n'
                             '        pass\n'
                             '    else:\n'
                             '        a\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 6\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_bare_integer_in_try(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        a\n'
                             '    except:\n'
                             '        pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_bare_integer_in_except(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        pass\n'
                             '    except:\n'
                             '        a\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_bare_integer_in_match_case(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: u8):\n'
                             '    match a:\n'
                             '        case 1:\n'
                             '            1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '                1\n'
            '                ^\n'
            "CompileError: bare integer\n")

    def test_bare_integer_in_while(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    while True:\n'
                             '        1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '            1\n'
            '            ^\n'
            "CompileError: bare integer\n")

    def test_bare_integer_in_for(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for i in "":\n'
                             '        1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '            1\n'
            '            ^\n'
            "CompileError: bare integer\n")

    def test_not_only_allowed_on_bool(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(not "hi")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(not "hi")\n'
            '                  ^\n'
            "CompileError: expected a 'bool', got a 'string'\n")

    def test_negative_bool(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(-True)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(-True)\n'
            '              ^\n'
            "CompileError: unary '-' can only operate on numbers\n")

    def test_positive_string(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(+"hi")\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(+"hi")\n'
            '              ^\n'
            "CompileError: unary '+' can only operate on numbers\n")

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

    def test_not_enum(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A = 1\n'
                             'def foo():\n'
                             '    print(not Foo.A)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        print(not Foo.A)\n'
            '                  ^\n'
            "CompileError: expected a 'bool', got a 'foo.lib.Foo'\n")

    def test_enum_member_value_lower_than_previous_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A = 0\n'
                             '    B = -1\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        B = -1\n'
            '            ^\n'
            "CompileError: enum member value lower than for previous member\n")

    def test_enum_member_value_lower_than_previous_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A\n'
                             '    B\n'
                             '    C = 0\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        C = 0\n'
            '            ^\n'
            "CompileError: enum member value lower than for previous member\n")

    def test_enum_pascal_case(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class foo:\n'
                             '    A\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '    class foo:\n'
            '    ^\n'
            "CompileError: enum names must be pascal case\n")

    def test_enum_bad_member_syntax(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    def a(self):\n'
                             '        pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        def a(self):\n'
            '        ^\n'
            "CompileError: invalid enum member syntax\n")

    def test_trait_pascal_case(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@trait\n'
                             'class foo:\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '    class foo:\n'
            '    ^\n'
            "CompileError: trait names must be pascal case\n")

    def test_variable_defined_in_if_can_not_be_used_after(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    if True:\n'
                             '        v = 1\n'
                             '    print(v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(v)\n'
            '              ^\n'
            "CompileError: undefined variable 'v'\n")

    def test_variable_defined_in_while_can_not_be_used_after(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    while False:\n'
                             '        v = 1\n'
                             '    print(v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(v)\n'
            '              ^\n'
            "CompileError: undefined variable 'v'\n")

    def test_variable_defined_in_while_can_not_be_used_after(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    l: [bool] = []\n'
                             '    for _ in l:\n'
                             '        v = 1\n'
                             '    print(v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        print(v)\n'
            '              ^\n'
            "CompileError: undefined variable 'v'\n")

    def test_define_empty_list_without_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v = []\n'
                             '    print(v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        v = []\n'
            '        ^\n'
            "CompileError: cannot infer type from empty list\n")

    def test_define_empty_dict_without_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    v = {}\n'
                             '    print(v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        v = {}\n'
            '        ^\n'
            "CompileError: cannot infer type from empty dict\n")

    def test_if_else_different_variable_type_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    if False:\n'
                             '        x: i8 = 1\n'
                             '    else:\n'
                             '        x: i16 = 2\n'
                             '    print(x)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 6\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_if_else_different_variable_type_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    if False:\n'
                             '        x = 1\n'
                             '    elif True:\n'
                             '        x = 2\n'
                             '    else:\n'
                             '        if True:\n'
                             '            x = ""\n'
                             '        else:\n'
                             '            x = 3\n'
                             '    print(x)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 11\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_try_except_different_variable_type_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        x = 1\n'
                             '    except:\n'
                             '        x = ""\n'
                             '    print(x)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 6\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_try_except_different_variable_type_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        x = 1\n'
                             '    except GeneralError:\n'
                             '        x = ""\n'
                             '    except ValueError:\n'
                             '        x = 2\n'
                             '    print(x)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 8\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_try_except_missing_branch(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        x = 1\n'
                             '    except GeneralError:\n'
                             '        pass\n'
                             '    except ValueError:\n'
                             '        x = 2\n'
                             '    print(x)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 8\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_all_branches_different_variable_type_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    try:\n'
                             '        if False:\n'
                             '            x = 1\n'
                             '        else:\n'
                             '            x = 2\n'
                             '    except GeneralError:\n'
                             '        try:\n'
                             '            x = 3\n'
                             '        except:\n'
                             '            if True:\n'
                             '                x: u8 = 4\n'
                             '            else:\n'
                             '                x = 5\n'
                             '    print(x)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 15\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_named_parameter_wrong_name(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: bool):\n'
                             '    print(a)\n'
                             'def bar():\n'
                             '    foo(b=True)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        foo(b=True)\n'
            '            ^\n'
            "CompileError: invalid parameter 'b'\n")

    def test_named_parameter_twice(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: bool, b: i64):\n'
                             '    print(a, b)\n'
                             'def bar():\n'
                             '    foo(b=True, b=1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        foo(b=True, b=1)\n'
            '                    ^\n'
            "CompileError: parameter 'b' given more than once\n")

    def test_both_regular_and_named_parameter(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: bool):\n'
                             '    print(a)\n'
                             'def bar():\n'
                             '    foo(True, a=True)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        foo(True, a=True)\n'
            '        ^\n'
            "CompileError: expected 1 parameter, got 2\n")

    def test_named_parameter_before_regular(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: bool, b: i64):\n'
                             '    print(a, b)\n'
                             'def bar():\n'
                             '    foo(a=True, 1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<string>", line 4\n'
            '    foo(a=True, 1)\n'
            '                 ^\n'
            "SyntaxError: positional argument follows keyword argument\n")

    def test_only_iterate_over_dict_pairs_supported(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for item in {1: 2}:\n'
                             '        print(item)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for item in {1: 2}:\n'
            '            ^\n'
            "CompileError: iteration over dict must be done on key/value tuple\n")

    def test_fail_to_redefine_method_call_variable_in_for_loop_for_now_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def foo(self) -> [string]:\n'
                             '        return []\n'
                             'def foo(a: bool):\n'
                             '    for a in Foo().foo():\n'
                             '        print(a)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        for a in Foo().foo():\n'
            '            ^\n'
            "CompileError: redefining variable 'a'\n")

    def test_fail_to_redefine_method_call_variable_in_for_loop_for_now_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def foo(self) -> [(string, u8)]:\n'
                             '        return []\n'
                             'def foo(b: bool):\n'
                             '    for a, b in Foo().foo():\n'
                             '        print(a, b)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        for a, b in Foo().foo():\n'
            '               ^\n'
            "CompileError: redefining variable 'b'\n")

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

    def test_name_clash(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def bar():\n'
                             '    pass\n'
                             'def foo():\n'
                             '    bar = 1\n'
                             '    print(bar)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        bar = 1\n'
            '        ^\n'
            "CompileError: redefining 'bar'\n")

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

    def test_import_after_function_definition(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    pass\n'
                             'from bar import fie\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '    from bar import fie\n'
            '    ^\n'
            "CompileError: imports must be at the beginning of the file\n")

    def test_import_after_variable_definition(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('V: bool = True\n'
                             'from bar import fie\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '    from bar import fie\n'
            '    ^\n'
            "CompileError: imports must be at the beginning of the file\n")

    def test_import_after_import(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('import bar\n'
                             'from bar import fie\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    import bar\n'
            '    ^\n'
            "CompileError: only 'from <module> import ...' is allowed\n")

    def test_trait_member(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@trait\n'
                             'class Foo:\n'
                             '    x: i32\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        x: i32\n'
            '        ^\n'
            "CompileError: traits cannot have members\n")

    def test_inline_constant_default_bool_parameter_value(self):
        source = transpile_source('def foo(a: bool = True):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(Bool(true))', source)

    def test_inline_constant_default_u8_parameter_value(self):
        source = transpile_source('def foo(a: u8 = 1):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(1)', source)

    def test_inline_constant_default_i8_parameter_value(self):
        source = transpile_source('def foo(a: i8 = -1):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(-1)', source)

    def test_inline_constant_default_f64_parameter_value(self):
        source = transpile_source('def foo(a: f64 = 5.1):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(5.1)', source)

    def test_inline_constant_default_string_parameter_value(self):
        source = transpile_source('def foo(a: string = "hi"):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(String("hi"))', source)

    def test_inline_constant_default_class_parameter_value_none(self):
        source = transpile_source('class Foo:\n'
                                  '    pass\n'
                                  'def foo(a: Foo = None):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(nullptr)', source)

    def test_inline_constant_default_tuple_parameter_value_none(self):
        source = transpile_source('def foo(a: (i8, string) = None):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(nullptr)', source)

    def test_not_inline_constant_default_class_parameter_value_not_none(self):
        source = transpile_source('class Foo:\n'
                                  '    pass\n'
                                  'def foo(a: Foo = Foo()):\n'
                                  '    pass\n'
                                  'def bar():\n'
                                  '    foo()\n')

        self.assert_in('foo(foo::lib::foo_a_default())', source)

    def test_aug_assign_wrong_integer_types(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    x: i32 = 0\n'
                             '    x += i8(1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        x += i8(1)\n'
            '             ^\n'
            "CompileError: expected a 'i32', got a 'i8'\n")

    def test_embedded_cpp_instead_of_docstring(self):
        source = transpile_source('class Foo:\n'
                                  '    def foo(self):\n'
                                  '        "mys-embedded-c++ // nothing 1"\n'
                                  'def bar():\n'
                                  '    "mys-embedded-c++ // nothing 2"\n')

        self.assert_in('// nothing 1', source)
        self.assert_in('// nothing 2', source)

    def test_list_with_two_types(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('VAR: [bool, bool] = None\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    VAR: [bool, bool] = None\n'
            '         ^\n'
            "CompileError: expected 1 type in list, got 2\n")

    def test_complex(self):
        # complex may be implemented at some point.
        with self.assertRaises(Exception) as cm:
            transpile_source('VAR: complex = 1 + 2j\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    VAR: complex = 1 + 2j\n'
            '         ^\n'
            "CompileError: undefined type 'complex'\n")
