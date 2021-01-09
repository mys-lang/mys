from .utils import build_and_test_module
from .utils import TestCase
from .utils import transpile_source
from .utils import remove_ansi


class Test(TestCase):

    def test_enums(self):
        build_and_test_module('enums')

    def test_invalid_string_enum_member_value(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A = "s"\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        A = "s"\n'
            '            ^\n'
            "CompileError: invalid enum member value\n")

    def test_invalid_enum_member_name(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    V1, V2 = 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        V1, V2 = 1\n'
            '        ^\n'
            "CompileError: invalid enum member syntax\n")

    def test_invalid_enum_member_value_plus_sign(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A = +1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        A = +1\n'
            '            ^\n'
            "CompileError: invalid enum member value\n")

    def test_invalid_enum_member_value_variable(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A = b\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        A = b\n'
            '            ^\n'
            "CompileError: invalid enum member value\n")

    def test_non_pascal_case_enum_member_name(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    aB = 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        aB = 1\n'
            '        ^\n'
            "CompileError: enum member names must be pascal case\n")

    def test_invalid_enum_member_syntax(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    1 + 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        1 + 1\n'
            '        ^\n'
            "CompileError: invalid enum member syntax\n")

    def test_empty_enum_type(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum()\n'
                             'class Foo:\n'
                             '    Ab = 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    @enum()\n'
            '     ^\n'
            "CompileError: one parameter expected, got 0\n")

    def test_bad_enum_type_f32(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum(f32)\n'
                             'class Foo:\n'
                             '    Ab = 1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    @enum(f32)\n'
            '          ^\n'
            "CompileError: integer type expected, not 'f32'\n")

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

        self.assert_exception_string(
            cm,
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

        self.assert_exception_string(
            cm,
            '  File "", line 5\n'
            '        print(Foo(1, 2))\n'
            '              ^\n'
            "CompileError: expected 1 parameter, got 2\n")

    def test_not_enum(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class Foo:\n'
                             '    A = 1\n'
                             'def foo():\n'
                             '    print(not Foo.A)\n')

        self.assert_exception_string(
            cm,
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

        self.assert_exception_string(
            cm,
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

        self.assert_exception_string(
            cm,
            '  File "", line 5\n'
            '        C = 0\n'
            '            ^\n'
            "CompileError: enum member value lower than for previous member\n")

    def test_enum_pascal_case(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('@enum\n'
                             'class foo:\n'
                             '    A\n')

        self.assert_exception_string(
            cm,
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

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '        def a(self):\n'
            '        ^\n'
            "CompileError: invalid enum member syntax\n")
