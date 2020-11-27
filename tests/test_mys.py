import difflib
import ast
import sys
import unittest
from mys.transpile import transpile
from mys import compiler

from .utils import read_file
from .utils import remove_ansi

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
            header, source = transpile(read_file(f'tests/files/{data}.mys'),
                                       f'{data}.mys',
                                       f'{data}.mys.hpp',
                                       {})
            self.assert_equal_to_file(
                header,
                f'tests/files/{data}.mys.hpp')
            self.assert_equal_to_file(
                source,
                f'tests/files/{data}.mys.cpp')

    def test_invalid_main_argument(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main(argv: i32): pass', '', '', {})

        self.assertEqual(str(cm.exception),
                         "main() takes 'argv: [string]' or no arguments.")

    def test_invalid_main_return_type(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main() -> i32: pass', '', '', {})

        self.assertEqual(str(cm.exception), "main() must return 'None'.")

    def test_lambda_not_supported(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main(): print((lambda x: x)(1))', 'foo.py', '', {})

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "foo.py", line 1\n'
                         '    def main(): print((lambda x: x)(1))\n'
                         '                       ^\n'
                         'LanguageError: lambda functions are not supported\n')

    def test_bad_syntax(self):
        with self.assertRaises(Exception) as cm:
            transpile('DEF main(): pass', '<unknown>', '', {})

        self.assertEqual(remove_ansi(str(cm.exception)),
                         '  File "<unknown>", line 1\n'
                         '    DEF main(): pass\n'
                         '        ^\n'
                         'SyntaxError: invalid syntax\n')

    def test_import_in_function_should_fail(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main():\n'
                      '    import foo\n',
                      '<unknown>',
                      '',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<unknown>", line 2\n'
            '        import foo\n'
            '        ^\n'
            'LanguageError: imports are only allowed on module level\n')

    def test_class_in_function_should_fail(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main():\n'
                      '    class A:\n'
                      '        pass\n',
                      '<unknown>',
                      '',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<unknown>", line 2\n'
            '        class A:\n'
            '        ^\n'
            'LanguageError: class definitions are only allowed on module level\n')

    def test_empty_function(self):
        _, source = transpile('def foo():\n'
                              '    pass\n',
                              '<unknown>',
                              '',
                              {})

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '\n'
                       '}\n',
                       source)

    def test_multiple_imports_failure(self):
        with self.assertRaises(Exception) as cm:
            transpile('from foo import bar, fie\n',
                      '<unknown>',
                      '',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "<unknown>", line 1\n'
            '    from foo import bar, fie\n'
            '    ^\n'
            'LanguageError: only one import is allowed, found 2\n')

    def test_relative_import_outside_package(self):
        with self.assertRaises(Exception) as cm:
            transpile('from .. import fie\n',
                      'src/mod.mys',
                      'pkg/mod.mys.hpp',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "src/mod.mys", line 1\n'
            '    from .. import fie\n'
            '    ^\n'
            'LanguageError: relative import is outside package\n')

    def test_comaprsion_operator_return_types(self):
        ops = ['eq', 'ne', 'gt', 'ge', 'lt', 'le']

        for op in ops:
            with self.assertRaises(Exception) as cm:
                transpile('class Foo:\n'
                          f'    def __{op}__(self, other: Foo):\n'
                          '        return True\n',
                          'src/mod.mys',
                          'pkg/mod.mys.hpp',
                          {})

            self.assertEqual(
                remove_ansi(str(cm.exception)),
                '  File "src/mod.mys", line 2\n'
                f'        def __{op}__(self, other: Foo):\n'
                '        ^\n'
                f'LanguageError: __{op}__() must return bool\n')

    def test_arithmetic_operator_return_types(self):
        ops = ['add', 'sub']

        for op in ops:
            with self.assertRaises(Exception) as cm:
                transpile('class Foo:\n'
                          f'    def __{op}__(self, other: Foo) -> bool:\n'
                          '        return True\n',
                          'src/mod.mys',
                          'pkg/mod.mys.hpp',
                          {})

            self.assertEqual(
                remove_ansi(str(cm.exception)),
                '  File "src/mod.mys", line 2\n'
                f'        def __{op}__(self, other: Foo) -> bool:\n'
                '        ^\n'
                f'LanguageError: __{op}__() must return Foo\n')

    def test_basic_print_function(self):
        _, source = transpile('def main():\n'
                              '    print("Hi!")\n',
                              'src/mod.mys',
                              'pkg/mod.mys.hpp',
                              {})

        self.assert_in('std::cout << "Hi!" << std::endl;', source)

    def test_print_function_with_end(self):
        _, source = transpile('def main():\n'
                              '    print("Hi!", end="")\n',
                              'src/mod.mys',
                              'pkg/mod.mys.hpp',
                              {})

        self.assert_in('std::cout << "Hi!" << "";', source)

    def test_print_function_with_flush_true(self):
        _, source = transpile('def main():\n'
                              '    print("Hi!", flush=True)\n',
                              'src/mod.mys',
                              'pkg/mod.mys.hpp',
                              {})

        self.assert_in('    std::cout << "Hi!" << std::endl;\n'
                       '    if (true) {\n'
                       '        std::cout << std::flush;\n'
                       '    }',
                       source)


    def test_print_function_with_flush_false(self):
        _, source = transpile('def main():\n'
                              '    print("Hi!", flush=False)\n',
                              'src/mod.mys',
                              'pkg/mod.mys.hpp',
                              {})

        self.assert_in('std::cout << "Hi!" << std::endl;', source)

    def test_print_function_with_and_and_flush(self):
        _, source = transpile('def main():\n'
                              '    print("Hi!", end="!!", flush=True)\n',
                              'src/mod.mys',
                              'pkg/mod.mys.hpp',
                              {})

        self.assert_in('    std::cout << "Hi!" << "!!";\n'
                       '    if (true) {\n'
                       '        std::cout << std::flush;\n'
                       '    }',
                       source)

    def test_print_function_invalid_keyword(self):
        with self.assertRaises(Exception) as cm:
            transpile('def main():\n'
                      '    print("Hi!", foo=True)\n',
                      'src/mod.mys',
                      'pkg/mod.mys.hpp',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "src/mod.mys", line 2\n'
            '        print("Hi!", foo=True)\n'
            '        ^\n'
            "LanguageError: invalid keyword argument 'foo' to print(), only "
            "'end' and 'flush' are allowed\n")

    def test_undefined_variable_1(self):
        # Everything ok, 'value' defined.
        transpile('def foo(value: bool) -> bool:\n'
                  '    return value\n',
                  '',
                  '',
                  {})

        # Error, 'value' is not defined.
        with self.assertRaises(Exception) as cm:
            transpile('def foo() -> bool:\n'
                      '    return value\n',
                      '',
                      '',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return value\n'
            '               ^\n'
            "LanguageError: undefined variable 'value'\n")

    def test_undefined_variable_2(self):
        with self.assertRaises(Exception) as cm:
            transpile('def foo() -> i32:\n'
                      '    return 2 * value\n',
                      '',
                      '',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        return 2 * value\n'
            '                   ^\n'
            "LanguageError: undefined variable 'value'\n")

    def test_undefined_variable_3(self):
        with self.assertRaises(Exception) as cm:
            transpile('def foo(v1: i32) -> i32:\n'
                      '    return v1\n'
                      'def bar() -> i32:\n'
                      '    a: i32 = 1\n'
                      '    return foo(a, value)\n',
                      '',
                      '',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 5\n'
            '        return foo(a, value)\n'
            '                      ^\n'
            "LanguageError: undefined variable 'value'\n")

    def test_undefined_variable_4(self):
        with self.assertRaises(Exception) as cm:
            transpile('def bar():\n'
                      '    try:\n'
                      '        pass\n'
                      '    except Exception as e:\n'
                      '        pass\n'
                      '\n'
                      '    print(e)\n',
                      '',
                      '',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 7\n'
            '        print(e)\n'
            '              ^\n'
            "LanguageError: undefined variable 'e'\n")

    def test_undefined_variable_in_fstring(self):
        with self.assertRaises(Exception) as cm:
            transpile('def bar():\n'
                      '    print(f"{value}")\n',
                      '',
                      '',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 2\n'
            '        print(f"{value}")\n'
            '                 ^\n'
            "LanguageError: undefined variable 'value'\n")

    def test_only_global_defined_in_callee(self):
        with self.assertRaises(Exception) as cm:
            transpile('glob: bool = True\n'
                      'def bar() -> i32:\n'
                      '    a: i32 = 1\n'
                      '    return foo(a)\n'
                      'def foo(v1: i32) -> i32:\n'
                      '    return glob + v1 + a\n'
                      '',
                      '',
                      '',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 6\n'
            '        return glob + v1 + a\n'
            '                           ^\n'
            "LanguageError: undefined variable 'a'\n")

    def test_imported_variable_usage(self):
        transpile('from foo import bar\n'
                  '\n'
                  'def fie() -> i32:\n'
                  '    return 2 * bar\n',
                  '',
                  '',
                  {
                      'foo.lib': compiler.find_public(
                          compiler.create_ast('bar: i32 = 1'))
                  })

    def test_imported_module_does_not_exist(self):
        with self.assertRaises(Exception) as cm:
            transpile('from foo import bar\n'
                      '\n'
                      'def fie() -> i32:\n'
                      '    return 2 * bar\n',
                      '',
                      '',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    from foo import bar\n'
            '    ^\n'
            "LanguageError: imported module 'foo.lib' does not exist\n")

    def test_imported_module_does_not_contain(self):
        with self.assertRaises(Exception) as cm:
            transpile('from foo import bar\n'
                      '\n'
                      'def fie() -> i32:\n'
                      '    return 2 * bar\n',
                      '',
                      '',
                      {
                          'foo.lib': compiler.find_public(
                              compiler.create_ast('boo: i32 = 1'))
                      })

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 1\n'
            '    from foo import bar\n'
            '    ^\n'
            "LanguageError: imported module 'foo.lib' does not contain 'bar'\n")

    def test_find_public(self):
        public = compiler.find_public(
            compiler.create_ast(
                'VAR1: i32 = 1\n'
                '_VAR2: u64 = 5\n'
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
                'class _Class3:\n'
                '    pass\n'
                'def func1(a: i32, b: bool, c: Class1, d: [(u8, string)]):\n'
                '    pass\n'
                'def func2() -> bool:\n'
                '    pass\n'
                'def func3() -> [i32]:\n'
                '    pass\n'
                'def _func4():\n'
                '    pass\n'))

        self.assertEqual(list(public.variables), ['VAR1'])
        self.assertEqual(list(public.classes), ['Class1', 'Class2'])
        self.assertEqual(list(public.functions), ['func1', 'func2', 'func3'])

        func1s = public.functions['func1']
        self.assertEqual(len(func1s), 1)

        func1 = func1s[0]
        self.assertEqual(func1.name, 'func1')
        self.assertEqual(func1.returns, None)
        self.assertEqual(
            func1.args,
            [('a', 'i32'), ('b', 'bool'), ('c', 'Class1'), ('d', [('u8', 'string')])])

        func2s = public.functions['func2']
        self.assertEqual(len(func2s), 1)

        func2 = func2s[0]
        self.assertEqual(func2.name, 'func2')
        self.assertEqual(func2.returns, 'bool')
        self.assertEqual(func2.args, [])

        func3s = public.functions['func3']
        self.assertEqual(len(func3s), 1)

        func3 = func3s[0]
        self.assertEqual(func3.name, 'func3')
        self.assertEqual(func3.returns, ['i32'])
        self.assertEqual(func3.args, [])

        class1 = public.classes['Class1']
        self.assertEqual(class1.name, 'Class1')
        self.assertEqual(list(class1.members), ['m1', 'm2'])
        self.assertEqual(list(class1.methods), ['foo', 'bar'])
        self.assertEqual(list(class1.functions), ['fie'])

        # Members.
        m1 = class1.members['m1']
        self.assertEqual(m1.name, 'm1')
        self.assertEqual(m1.type, 'i32')

        m2 = class1.members['m2']
        self.assertEqual(m2.name, 'm2')
        self.assertEqual(m2.type, ['i32'])

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

    def test_declare_empty_trait(self):
        _, source = transpile('@trait\n'
                              'class Foo:\n'
                              '    pass\n',
                              '',
                              '',
                              {})
        self.assert_in('class Foo : public Object {\n'
                       '\n'
                       'public:\n'
                       '\n'
                       '};\n',
                       source)

    def test_declare_trait_with_single_method(self):
        _, source = transpile('@trait\n'
                              'class Foo:\n'
                              '    def bar(self):\n'
                              '        pass\n',
                              '',
                              '',
                              {})

        self.assert_in('class Foo : public Object {\n'
                       '\n'
                       'public:\n'
                       '\n'
                       '    virtual void bar(void) = 0;\n'
                       '\n'
                       '};\n',
                       source)

    def test_declare_trait_with_multiple_methods(self):
        _, source = transpile('@trait\n'
                              'class Foo:\n'
                              '    def bar(self):\n'
                              '        pass\n'
                              '    def fie(self, v1: i32) -> bool:\n'
                              '        pass\n',
                              '',
                              '',
                              {})

        self.assert_in('class Foo : public Object {\n'
                       '\n'
                       'public:\n'
                       '\n'
                       '    virtual void bar(void) = 0;\n'
                       '\n'
                       '    virtual bool fie(i32 v1) = 0;\n'
                       '\n'
                       '};\n',
                       source)

    def test_declare_trait_with_method_body(self):
        # ToDo: Method bodies should eventually be supported, but not
        #       right now.
        with self.assertRaises(Exception) as cm:
            transpile('@trait\n'
                      'class Foo:\n'
                      '    def bar(self):\n'
                      '        print()\n',
                      '',
                      '',
                      {})

        self.assertEqual(
            remove_ansi(str(cm.exception)),
            '  File "", line 3\n'
            '        def bar(self):\n'
            '        ^\n'
            "LanguageError: trait method body must be 'pass'\n")

    def test_implement_trait_in_class(self):
        _, source = transpile('@trait\n'
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
                              '        print()\n',
                              '',
                              '',
                              {})

        self.assert_in('class Foo : public Base {', source)
        self.assert_in('class Bar : public Base, public Base2 {', source)

    def test_match_i32(self):
        _, source = transpile('def foo(value: i32):\n'
                              '    match value:\n'
                              '        case 0:\n'
                              '            print(value)\n'
                              '        case _:\n'
                              '            print(value)\n',
                              '',
                              '',
                              {})

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
        _, source = transpile('def foo(value: string):\n'
                              '    match value:\n'
                              '        case "a":\n'
                              '            print(value)\n'
                              '        case "b":\n'
                              '            print(value)\n',
                              '',
                              '',
                              {})

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
        _, source = transpile('def foo() -> i32:\n'
                              '    return 1\n'
                              'def bar():\n'
                              '    match foo():\n'
                              '        case 0:\n'
                              '            print(0)\n',
                              '',
                              '',
                              {})

        self.assertRegex(source,
                         r'void bar\(void\)\n'
                         r'{\n'
                         r'    auto subject_\d+ = foo\(\);\n'
                         r'    if \(subject_\d+ == 0\) {\n'
                         r'        std::cout << 0 << std::endl;\n'
                         r'    }\n'
                         r'}\n')

    def test_match_trait(self):
        _, source = transpile('@trait\n'
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
                              '            print(value)\n',
                              '',
                              '',
                              {})

        self.assertRegex(
            source,
            'void foo\(const std::shared_ptr<Base>& base\)\n'
            '{\n'
            '    auto casted_\d+ = std::dynamic_pointer_cast<Foo>\(base\);\n'
            '    if \(casted_\d+\) {\n'
            '        std::cout << "foo" << std::endl;\n'
            '    } else {\n'
            '        auto casted_\d+ = std::dynamic_pointer_cast<Bar>\(base\);\n'
            '        if \(casted_\d+\) {\n'
            '            auto value = std::move\(casted_\d+\);\n'
            '            std::cout << value << std::endl;\n'
            '        } else {\n'
            '            auto casted_\d+ = std::dynamic_pointer_cast<Fie>\(base\);\n'
            '            if \(casted_\d+\) {\n'
            '                auto value = std::move\(casted_\d+\);\n'
            '                std::cout << value << std::endl;\n'
            '            }\n'
            '        }\n'
            '    }\n'
            '}\n')

    def test_inferred_type_integer_assignment(self):
        _, source = transpile('def foo():\n'
                              '    value_1 = 1\n'
                              '    value_2 = -1\n'
                              '    value_3 = +1\n'
                              '    print(value_1, value_2, value_3)\n',
                              '',
                              '',
                              {})

        self.assert_in(
            'void foo(void)\n'
            '{\n'
            '    i64 value_1 = 1;\n'
            '    i64 value_2 = -(1);\n'
            '    i64 value_3 = +(1);\n'
            '    std::cout << value_1 << " " << value_2 << " " << value_3 << std::endl;\n'
            '}\n',
            source)

    def test_inferred_type_string_assignment(self):
        _, source = transpile('def foo():\n'
                              '    value = "a"\n'
                              '    print(value)\n',
                              '',
                              '',
                              {})

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    String value("a");\n'
                       '    std::cout << value << std::endl;\n'
                       '}\n',
                       source)

    def test_inferred_type_bool_assignment(self):
        _, source = transpile('def foo():\n'
                              '    value = True\n'
                              '    print(value)\n',
                              '',
                              '',
                              {})

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    bool value = true;\n'
                       '    std::cout << value << std::endl;\n'
                       '}\n',
                       source)

    def test_inferred_type_float_assignment(self):
        _, source = transpile('def foo():\n'
                              '    value = 6.44\n'
                              '    print(value)\n',
                              '',
                              '',
                              {})

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    f64 value = 6.44;\n'
                       '    std::cout << value << std::endl;\n'
                       '}\n',
                       source)

    def test_inferred_type_class_assignment(self):
        _, source = transpile('class A:\n'
                              '    pass\n'
                              'def foo():\n'
                              '    value = A()\n'
                              '    print(value)\n',
                              '',
                              '',
                              {})

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '    auto value = std::make_shared<A>();\n'
                       '    std::cout << value << std::endl;\n'
                       '}\n',
                       source)

    def test_string_as_function_parameter(self):
        _, source = transpile('def foo(value: string) -> string:\n'
                              '    return value\n'
                              'def bar():\n'
                              '    print(foo("Cat"))\n',
                              '',
                              '',
                              {})

        self.assert_in('void bar(void)\n'
                       '{\n'
                       '    std::cout << foo("Cat") << std::endl;\n'
                       '}\n',
                       source)
