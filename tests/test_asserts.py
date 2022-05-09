from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_asserts(self):
        build_and_test_module('asserts')

    def test_assert_function_that_does_not_return_any_value(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    pass\n'
            'func bar():\n'
            '    assert foo()\n',
            '  File "", line 4\n'
            '        assert foo()\n'
            '               ^\n'
            "CompileError: expected a 'bool', got 'None'\n")
