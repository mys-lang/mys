from .utils import TestCase


class Test(TestCase):

    def test_value_if_cond_else_value_1(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    print(1 if 1 else 2)\n',
            '  File "", line 2\n'
            '        print(1 if 1 else 2)\n'
            '                   ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

    def test_value_if_cond_else_value_2(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    print(1 if True else "")\n',
            '  File "", line 2\n'
            '        print(1 if True else "")\n'
            '                             ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_if_cond_as_non_bool(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    if 1:\n'
            '        pass\n',
            '  File "", line 2\n'
            '        if 1:\n'
            '           ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

    def test_bare_name_in_if(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    a: i32 = 0\n'
            '    if True:\n'
            '        a\n',
            '  File "", line 4\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_bare_name_in_else(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    a: i32 = 0\n'
            '    if True:\n'
            '        pass\n'
            '    else:\n'
            '        a\n',
            '  File "", line 6\n'
            '            a\n'
            '            ^\n'
            "CompileError: bare name\n")

    def test_variable_defined_in_if_can_not_be_used_after(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    if True:\n'
            '        v = 1\n'
            '    print(v)\n',
            '  File "", line 4\n'
            '        print(v)\n'
            '              ^\n'
            "CompileError: undefined variable 'v'\n")

    def test_if_else_different_variable_type_1(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    if False:\n'
            '        x: i8 = 1\n'
            '    else:\n'
            '        x: i16 = 2\n'
            '    print(x)\n',
            '  File "", line 6\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_if_else_different_variable_type_2(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    if False:\n'
            '        x = 1\n'
            '    elif True:\n'
            '        x = 2\n'
            '    else:\n'
            '        if True:\n'
            '            x = ""\n'
            '        else:\n'
            '            x = 3\n'
            '    print(x)\n',
            '  File "", line 11\n'
            '        print(x)\n'
            '              ^\n'
            "CompileError: undefined variable 'x'\n")

    def test_value_in_all_branches_with_while(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    if False:\n'
            '        value = -1\n'
            '    else:\n'
            '        while False:\n'
            '            value = 1\n'
            '    assert value == -2\n',
            '  File "", line 7\n'
            '        assert value == -2\n'
            '               ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_value_in_all_branches_with_for(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    if False:\n'
            '        value = -1\n'
            '    else:\n'
            '        for value in range(2):\n'
            '            value += 1\n'
            '    assert value == -2\n',
            '  File "", line 7\n'
            '        assert value == -2\n'
            '               ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_value_in_all_branches_with_for_2(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    if False:\n'
            '        value = -1\n'
            '    else:\n'
            '        for _ in range(2):\n'
            '            value = 1\n'
            '    assert value == -2\n',
            '  File "", line 7\n'
            '        assert value == -2\n'
            '               ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_value_in_all_branches_with_while_raises(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    if False:\n'
            '        value = -1\n'
            '    else:\n'
            '        while True:\n'
            '            raise ValueError()\n'
            '    assert value == -2\n',
            '  File "", line 7\n'
            '        assert value == -2\n'
            '               ^\n'
            "CompileError: undefined variable 'value'\n")

    def test_value_in_all_branches_with_for_raises(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    if False:\n'
            '        value = -1\n'
            '    else:\n'
            '        for _ in range(1):\n'
            '            raise ValueError()\n'
            '    assert value == -2\n',
            '  File "", line 7\n'
            '        assert value == -2\n'
            '               ^\n'
            "CompileError: undefined variable 'value'\n")
