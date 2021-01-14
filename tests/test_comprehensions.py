from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_comprehensions(self):
        build_and_test_module('comprehensions')

    def test_list_comprehension_not_implemented(self):
        self.assert_transpile_raises(
            'def foo() -> [i64]:\n'
            "    return [v for v in [1]]\n",
            '  File "", line 2\n'
            '        return [v for v in [1]]\n'
            "               ^\n"
            'CompileError: list comprehension is not implemented\n')

    def test_dict_comprehension_not_implemented(self):
        self.assert_transpile_raises(
            'def foo() -> {i64: i64}:\n'
            "    return {k: v for k, v in [(1, 2)]}\n",
            '  File "", line 2\n'
            '        return {k: v for k, v in [(1, 2)]}\n'
            "               ^\n"
            'CompileError: dict comprehension is not implemented\n')

    def test_set_comprehension_not_implemented(self):
        self.assert_transpile_raises(
            'def foo():\n'
            "    print({v for v in [1]})\n",
            '  File "", line 2\n'
            '        print({v for v in [1]})\n'
            "              ^\n"
            'CompileError: set comprehension is not implemented\n')
