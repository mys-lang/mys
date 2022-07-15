from mys.parser import ast
from mys.transpiler.definitions import find_definitions

from .utils import TestCase


class Test(TestCase):

    def test_string(self):
        definitions = find_definitions(
            ast.parse(
                'VAR1: i32 = 1\n'
                '_VAR2: [bool] = [True, False]\n'
                'enum Enum1:\n'
                '    A\n'
                '    B\n'
                '    C\n'
                '    D = 100\n'
                '    E\n'
                'enum _Enum2(u8):\n'
                '    Aa = 1\n'
                '    Bb = 5\n'
                'trait Trait1:\n'
                '    func foo(self):\n'
                '        pass\n'
                'class Class1:\n'
                '    m1: i32\n'
                '    m2: [i32]\n'
                '    _m3: i32\n'
                '    func foo(self):\n'
                '        pass\n'
                '    func bar(self, a: i32) -> i32:\n'
                '        return a\n'
                '    func bar(self, a: i32, b: (bool, u8)) -> [i32]:\n'
                '        return a\n'
                '    func fie(a: i32):\n'
                '        pass\n'
                'class Class2:\n'
                '    pass\n'
                '@generic(T)\n'
                'class _Class3:\n'
                '    a: T\n'
                'func func1(a: i32, b: bool, c: Class1, d: [(u8, string)]):\n'
                '    pass\n'
                'func func2() -> bool:\n'
                '    pass\n'
                '@raises(TypeError)\n'
                'func func3() -> [i32]:\n'
                '    raise TypeError()\n'
                '@generic(T1, T2)\n'
                'func _func4(a: T1, b: T2):\n'
                '    pass\n'),
            [],
            None,
            None)

        self.assertEqual(
            str(definitions),
            "Definitions:\n"
            "  Variables:\n"
            "    VAR1: i32\n"
            "    _VAR2: ['bool']\n"
            "  Classes:\n"
            "    Class1():\n"
            "      m1: i32\n"
            "      m2: ['i32']\n"
            "      _m3: i32\n"
            "      foo() -> None\n"
            "      bar(a: i32) -> i32\n"
            "      bar(a: i32, b: ('bool', 'u8')) -> ['i32']\n"
            "    Class2():\n"
            "    _Class3():\n"
            "      a: T\n"
            "  Traits:\n"
            "    Trait1:\n"
            "      foo() -> None\n"
            "  Enums:\n"
            "    Enum1\n"
            "    _Enum2\n"
            "  Functions:\n"
            "    func1(a: i32, b: bool, c: Class1, d: [('u8', 'string')]) -> None\n"
            "    func2() -> bool\n"
            "    func3() -> ['i32']\n"
            "    _func4(a: T1, b: T2) -> None")
