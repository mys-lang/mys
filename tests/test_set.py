from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_set(self):
        build_and_test_module('set')

    def test_type_error(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    a: u32 = {1}\n'
            '    print(a)\n',
            '  File "", line 2\n'
            '        a: u32 = {1}\n'
            '                 ^\n'
            "CompileError: cannot convert set to 'u32'\n")
