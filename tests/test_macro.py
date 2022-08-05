from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_macro(self):
        build_and_test_module('macro')

    def test_macros_not_allowed_in_traits(self):
        self.assert_transpile_raises(
            'trait Foo:\n'
            '    macro FOO(self):\n'
            '        pass\n',
            '  File "", line 2\n'
            '        macro FOO(self):\n'
            '        ^\n'
            "CompileError: traits cannot have macro methods\n")
