from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_comprehensions(self):
        build_and_test_module('comprehensions')

    def test_list_comprehension_two_for_loops(self):
        self.assert_transpile_raises(
            'def foo() -> [i64]:\n'
            "    return [x * y for x in [1] for y in [2]]\n",
            '  File "", line 2\n'
            '        return [x * y for x in [1] for y in [2]]\n'
            "               ^\n"
            'CompileError: only one for-loop allowed\n')

    def test_comprehension_over_tuple(self):
        self.assert_transpile_raises(
            'def foo() -> [i64]:\n'
            "    return [x for x in (1, True)]\n",
            '  File "", line 2\n'
            '        return [x for x in (1, True)]\n'
            "                           ^\n"
            'CompileError: iteration over tuples not allowed\n')
