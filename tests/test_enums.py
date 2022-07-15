from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_enums(self):
        build_and_test_module('enums')

    def test_invalid_string_enum_member_value(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    A = "s"\n',
            '  File "", line 2\n'
            '        A = "s"\n'
            '            ^\n'
            "CompileError: invalid enum member value\n")

    def test_invalid_enum_member_name(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    V1, V2 = 1\n',
            '  File "", line 2\n'
            '        V1, V2 = 1\n'
            '        ^\n'
            "CompileError: invalid enum member syntax\n")

    def test_invalid_enum_member_value_plus_sign(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    A = +1\n',
            '  File "", line 2\n'
            '        A = +1\n'
            '            ^\n'
            "CompileError: invalid enum member value\n")

    def test_invalid_enum_member_value_variable(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    A = b\n',
            '  File "", line 2\n'
            '        A = b\n'
            '            ^\n'
            "CompileError: invalid enum member value\n")

    def test_non_pascal_case_enum_member_name(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    aB = 1\n',
            '  File "", line 2\n'
            '        aB = 1\n'
            '        ^\n'
            "CompileError: enum member names must be pascal case\n")

    def test_invalid_enum_member_syntax(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    1 + 1\n',
            '  File "", line 2\n'
            '        1 + 1\n'
            '        ^\n'
            "CompileError: invalid enum member syntax\n")

    def test_bad_enum_type_f32(self):
        self.assert_transpile_raises(
            'enum Foo(f32):\n'
            '    Ab = 1\n',
            '  File "", line 1\n'
            '    enum Foo(f32):\n'
            '             ^\n'
            "CompileError: integer type expected, not 'f32'\n")

    def test_enum_float_value(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    A = 1\n'
            'func foo():\n'
            '    print(Foo(0.0))\n',
            '  File "", line 4\n'
            '        print(Foo(0.0))\n'
            '                  ^\n'
            "CompileError: cannot convert float to 'i64'\n")

    def test_enum_too_many_parameters(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    A = 1\n'
            'func foo():\n'
            '    print(Foo(1, 2))\n',
            '  File "", line 4\n'
            '        print(Foo(1, 2))\n'
            '              ^\n'
            "CompileError: expected 1 parameter, got 2\n")

    def test_not_enum(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    A = 1\n'
            'func foo():\n'
            '    print(not Foo.A)\n',
            '  File "", line 4\n'
            '        print(not Foo.A)\n'
            '                  ^\n'
            "CompileError: expected a 'bool', got a 'foo.lib.Foo'\n")

    def test_enum_member_value_lower_than_previous_1(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    A = 0\n'
            '    B = -1\n',
            '  File "", line 3\n'
            '        B = -1\n'
            '            ^\n'
            "CompileError: enum member value lower than for previous member\n")

    def test_enum_member_value_lower_than_previous_2(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    A\n'
            '    B\n'
            '    C = 0\n',
            '  File "", line 4\n'
            '        C = 0\n'
            '            ^\n'
            "CompileError: enum member value lower than for previous member\n")

    def test_enum_pascal_case(self):
        self.assert_transpile_raises(
            'enum foo:\n'
            '    A\n',
            '  File "", line 1\n'
            '    enum foo:\n'
            '    ^\n'
            "CompileError: enum names must be pascal case\n")

    def test_enum_bad_member_syntax(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    func a(self):\n'
            '        pass\n',
            '  File "", line 2\n'
            '        func a(self):\n'
            '        ^\n'
            "CompileError: invalid enum member syntax\n")

    def test_use_missing_enum_value_in_print(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    Apa = 1\n'
            'func foo():\n'
            '    print(Foo.APA)\n',
            '  File "", line 4\n'
            '        print(Foo.APA)\n'
            '              ^\n'
            "CompileError: enum has no member 'APA'\n")

    def test_use_missing_enum_value_in_comparision(self):
        self.assert_transpile_raises(
            'enum Foo:\n'
            '    Apa = 1\n'
            'func foo():\n'
            '    if Foo.APA == Foo.Apa:\n'
            '        pass\n',
            '  File "", line 4\n'
            '        if Foo.APA == Foo.Apa:\n'
            '           ^\n'
            "CompileError: enum has no member 'APA'\n")
