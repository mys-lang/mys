from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_loops(self):
        build_and_test_module('loops')

    def test_for_else_not_supported(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    for _ in range(3):\n'
            '        pass\n'
            '    else:\n'
            '        pass\n',
            '  File "", line 2\n'
            '        for _ in range(3):\n'
            '        ^\n'
            "CompileError: for else clause not supported\n")

    def test_while_else_not_supported(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    while False:\n'
            '        pass\n'
            '    else:\n'
            '        pass\n',
            '  File "", line 2\n'
            '        while False:\n'
            '        ^\n'
            "CompileError: while else clause not supported\n")
