from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_infer_types(self):
        build_and_test_module('infer_types')

    def test_infer_type_from_none(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    a = None\n',
            '  File "", line 2\n'
            "        a = None\n"
            '        ^\n'
            "CompileError: cannot infer variable type\n")

    def test_dict_without_type(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    v = {}\n'
            '    print(v)\n',
            '  File "", line 2\n'
            '        v = {}\n'
            '        ^\n'
            "CompileError: cannot infer variable type\n")
