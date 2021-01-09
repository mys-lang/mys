from mys.transpiler import TranspilerError
from .utils import transpile_source
from .utils import TestCase


class Test(TestCase):

    def test_while_non_bool(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    while 1:\n'
                             '        pass\n')

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            "        while 1:\n"
            '              ^\n'
            "CompileError: expected a 'bool', got a 'i64'\n")

    def test_bare_integer_in_while(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    while True:\n'
                             '        1\n')

        self.assert_exception_string(
            cm,
            '  File "", line 3\n'
            '            1\n'
            '            ^\n'
            "CompileError: bare integer\n")

    def test_variable_defined_in_while_can_not_be_used_after_1(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def foo():\n'
                             '    while False:\n'
                             '        v = 1\n'
                             '    print(v)\n')

        self.assert_exception_string(
            cm,
            '  File "", line 4\n'
            '        print(v)\n'
            '              ^\n'
            "CompileError: undefined variable 'v'\n")
