from mys.transpiler import TranspilerError
from mys.transpiler.utils import make_function_name

from .utils import TestCase
from .utils import build_and_test_module
from .utils import remove_ansi
from .utils import transpile_source


class Test(TestCase):

    def test_functions(self):
        build_and_test_module('functions')

    def test_invalid_main_argument(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def main(argv: i32): pass',
                             has_main=True)

        self.assert_exception_string(
            cm,
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
        with self.assertRaises(TranspilerError) as cm:
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
        with self.assertRaises(TranspilerError) as cm:
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

    def test_empty_function(self):
        source = transpile_source('def foo():\n'
                                  '    pass\n')

        self.assert_in('void foo(void)\n'
                       '{\n'
                       '\n'
                       '}\n',
                       source)

    def test_undefined_function(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    bar()\n',
            '  File "", line 2\n'
            '        bar()\n'
            '        ^\n'
            "CompileError: undefined function 'bar'\n")

    def test_test_can_not_take_any_values(self):
        self.assert_transpile_raises(
            '@test(H)\n'
            'def foo():\n'
            '    pass\n',
            '  File "", line 1\n'
            '    @test(H)\n'
            '     ^\n'
            "CompileError: no parameters expected\n")

    def test_non_snake_case_function(self):
        self.assert_transpile_raises(
            'def Apa():\n'
            '    pass\n',
            '  File "", line 1\n'
            '    def Apa():\n'
            '    ^\n'
            "CompileError: function names must be snake case\n")

    def test_non_snake_case_function_parameter_name(self):
        self.assert_transpile_raises(
            'def foo(A: i32):\n'
            '    pass\n',
            '  File "", line 1\n'
            '    def foo(A: i32):\n'
            '            ^\n'
            "CompileError: parameter names must be snake case\n")

    def test_missing_function_parameter_type(self):
        self.assert_transpile_raises(
            'def foo(x):\n'
            '    pass\n',
            '  File "", line 1\n'
            '    def foo(x):\n'
            '            ^\n'
            "CompileError: parameters must have a type\n")

    def test_test_function_with_parameter(self):
        self.assert_transpile_raises(
            '@test\n'
            'def test_foo(v: bool):\n'
            '    pass\n',
            '  File "", line 2\n'
            '    def test_foo(v: bool):\n'
            '    ^\n'
            "CompileError: test functions takes no parameters\n")

    def test_test_function_with_return_value(self):
        self.assert_transpile_raises(
            '@test\n'
            'def test_foo() -> bool:\n'
            '    return True\n',
            '  File "", line 2\n'
            '    def test_foo() -> bool:\n'
            '    ^\n'
            "CompileError: test functions must not return any value\n")

    def test_function_name(self):
        datas = [
            ('foo', [], None, 'foo'),
            ('foo', ['i64'], None, 'foo_i64'),
            ('foo', ['i64'], 'bool', 'foo_i64_r_bool'),
            ('foo',
             ['i64', ('bool', 'string')],
             ['bool'],
             'foo_i64_tb_bool_string_te_r_lb_bool_le'),
            ('kalle_kula',
             ['Foo', {'bool': 'Bar'}],
             None,
             'kalle_kula_Foo_db_bool_cn_Bar_de')
        ]

        for name, params, returns, expected in datas:
            actual = make_function_name(name, params, returns)
            self.assertEqual(actual, expected)

    def test_ambigious_call_in_assert(self):
        self.assert_transpile_raises(
            'def foo(a: i64) -> u8:\n'
            '    return 1\n'
            'def foo(a: i32) -> u8:\n'
            '    return 2\n'
            'def bar():\n'
            '    assert foo(1) == 1\n',
            '  File "", line 6\n'
            '        assert foo(1) == 1\n'
            '               ^\n'
            "CompileError: ambigious function call\n")

    def test_ambigious_call(self):
        self.assert_transpile_raises(
            'def foo(a: i64) -> u8:\n'
            '    return 1\n'
            'def foo(a: i32) -> u8:\n'
            '    return 2\n'
            'def bar():\n'
            '    foo(1)\n',
            '  File "", line 6\n'
            '        foo(1)\n'
            '        ^\n'
            "CompileError: ambigious function call\n")

    def test_ambigious_call_default(self):
        self.assert_transpile_raises(
            'def foo() -> u8:\n'
            '    return 1\n'
            'def foo(a: i32 = 2) -> u8:\n'
            '    return 2\n'
            'def bar():\n'
            '    foo()\n',
            '  File "", line 6\n'
            '        foo()\n'
            '        ^\n'
            "CompileError: ambigious function call\n")
