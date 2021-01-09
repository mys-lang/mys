from .utils import TestCase


class Test(TestCase):

    def test_while_non_bool(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    while 1:\n'
            '        pass\n',
            '  File "", line 2\n'
            "        while 1:\n"
            '              ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

    def test_bare_integer_in_while(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    while True:\n'
            '        1\n',
            '  File "", line 3\n'
            '            1\n'
            '            ^\n'
            "CompileError: bare integer\n")

    def test_variable_defined_in_while_can_not_be_used_after_1(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    while False:\n'
            '        v = 1\n'
            '    print(v)\n',
            '  File "", line 4\n'
            '        print(v)\n'
            '              ^\n'
            "CompileError: undefined variable 'v'\n")
