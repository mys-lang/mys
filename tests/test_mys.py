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

def transpile_source(source, filename='', module_hpp=''):
    return transpile([Source(source,
                             filename=filename,
                             module_hpp=module_hpp)])[0][1]


class MysTest(unittest.TestCase):

    maxDiff = None

    def assert_equal_to_file(self, actual, expected):
        # open(expected, 'w').write(actual)
        self.assertEqual(read_file(expected), actual)

    def assert_in(self, needle, haystack):
        try:
            self.assertIn(needle, haystack)
        except AssertionError:
            differ = difflib.Differ()
            diff = differ.compare(needle.splitlines(), haystack.splitlines())

            raise AssertionError(
                '\n' + '\n'.join([diffline.rstrip('\n') for diffline in diff]))

    def test_all(self):
        datas = [
            'basics'
        ]

        for data in datas:
            header, source = transpile([
                Source(read_file(f'tests/files/{data}.mys'),
                       filename=f'{data}.mys',
                       module_hpp=f'{data}.mys.hpp')
            ])[0]
            self.assert_equal_to_file(
                header,
                f'tests/files/{data}.mys.hpp')
            self.assert_equal_to_file(
                source,
                f'tests/files/{data}.mys.cpp')

    def test_invalid_main_argument(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main(argv: i32): pass')

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "", line 1\n'
                         '    def main(argv: i32): pass\n'
                         '    ^\n'
                         "CompileError: main() takes 'argv: [string]' or no arguments\n")

    def test_invalid_main_return_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main() -> i32: pass')

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "", line 1\n'
                         '    def main() -> i32: pass\n'
                         '    ^\n'
                         "CompileError: main() must not return any value\n")

    def test_return_nothing_in_main(self):
        source = transpile_source('def main():\n'
                                  '    return\n')

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
                             filename='foo.py')

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "foo.py", line 1\n'
                         '    def main(): print((lambda x: x)(1))\n'
                         '                       ^\n'
                         'CompileError: lambda functions are not supported\n')

    def test_bad_syntax(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('DEF main(): pass', filename='<unknown>')

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "<unknown>", line 1\n'
                         '    DEF main(): pass\n'
                         '        ^\n'
                         'SyntaxError: invalid syntax\n')

    def test_import_in_function_should_fail(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main():\n'
                             '    import foo\n',
                             filename='<unknown>')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<unknown>", line 2\n'
            '        import foo\n'
            '        ^\n'
            'CompileError: imports are only allowed on module level\n')

    def test_import_from_in_function_should_fail(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main():\n'
                             '    from foo import bar\n')

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
            'CompileError: use from ... import ...\n')

    def test_class_in_function_should_fail(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main():\n'
                             '    class A:\n'
                             '        pass\n',
                             filename='<unknown>')

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
                             filename='<unknown>')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<unknown>", line 1\n'
            '    from foo import bar, fie\n'
            '    ^\n'
            'CompileError: only one import is allowed, found 2\n')

    def test_relative_import_outside_package(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('from .. import fie\n',
                             filename='src/mod.mys',
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
                                 filename='src/mod.mys',
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
                                  '    print("Hi!")\n')

        self.assert_in('std::cout << "Hi!" << std::endl;', source)

    def test_print_function_with_end(self):
        source = transpile_source('def main():\n'
                                  '    print("Hi!", end="")\n')

        self.assert_in('std::cout << "Hi!" << "";', source)

    def test_print_function_with_flush_true(self):
        source = transpile_source('def main():\n'
                                  '    print("Hi!", flush=True)\n')

        self.assert_in('    std::cout << "Hi!" << std::endl;\n'
                       '    if (Bool(true)) {\n'
                       '        std::cout << std::flush;\n'
                       '    }',
                       source)


    def test_print_function_with_flush_false(self):
        source = transpile_source('def main():\n'
                                  '    print("Hi!", flush=False)\n')

        self.assert_in('std::cout << "Hi!" << std::endl;', source)

    def test_print_function_with_and_and_flush(self):
        source = transpile_source('def main():\n'
                                  '    print("Hi!", end="!!", flush=True)\n')

        self.assert_in('    std::cout << "Hi!" << "!!";\n'
                       '    if (Bool(true)) {\n'
                       '        std::cout << std::flush;\n'
                       '    }',
                       source)

    def test_print_function_i8_u8_as_integers_not_char(self):
        source = transpile_source('def main():\n'
                                  '    print(i8(-1), u8(1), u16(1))\n')

        self.assert_in(
            '    std::cout << (int)i8(-1) << " " << (unsigned)u8(1) '
            '<< " " << u16(1) << std::endl;\n',
            source)

    def test_print_function_invalid_keyword(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def main():\n'
                             '    print("Hi!", foo=True)\n',
                             'src/mod.mys',
                             'pkg/mod.mys.hpp')

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

    def test_undefined_variable_4(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def bar():\n'
                             '    try:\n'
                             '        pass\n'
                             '    except GeneralError as e:\n'
                             '        pass\n'
                             '\n'
                             '    print(e)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 7\n'
            '        print(e)\n'
            '              ^\n'
            "CompileError: undefined variable 'e'\n")

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
            "CompileError: undefined class 'Bar'\n")

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
            transpile_source('from foo import bar\n'
                             '\n'
                             'def fie() -> i32:\n'
                             '    return 2 * bar\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    from foo import bar\n'
            '    ^\n'
            "CompileError: imported module 'foo.lib' does not exist\n")

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
            "CompileError: can't import private definition '_BAR'\n")

    def test_import_function_ok(self):
        transpile([
            Source('from foo import bar\n'
                   'def fie():\n'
                   '    bar()\n'),
            Source('def bar():\n'
                   '    pass\n',
                   module='foo.lib')
        ])

    def test_find_definitions(self):
        definitions = find_definitions(
            ast.parse(
                'VAR1: i32 = 1\n'
                '_VAR2: [bool] = [True, False]\n'
                '@enum\n'
                'class Enum1:\n'
                '    A\n'
                '    B\n'
                '    C\n'
                '    D = 100\n'
                '    E\n'
                '@enum(u8)\n'
                'class _Enum2:\n'
                '    Aa = 1\n'
                '    Bb = -5\n'
                '@trait\n'
                'class Trait1:\n'
                '    def foo(self):\n'
                '        pass\n'
                'class Class1:\n'
                '    m1: i32\n'
                '    m2: [i32]\n'
                '    _m3: i32\n'
                '    def foo(self):\n'
                '        pass\n'
                '    def bar(self, a: i32) -> i32:\n'
                '        return a\n'
                '    def bar(self, a: i32, b: (bool, u8)) -> [i32]:\n'
                '        return a\n'
                '    def fie(a: i32):\n'
                '        pass\n'
                'class Class2:\n'
                '    pass\n'
                '@generic(T)\n'
                'class _Class3:\n'
                '    a: T\n'
                'def func1(a: i32, b: bool, c: Class1, d: [(u8, string)]):\n'
                '    pass\n'
                'def func2() -> bool:\n'
                '    pass\n'
                '@raises(TypeError)\n'
                'def func3() -> [i32]:\n'
                '    raise TypeError()\n'
                '@generic(T1, T2)\n'
                'def _func4(a: T1, b: T2):\n'
                '    pass\n'))

        self.assertEqual(list(definitions.variables), ['VAR1', '_VAR2'])
        self.assertEqual(list(definitions.classes), ['Class1', 'Class2', '_Class3'])
        self.assertEqual(list(definitions.traits), ['Trait1'])
        self.assertEqual(list(definitions.functions),
                         ['func1', 'func2', 'func3', '_func4'])
        self.assertEqual(list(definitions.enums), ['Enum1', '_Enum2'])

        # Variables.
        var1 = definitions.variables['VAR1']
        self.assertEqual(var1.name, 'VAR1')
        self.assertEqual(var1.type, 'i32')

        var2 = definitions.variables['_VAR2']
        self.assertEqual(var2.name, '_VAR2')
        self.assertEqual(var2.type, ['bool'])

        # Enums.
        enum1 = definitions.enums['Enum1']
        self.assertEqual(enum1.name, 'Enum1')
        self.assertEqual(enum1.type, 'i64')
        self.assertEqual(enum1.members,
                         [('A', 0), ('B', 1), ('C', 2), ('D', 100), ('E', 101)])

        enum2 = definitions.enums['_Enum2']
        self.assertEqual(enum2.name, '_Enum2')
        self.assertEqual(enum2.type, 'u8')
        self.assertEqual(enum2.members, [('Aa', 1), ('Bb', -5)])

        # Functions.
        func1s = definitions.functions['func1']
        self.assertEqual(len(func1s), 1)

        func1 = func1s[0]
        self.assertEqual(func1.name, 'func1')
        self.assertEqual(func1.returns, None)
        self.assertEqual(
            func1.args,
            [('a', 'i32'), ('b', 'bool'), ('c', 'Class1'), ('d', [('u8', 'string')])])

        func2s = definitions.functions['func2']
        self.assertEqual(len(func2s), 1)

        func2 = func2s[0]
        self.assertEqual(func2.name, 'func2')
        self.assertEqual(func2.returns, 'bool')
        self.assertEqual(func2.args, [])

        func3s = definitions.functions['func3']
        self.assertEqual(len(func3s), 1)

        func3 = func3s[0]
        self.assertEqual(func3.name, 'func3')
        self.assertEqual(func3.raises, ['TypeError'])
        self.assertEqual(func3.returns, ['i32'])
        self.assertEqual(func3.args, [])

        func4s = definitions.functions['_func4']
        self.assertEqual(len(func4s), 1)

        func4 = func4s[0]
        self.assertEqual(func4.name, '_func4')
        self.assertEqual(func4.generic_types, ['T1', 'T2'])
        self.assertEqual(func4.returns, None)
        self.assertEqual(func4.args, [('a', 'T1'), ('b', 'T2')])

        # Class1.
        class1 = definitions.classes['Class1']
        self.assertEqual(class1.name, 'Class1')
        self.assertEqual(class1.generic_types, [])
        self.assertEqual(list(class1.members), ['m1', 'm2', '_m3'])
        self.assertEqual(list(class1.methods), ['foo', 'bar'])
        self.assertEqual(list(class1.functions), ['fie'])

        # Members.
        m1 = class1.members['m1']
        self.assertEqual(m1.name, 'm1')
        self.assertEqual(m1.type, 'i32')

        m2 = class1.members['m2']
        self.assertEqual(m2.name, 'm2')
        self.assertEqual(m2.type, ['i32'])

        m3 = class1.members['_m3']
        self.assertEqual(m3.name, '_m3')
        self.assertEqual(m3.type, 'i32')

        # Methods.
        foos = class1.methods['foo']
        self.assertEqual(len(foos), 1)

        foo = foos[0]
        self.assertEqual(foo.name, 'foo')
        self.assertEqual(foo.returns, None)
        self.assertEqual(foo.args, [])

        bars = class1.methods['bar']
        self.assertEqual(len(bars), 2)

        bar = bars[0]
        self.assertEqual(bar.name, 'bar')
        self.assertEqual(bar.returns, 'i32')
        self.assertEqual(bar.args, [('a', 'i32')])

        bar = bars[1]
        self.assertEqual(bar.name, 'bar')
        self.assertEqual(bar.returns, ['i32'])
        self.assertEqual(bar.args, [('a', 'i32'), ('b', ('bool', 'u8'))])

        fies = class1.functions['fie']
        self.assertEqual(len(fies), 1)

        # Functions.
        fie = fies[0]
        self.assertEqual(fie.name, 'fie')
        self.assertEqual(fie.returns, None)
        self.assertEqual(fie.args, [('a', 'i32')])

        # _Class3.
        class3 = definitions.classes['_Class3']
        self.assertEqual(class3.name, '_Class3')
        self.assertEqual(class3.generic_types, ['T'])
        self.assertEqual(list(class3.members), ['a'])
        self.assertEqual(list(class3.methods), [])
        self.assertEqual(list(class3.functions), [])

        # Members.
        a = class3.members['a']
        self.assertEqual(a.name, 'a')
        self.assertEqual(a.type, 'T')

        # Trait1.
        trait1 = definitions.traits['Trait1']
        self.assertEqual(trait1.name, 'Trait1')
        self.assertEqual(list(trait1.methods), ['foo'])

        # Methods.
        foos = trait1.methods['foo']
        self.assertEqual(len(foos), 1)

        foo = foos[0]
        self.assertEqual(foo.name, 'foo')
        self.assertEqual(foo.returns, None)
        self.assertEqual(foo.args, [])

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
            transpile_source('class apa():\n'
                             '    pass\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    class apa():\n'
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

    def test_for_loop_underscores(self):
        source = transpile_source('def foo():\n'
                                  '    for _, _ in [(1, True)]:\n'
                                  '        pass\n')

        self.assert_in(
            "    auto items_1 = std::make_shared<List<std::shared_ptr<"
            "Tuple<i64, Bool>>>>("
            "std::initializer_list<std::shared_ptr<Tuple<i64, Bool>>>{"
            "std::make_shared<Tuple<i64, Bool>>(1, Bool(true))});\n"
            '    for (auto i_2 = 0; i_2 < items_1->__len__(); i_2++) {\n'
            '    }\n',
            source)

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
            "CompileError: invalid enum member name\n")

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
        header = transpile_header('@trait\n'
                                  'class Foo:\n'
                                  '    pass\n')
        self.assert_in('class Foo : public Object {\n'
                       'public:\n'
                       '\n'
                       '};\n',
                       header)

    def test_define_trait_with_single_method(self):
        header = transpile_header('@trait\n'
                                  'class Foo:\n'
                                  '    def bar(self):\n'
                                  '        pass\n')

        self.assert_in('class Foo : public Object {\n'
                       'public:\n'
                       '    virtual void bar() = 0;\n'
                       '};\n',
                       header)

    def test_define_trait_with_multiple_methods(self):
        header = transpile_header('@trait\n'
                                  'class Foo:\n'
                                  '    def bar(self):\n'
                                  '        pass\n'
                                  '    def fie(self, v1: i32) -> bool:\n'
                                  '        pass\n')

        self.assert_in('class Foo : public Object {\n'
                       'public:\n'
                       '    virtual void bar() = 0;\n'
                       '    virtual Bool fie(i32 v1) = 0;\n'
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
            "CompileError: traits can not have members\n")

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

    def test_implement_trait_in_class(self):
        header = transpile_header('@trait\n'
                                  'class Base:\n'
                                  '    def bar(self) -> bool:\n'
                                  '        pass\n'
                                  '@trait\n'
                                  'class Base2:\n'
                                  '    def fie(self):\n'
                                  '        pass\n'
                                  'class Foo(Base):\n'
                                  '    def bar(self) -> bool:\n'
                                  '        return False\n'
                                  'class Bar(Base, Base2):\n'
                                  '    def bar(self) -> bool:\n'
                                  '        return True\n'
                                  '    def fie(self):\n'
                                  '        print()\n')

        self.assert_in('class Foo : public Base {', header)
        self.assert_in('class Bar : public Base, public Base2 {', header)

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

    def test_match_i32(self):
        source = transpile_source('def foo(value: i32):\n'
                                  '    match value:\n'
                                  '        case 0:\n'
                                  '            print(value)\n'
                                  '        case _:\n'
                                  '            print(value)\n')

        self.assert_in('void foo(i32 value)\n'
                       '{\n'
                       '    if (value == 0) {\n'
                       '        std::cout << value << std::endl;\n'
                       '    } else {\n'
                       '        std::cout << value << std::endl;\n'
                       '    }\n'
                       '}',
                       source)

    def test_match_string(self):
        source = transpile_source('def foo(value: string):\n'
                                  '    match value:\n'
                                  '        case "a":\n'
                                  '            print(value)\n'
                                  '        case "b":\n'
                                  '            print(value)\n')

        self.assert_in('void foo(const String& value)\n'
                       '{\n'
                       '    if (value == "a") {\n'
                       '        std::cout << value << std::endl;\n'
                       '    } else if (value == "b") {\n'
                       '        std::cout << value << std::endl;\n'
                       '    }\n'
                       '}',
                       source)

    def test_match_function_return_value(self):
        source = transpile_source('def foo() -> i32:\n'
                                  '    return 1\n'
                                  'def bar():\n'
                                  '    match foo():\n'
                                  '        case 0:\n'
                                  '            print(0)\n')

        self.assert_in('void bar(void)\n'
                       '{\n'
                       '    auto subject_1 = foo();\n'
                       '    if (subject_1 == 0) {\n'
                       '        std::cout << 0 << std::endl;\n'
                       '    }\n'
                       '}\n',
                       source)

    def test_match_trait(self):
        source = transpile_source('@trait\n'
                                  'class Base:\n'
                                  '    pass\n'
                                  'class Foo(Base):\n'
                                  '    pass\n'
                                  'class Bar(Base):\n'
                                  '    pass\n'
                                  'class Fie(Base):\n'
                                  '    pass\n'
                                  'def foo(base: Base):\n'
                                  '    match base:\n'
                                  '        case Foo():\n'
                                  '            print("foo")\n'
                                  '        case Bar() as value:\n'
                                  '            print(value)\n'
                                  '        case Fie() as value:\n'
                                  '            print(value)\n')

        self.assert_in(
            'void foo(const std::shared_ptr<Base>& base)\n'
            '{\n'
            '    auto casted_1 = std::dynamic_pointer_cast<Foo>(base);\n'
            '    if (casted_1) {\n'
            '        std::cout << "foo" << std::endl;\n'
            '    } else {\n'
            '        auto casted_2 = std::dynamic_pointer_cast<Bar>(base);\n'
            '        if (casted_2) {\n'
            '            auto value = std::move(casted_2);\n'
            '            std::cout << value << std::endl;\n'
            '        } else {\n'
            '            auto casted_3 = std::dynamic_pointer_cast<Fie>(base);\n'
            '            if (casted_3) {\n'
            '                auto value = std::move(casted_3);\n'
            '                std::cout << value << std::endl;\n'
            '            }\n'
            '        }\n'
            '    }\n'
            '}\n',
            source)

    def test_match_integer_literal(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(value: i32):\n'
                             '    match 1:\n'
                             '        case 0:\n'
                             '            print(1)\n'
                             '        case _:\n'
                             '            print(-1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        match 1:\n'
            '              ^\n'
            "CompileError: subject can only be variables and return values\n")

    def test_inferred_type_integer_assignment(self):
        source = transpile_source('def foo():\n'
                                  '    value_1 = 1\n'
                                  '    value_2 = -1\n'
                                  '    value_3 = +1\n'
                                  '    print(value_1, value_2, value_3)\n')

        self.assert_in(
            'void foo(void)\n'
            '{\n'
            '    i64 value_1 = 1;\n'
            '    i64 value_2 = -1;\n'
            '    i64 value_3 = 1;\n'
            '    std::cout << value_1 << " " << value_2 << " " << value_3 << std::endl;\n'
            '}\n',
            source)

    def test_inferred_type_combined_integers_assignment(self):
        source = transpile_source('def foo():\n'
                                  '    value_1 = (1 + 1)\n'
                                  '    value_2 = (1 / (3 ^ 4) * 3)\n'
                                  '    print(value_1, value_2)\n')

        self.assert_in(
            'void foo(void)\n'
            '{\n'
            '    i64 value_1 = (1 + 1);\n'
            '    i64 value_2 = ((1 / (3 ^ 4)) * 3);\n'
            '    std::cout << value_1 << " " << value_2 << std::endl;\n'
            '}\n',
            source)

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

    def test_inferred_type_string_assignment(self):
        source = transpile_source('def foo():\n'
                                  '    value = "a"\n'
                                  '    print(value)\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    String value = String("a");\n'
                       '    std::cout << value << std::endl;\n'
                       '}\n',
                       source)

    def test_inferred_type_bool_assignment(self):
        source = transpile_source('def foo():\n'
                                  '    value = True\n'
                                  '    print(value)\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    Bool value = Bool(true);\n'
                       '    std::cout << value << std::endl;\n'
                       '}\n',
                       source)

    def test_inferred_type_float_assignment(self):
        source = transpile_source('def foo():\n'
                                  '    value_1 = 6.44\n'
                                  '    value_2 = -6.44\n'
                                  '    value_3 = +6.44\n'
                                  '    print(value_1, value_2, value_3)\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    f64 value_1 = 6.44;\n'
                       '    f64 value_2 = -(6.44);\n'
                       '    f64 value_3 = +(6.44);\n'
                       '    std::cout << value_1 << " " << value_2 << " " << '
                       'value_3 << std::endl;\n'
                       '}\n',
                       source)

    def test_inferred_type_class_assignment(self):
        source = transpile_source('class A:\n'
                                  '    pass\n'
                                  'def foo():\n'
                                  '    value = A()\n'
                                  '    print(value)\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    auto value = std::make_shared<A>();\n'
                       '    std::cout << value << std::endl;\n'
                       '}\n',
                       source)

    def test_tuple_assignment(self):
        source = transpile_source('def foo():\n'
                                  '    value_1 = (1, "hi", True, 1.0)\n'
                                  '    value_2: (i64, f64) = (1, 1.0)\n'
                                  '    print(value_1)\n')

        self.assert_in(
            'void foo(void)\n'
            '{\n'
            '    auto value_1 = std::make_shared<Tuple<i64, String, Bool, f64>>('
            '1, "hi", Bool(true), 1.0);\n'
            '    auto value_2 = std::make_shared<Tuple<i64, f64>>(1, 1.0);\n'
            '    std::cout << value_1 << std::endl;\n'
            '}\n',
            source)

    def test_reassign_class_variable(self):
        source = transpile_source('class A:\n'
                                  '    pass\n'
                                  'def foo():\n'
                                  '    value = A()\n'
                                  '    print(value)\n'
                                  '    value = A()\n'
                                  '    print(value)\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    auto value = std::make_shared<A>();\n'
                       '    std::cout << value << std::endl;\n'
                       '    value = std::make_shared<A>();\n'
                       '    std::cout << value << std::endl;\n'
                       '}\n',
                       source)

    def test_string_as_function_parameter(self):
        source = transpile_source('def foo(value: string) -> string:\n'
                                  '    return value\n'
                                  'def bar():\n'
                                  '    print(foo("Cat"))\n')

        self.assert_in('void bar(void)\n'
                       '{\n'
                       '    std::cout << foo("Cat") << std::endl;\n'
                       '}\n',
                       source)

    def test_test_functions_not_in_header(self):
        header = transpile_header('@test\n'
                                  'def test_foo():\n'
                                  '    pass\n',
                                  module_hpp='foo/lib.mys.hpp')

        self.assertNotIn('test_foo', header)

    def test_function_header_signatures(self):
        header = transpile_header('class Foo:\n'
                                  '    pass\n'
                                  'def foo(a: i32, b: string, c: [i32]):\n'
                                  '    pass\n'
                                  'def bar(a: Foo) -> bool:\n'
                                  '    pass\n'
                                  'def fie(b: (i32, Foo)) -> u8:\n'
                                  '    pass\n'
                                  'def fum() -> [Foo]:\n'
                                  '    pass\n'
                                  'def fam() -> (bool, Foo):\n'
                                  '    pass\n')

        self.assert_in(
            'void foo(i32 a, const String& b, const std::shared_ptr<List<i32>>& c);',
            header)
        self.assert_in('Bool bar(const std::shared_ptr<Foo>& a);', header)
        self.assert_in(
            'u8 fie(const std::shared_ptr<Tuple<i32, std::shared_ptr<Foo>>>& b);',
            header)
        self.assert_in('std::shared_ptr<List<std::shared_ptr<Foo>>> fum(void);',
                       header)
        self.assert_in(
            'std::shared_ptr<Tuple<Bool, std::shared_ptr<Foo>>> fam(void);',
            header)

    def test_function_source_signatures(self):
        source = transpile_source('class Foo:\n'
                                  '    pass\n'
                                  'def foo(a: i32, b: string, c: [i32]):\n'
                                  '    pass\n'
                                  'def bar(a: Foo) -> bool:\n'
                                  '    pass\n'
                                  'def fie(b: (i32, Foo)) -> u8:\n'
                                  '    pass\n'
                                  'def fum() -> [Foo]:\n'
                                  '    pass\n'
                                  'def fam() -> (bool, Foo):\n'
                                  '    pass\n')

        self.assert_in(
            'void foo(i32 a, const String& b, const std::shared_ptr<List<i32>>& c);',
            source)
        self.assert_in('Bool bar(const std::shared_ptr<Foo>& a);', source)
        self.assert_in(
            'u8 fie(const std::shared_ptr<Tuple<i32, std::shared_ptr<Foo>>>& b);',
            source)
        self.assert_in('std::shared_ptr<List<std::shared_ptr<Foo>>> fum(void);',
                       source)
        self.assert_in(
            'std::shared_ptr<Tuple<Bool, std::shared_ptr<Foo>>> fam(void);',
            source)

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
            "CompileError: can't convert list to '(bool, i64)'\n")

    def test_return_tuple_from_function_returning_list(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> [bool]:\n'
                             '    return (1, True)')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return (1, True)\n'
            '               ^\n'
            "CompileError: can't convert tuple to '[bool]'\n")

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
            "CompileError: expected a '[(string, Foo)]', got a '{i64: i64}'\n")

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
            "CompileError: expected 0 parameter(s), got 1\n")

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
            "CompileError: expected a 'WrongBase', got a 'Foo'\n")

    def test_compare_i64_and_bool(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return 1 == True')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return 1 == True\n'
            '               ^\n'
            "CompileError: can't convert integer to 'bool'\n")

    def test_compare_mix_of_literals_and_known_types_1(self):
        source = transpile_source('def foo():\n'
                                  '    k: u64 = 1\n'
                                  '    v: i64 = 1\n'
                                  '    if 0xffffffffffffffff == k:\n'
                                  '        pass\n'
                                  '    print(v)\n')

        self.assert_in('18446744073709551615ull == k', source)

    def test_compare_mix_of_literals_and_known_types_2(self):
        source = transpile_source('def foo():\n'
                                  '    k: u64 = 1\n'
                                  '    v: i64 = 1\n'
                                  '    if k == 0xffffffffffffffff:\n'
                                  '        pass\n'
                                  '    print(v)\n')

        self.assert_in('k == 18446744073709551615ull', source)

    def test_call_member_method(self):
        source = transpile_source('class Foo:\n'
                                  '    def fam(self):\n'
                                  '        pass\n'
                                  'class Bar:\n'
                                  '    foo: Foo = Foo()\n'
                                  'def foo(bar: Bar):\n'
                                  '    bar.foo.fam()')

        self.assert_in('bar->foo->fam();', source)

    def test_global_variable(self):
        source = transpile_source('GLOB_1: i32 = 1\n'
                                  'GLOB_2: string = ""\n')

        self.assert_in('i32 GLOB_1 = 1;', source)
        self.assert_in('String GLOB_2 = String("");', source)

    def test_global_class_variable(self):
        source = transpile_source('class Foo:\n'
                                  '    pass\n'
                                  'GLOB: Foo = Foo()\n')

        self.assert_in('std::shared_ptr<Foo> GLOB = std::make_shared<Foo>();',
                       source)

    def test_global_variable_function_call(self):
        source = transpile_source('def foo(v: i32) -> i32:\n'
                                  '    return 2 * v\n'
                                  'GLOB: i32 = foo(1)\n')

        self.assert_in('i32 GLOB = foo(1);', source)

    def test_assign_256_to_u8(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('A: u8 = 256\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    A: u8 = 256\n'
            '            ^\n'
            "CompileError: integer literal out of range for 'u8'\n")

    def test_assign_max_to_u64(self):
        source = transpile_source('A: u64 = 0xffffffffffffffff\n')

        self.assert_in('u64 A = 18446744073709551615ull;', source)

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
            "CompileError: can't convert float to 'u8'\n")

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
            "CompileError: global variable types can't be inferred\n")

    def test_arithmetics_on_mix_of_literals_and_known_types_1(self):
        source = transpile_source('def foo():\n'
                                  '    k: u64 = 1\n'
                                  '    v: i64 = 1\n'
                                  '    value = (0xffffffffffffffff + k)\n'
                                  '    print(value, v)\n')

        self.assert_in('value = (18446744073709551615ull + k);', source)

    def test_arithmetics_on_mix_of_literals_and_known_types_2(self):
        source = transpile_source('def foo():\n'
                                  '    k: u64 = 1\n'
                                  '    v: i64 = 1\n'
                                  '    value = (k + 0xffffffffffffffff)\n'
                                  '    print(value, v)\n')

        self.assert_in('value = (k + 18446744073709551615ull);', source)

    def test_arithmetics_on_mix_of_literals_and_known_types_3(self):
        source = transpile_source('def foo():\n'
                                  '    k: u64 = 1\n'
                                  '    v: i64 = 1\n'
                                  '    value = (k * (1 / 2))\n'
                                  '    print(value, v)\n')

        self.assert_in('value = (k * (1ull / 2ull));', source)

    def test_arithmetics_on_mix_of_literals_and_known_types_4(self):
        source = transpile_source('def foo():\n'
                                  '    k: u64 = 1\n'
                                  '    v: i64 = 1\n'
                                  '    value = ((1 / 2) - 2 * k)\n'
                                  '    print(value, v)\n')

        self.assert_in('value = ((1ull / 2ull) - (2ull * k));', source)

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
            "CompileError: can't compare 'i8' and 'u32'\n")

    def test_global_class_variable_in_function_call(self):
        source = transpile_source('class Foo:\n'
                                  '    pass\n'
                                  'def foo(v: Foo) -> Foo:\n'
                                  '    return v\n'
                                  'GLOB: Foo = foo(Foo())\n')

        self.assert_in('std::shared_ptr<Foo> GLOB = foo(std::make_shared<Foo>());',
                       source)

    def test_function_call(self):
        source = transpile_source('def foo(a: i32, b: f32):\n'
                                  '    print(a, b)\n'
                                  'def bar():\n'
                                  '    foo(1, 2.1)\n')

        self.assert_in('foo(1, 2.1);', source)

    def test_assign_to_self(self):
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

    def test_assign_to_self(self):
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

    def test_tuple_unpack(self):
        source = transpile_source('class Foo:\n'
                                  '    def foo(self) -> (bool, i64):\n'
                                  '        return (True, -5)\n'
                                  'def foo():\n'
                                  '    foo = Foo()\n'
                                  '    a, b = foo.foo()\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    auto foo = std::make_shared<Foo>();\n'
                       '    auto tuple_1 = foo->foo();\n'
                       '    auto a = std::get<0>(tuple_1->m_tuple);\n'
                       '    auto b = std::get<1>(tuple_1->m_tuple);\n'
                       '}\n',
                       source)

    def test_tuple_unpack_init(self):
        source = transpile_source('def foo():\n'
                                  '    foo, bar = 1, "b"\n'
                                  '    if foo == 1:\n'
                                  '        print(bar)\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    auto tuple_1 = std::make_shared<Tuple<i64, String>>(1, "b");\n'
                       '    auto foo = std::get<0>(tuple_1->m_tuple);\n'
                       '    auto bar = std::get<1>(tuple_1->m_tuple);\n'
                       '    if (Bool(foo == 1)) {\n'
                       '        std::cout << bar << std::endl;\n'
                       '    }\n'
                       '}\n',
                       source)

    def test_tuple_unpack_variable_defined_other_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('class Foo:\n'
                             '    def foo(self) -> (bool, i64):\n'
                             '        return (True, -5)\n'
                             'def foo():\n'
                             '    foo = Foo()\n'
                             '    b: string = ""\n'
                             '    a, b = foo.foo()\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 7\n'
            '        a, b = foo.foo()\n'
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

    def test_character_literals_not_yet_supported(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "    a = '1'\n")

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            "        a = '1'\n"
            '            ^\n'
            "CompileError: character literals are not yet supported\n")

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

    def test_declare_list_with_variable_in_init(self):
        source = transpile_source('def foo():\n'
                                  '    a = -1\n'
                                  '    b: [i64] = [1, a]\n'
                                  '    print(a)\n')

        self.assert_in(
            'void foo(void)\n'
            '{\n'
            '    i64 a = -1;\n'
            '    std::shared_ptr<List<i64>> b = '
            'std::make_shared<List<i64>>(std::initializer_list<i64>{1, a});\n'
            '    std::cout << a << std::endl;\n'
            '}\n',
            source)

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

    def test_iterate_over_list_of_integer_literals(self):
        source = transpile_source('def foo():\n'
                                  '    for i in [5, 1]:\n'
                                  '        print(i)\n')

        self.assert_in(
            'void foo(void)\n'
            '{\n'
            '    auto items_1 = std::make_shared<List<i64>>('
            'std::initializer_list<i64>{5, 1});\n'
            '    for (auto i_2 = 0; i_2 < items_1->__len__(); i_2++) {\n'
            '        auto i = items_1->get(i_2);\n'
            '        std::cout << i << std::endl;\n'
            '    }\n'
            '}\n',
            source)

    def test_iterate_over_list(self):
        source = transpile_source('def foo():\n'
                                  '    values: [u32] = [3, 8]\n'
                                  '    for value in values:\n'
                                  '        print(value)\n')

        self.assert_in(
            'void foo(void)\n'
            '{\n'
            '    std::shared_ptr<List<u32>> values = std::make_shared<List<u32>>('
            'std::initializer_list<u32>{3, 8});\n'
            '    auto items_1 = values;\n'
            '    for (auto i_2 = 0; i_2 < items_1->__len__(); i_2++) {\n'
            '        auto value = items_1->get(i_2);\n'
            '        std::cout << value << std::endl;\n'
            '    }\n'
            '}\n',
            source)

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
            "CompileError: it's not allowed to iterate over tuples\n")

    def test_iterate_dict_tuple(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    for k, v in {5: 1}:\n'
                             '        print(k, v)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        for k, v in {5: 1}:\n'
            '                    ^\n'
            "CompileError: it's not yet supported to iterate over dicts\n")

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
            "CompileError: can only unpack enumerate into two variables\n")

    def test_iterate_over_enumerate(self):
        source = transpile_source('def foo():\n'
                                  '    values: [u32] = [3, 8]\n'
                                  '    for i, value in enumerate(values):\n'
                                  '        print(i, value)\n')

        self.assert_in(
            '    auto data_1_object = values;\n'
            '    auto data_1 = Data(data_1_object->__len__());\n'
            '    auto enumerate_2 = Enumerate(i64(0), i64(data_1.length()));\n'
            '    auto len_3 = data_1.length();\n'
            '    data_1.iter();\n'
            '    enumerate_2.iter();\n'
            '    for (auto i_4 = 0; i_4 < len_3; i_4++) {\n'
            '        auto i = enumerate_2.next();\n'
            '        auto value = data_1_object->get(data_1.next());\n'
            '        std::cout << i << " " << value << std::endl;\n'
            '    }\n',
            source)

    def test_iterate_over_slice(self):
        source = transpile_source('def foo():\n'
                                  '    for x in slice(range(4), 2):\n'
                                  '        print(x)\n')

        self.assert_in(
            '    auto range_1 = Range(i64(0), i64(4), i64(1));\n'
            '    auto slice_2 = OpenSlice(i64(2));\n'
            '    range_1.slice(slice_2);\n'
            '    auto len_3 = range_1.length();\n'
            '    range_1.iter();\n'
            '    for (auto i_4 = 0; i_4 < len_3; i_4++) {\n'
            '        auto x = range_1.next();\n'
            '        std::cout << x << std::endl;\n'
            '    }\n',
            source)

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
            "CompileError: two to four parameters expected, got 1\n")

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
            "CompileError: one to three parameters expected, got 4\n")

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
            "CompileError: one or two parameters expected, got 0\n")

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
            "CompileError: can't unpack 2 values into 1\n")

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
            "CompileError: one parameter expected, got 0\n")

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
            "CompileError: can't convert list to 'u32'\n")

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
            "CompileError: can't convert integer to '[string]'\n")

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
            "CompileError: unable to resolve literal type\n")

    def test_compare_wrong_types_5(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo() -> bool:\n'
                             '    return 1.0 == [""]\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return 1.0 == [""]\n'
            '               ^\n'
            "CompileError: can't convert float to '[string]'\n")

    def test_compare_wrong_types_6(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: i32) -> bool:\n'
                             '    return a in [""]\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return a in [""]\n'
            '               ^\n'
            "CompileError: expected a 'string', got a 'i32'\n")

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
            '              ^\n'
            "CompileError: integers can't be None\n")

    def test_compare_wrong_types_11(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(1.0 is None)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(1.0 is None)\n'
            '              ^\n'
            "CompileError: floats can't be None\n")

    def test_compare_wrong_types_12(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: i32):\n'
                             '    print(a is None)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(a is None)\n'
            '              ^\n'
            "CompileError: 'i32' can't be None\n")

    def test_compare_wrong_types_13(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: i32):\n'
                             '    print(None is a)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(None is a)\n'
            '              ^\n'
            "CompileError: 'i32' can't be None\n")

    def test_compare_wrong_types_14(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(True is None)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(True is None)\n'
            '              ^\n'
            "CompileError: 'bool' can't be None\n")

    def test_compare_wrong_types_15(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: bool):\n'
                             '    print(None is a)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(None is a)\n'
            '              ^\n'
            "CompileError: 'bool' can't be None\n")

    def test_compare_wrong_types_16(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo(a: bool):\n'
                             '    print(a is not 1)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(a is not 1)\n'
            '                       ^\n'
            "CompileError: can't convert integer to 'bool'\n")

    def test_compare_wrong_types_17(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(None in [1, 5])\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(None in [1, 5])\n'
            '              ^\n'
            "CompileError: 'i64' can't be None\n")

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
            "CompileError: types 'Foo' and 'Bar' differs\n")

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
            "CompileError: 'i64' is not a 'bool'\n")

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
            "CompileError: 'i64' is not a 'bool'\n")

    def test_inferred_type_none(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    a = None\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            "        a = None\n"
            '        ^\n'
            "CompileError: can't infer type from None\n")

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
            "CompileError: can't convert float to 'i64'\n")

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

    def test_assert_formatting_i8_u8(self):
        source = transpile_source('def foo():\n'
                                  '    assert i8(1) == i8(2)\n'
                                  '    assert u8(1) == u8(2)\n'
                                  '    assert u16(1) == u16(2)\n')

        self.assert_in('(int)var_1 << " == " << (int)var_2', source)
        self.assert_in('(unsigned)var_3 << " == " << (unsigned)var_4', source)
        self.assert_in('var_5 << " == " << var_6', source)

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
                             'def foo(foo: Foo):\n'
                             '    print(foo.missing)\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(foo.missing)\n'
            '              ^\n'
            "CompileError: class 'Foo' has no member 'missing'\n")

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
            "CompileError: class 'Foo' has no member 'missing'\n")

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
            "CompileError: class 'Foo' has no member 'b'\n")

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
            "CompileError: class 'Foo' member '_a' is private\n")

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
            "CompileError: expected one parameter, got 0\n")

    def test_len_two_params(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(len(1, 2))\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(len(1, 2))\n'
            '              ^\n'
            "CompileError: expected one parameter, got 2\n")

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
                             '    foo = (1, "b")\n'
                             '    print(foo[a])\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 4\n'
            '        print(foo[a])\n'
            '                  ^\n'
            "CompileError: tuple indexes must be integers\n")

    def test_tuple_index_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    foo = (1, "b")\n'
                             '    print(foo[1 / 2])\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        print(foo[1 / 2])\n'
            '                  ^\n'
            "CompileError: tuple indexes must be integers\n")

    def test_tuple_item_assign_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    foo = (1, "b")\n'
                             '    foo[0] = "ff"\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        foo[0] = "ff"\n'
            '                 ^\n'
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
            "CompileError: 'bool' can't be None\n")

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
            "CompileError: 'bool' can't be None\n")

    def test_assign_none_to_i32(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('A: i32 = None\n')

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    A: i32 = None\n'
            '             ^\n'
            "CompileError: 'i32' can't be None\n")

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
            "CompileError: expected a 'i64', got a 'f64'\n")

    def test_dict_init_key_types_mismatch(self):
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
            '            ^\n'
            "CompileError: invalid key type\n")

    # ToDo
    # def test_dict_init_value_types_mismatch_2(self):
    #     with self.assertRaises(Exception) as cm:
    #         transpile_source('def foo():\n'
    #                          '    v = {True: i8(5), False: u8(4)}\n'
    #                          '    print(v)\n')
    #
    #     self.assertEqual(
    #         remove_ansi(str(cm.exception)),
    #         '  File "", line 2\n'
    #         '        v = {True: 5, False: "a"}\n'
    #         '                             ^\n'
    #         "CompileError: expected a 'i64', got a 'string'\n")

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
            "CompileError: expected 1 parameter(s), got 2\n")

    # ToDo
    # def test_class_init_too_many_parameters(self):
    #     with self.assertRaises(Exception) as cm:
    #         transpile_source('class Foo:\n'
    #                          '    a: (bool, string)\n'
    #                          'def foo():\n'
    #                          '    print(Foo(("", 1)))\n')
    #
    #     self.assertEqual(
    #         remove_ansi(str(cm.exception)),
    #         '  File "", line 4\n'
    #         '        print(Foo(("", 1)))\n'
    #         '                  ^\n'
    #         "CompileError: types differ\n")

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
