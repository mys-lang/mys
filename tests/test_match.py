from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_match(self):
        build_and_test_module('match')

    def test_match_class(self):
        # Should probably be supported eventually.
        self.assert_transpile_raises(
            'class Foo:\n'
            '    x: i32\n'
            'def foo(v: Foo):\n'
            '    match v:\n'
            '        case Foo(x=1):\n'
            '            pass\n',
            '  File "", line 4\n'
            '        match v:\n'
            '              ^\n'
            "CompileError: matching classes if not supported\n")

    def test_match_wrong_case_type(self):
        self.assert_transpile_raises(
            'def foo(v: i32):\n'
            '    match v:\n'
            '        case 1:\n'
            '            pass\n'
            '        case "":\n'
            '            pass\n',
            '  File "", line 5\n'
            '            case "":\n'
            '                 ^\n'
            "CompileError: expected a 'i32', got a 'string'\n")

    def test_match_pattern_condition(self):
        self.assert_transpile_raises(
            'def foo(x: i32, y: u8):\n'
            '    match x:\n'
            '        case 1 if y == 2:\n'
            '            pass\n',
            '  File "", line 3\n'
            '            case 1 if y == 2:\n'
            '                      ^\n'
            "CompileError: guards are not supported\n")

    def test_match_trait_pattern_condition(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Base:\n'
            '    pass\n'
            'class Foo(Base):\n'
            '    pass\n'
            'def foo(base: Base):\n'
            '    match base:\n'
            '        case Foo() if False:\n'
            '            print("foo")\n',
            '  File "", line 8\n'
            '            case Foo() if False:\n'
            '                          ^\n'
            "CompileError: guards are not supported\n")

    def test_match_trait_pattern_not_class_1(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Base:\n'
            '    pass\n'
            'class Foo(Base):\n'
            '    pass\n'
            'def foo(base: Base):\n'
            '    match base:\n'
            '        case Foo as e:\n'
            '            print(e)\n',
            '  File "", line 8\n'
            '            case Foo as e:\n'
            '                 ^\n'
            "CompileError: trait match patterns must be class objects\n")

    def test_match_trait_pattern_not_class_2(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Base:\n'
            '    pass\n'
            'class Foo(Base):\n'
            '    pass\n'
            'def foo(base: Base):\n'
            '    match base:\n'
            '        case Foo:\n'
            '            pass\n',
            '  File "", line 8\n'
            '            case Foo:\n'
            '                 ^\n'
            "CompileError: trait match patterns must be class objects\n")

    def test_match_trait_pattern_with_arg(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Base:\n'
            '    pass\n'
            'class Foo(Base):\n'
            '    x: i64\n'
            'def foo(base: Base):\n'
            '    match base:\n'
            '        case Foo(5):\n'
            '            pass\n',
            '  File "", line 8\n'
            '            case Foo(5):\n'
            '                 ^\n'
            "CompileError: only keyword arguments can be matched\n")

    def test_match_trait_pattern_with_non_constant_arg(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Base:\n'
            '    pass\n'
            'class Foo(Base):\n'
            '    x: i64\n'
            'def foo(base: Base):\n'
            '    v: i64 = 5\n'
            '    match base:\n'
            '        case Foo(x=v):\n'
            '            pass\n',
            '  File "", line 9\n'
            '            case Foo(x=v):\n'
            '                 ^\n'
            "CompileError: only constants can be matched\n")

    def test_bare_integer_in_match_case(self):
        self.assert_transpile_raises(
            'def foo(a: u8):\n'
            '    match a:\n'
            '        case 1:\n'
            '            1\n',
            '  File "", line 4\n'
            '                1\n'
            '                ^\n'
            "CompileError: bare integer\n")
