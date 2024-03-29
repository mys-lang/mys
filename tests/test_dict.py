from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_dict(self):
        build_and_test_module('dict')

    def test_return_dict_from_function_returning_list(self):
        self.assert_transpile_raises(
            'class Foo:\n'
            '    pass\n'
            'func foo() -> [(string, Foo)]:\n'
            '    return {1: 2}',
            '  File "", line 4\n'
            '        return {1: 2}\n'
            '               ^\n'
            "CompileError: cannot convert dict to '[(string, foo.lib.Foo)]'\n")

    def test_wrong_dict_key_type(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v = {1: 5}\n'
            '    v["a"] = 4\n',
            '  File "", line 3\n'
            '        v["a"] = 4\n'
            '          ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_bad_dict_key_type(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v: {Foo: bool} = None\n',
            # Should probably say that Foo is not defined.
            '  File "", line 2\n'
            '        v: {Foo: bool} = None\n'
            '           ^\n'
            "CompileError: undefined type '{Foo: bool}'\n")

    def test_dict_value_type_not_defined(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v: {bool: Foo} = None\n',
            # Should probably say that Foo is not defined.
            '  File "", line 2\n'
            '        v: {bool: Foo} = None\n'
            '           ^\n'
            "CompileError: undefined type '{bool: Foo}'\n")

    def test_wrong_dict_value_type(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v = {1: 5}\n'
            '    v[2] = 2.5\n',
            '  File "", line 3\n'
            '        v[2] = 2.5\n'
            '               ^\n'
            "CompileError: cannot convert float to 'i64'\n")

    def test_dict_init_key_types_mismatch_1(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v: {i64: i64} = {1: 5, True: 0}\n'
            '    print(v)\n',
            '  File "", line 2\n'
            '        v: {i64: i64} = {1: 5, True: 0}\n'
            '                               ^\n'
            "CompileError: expected a 'i64', got a 'bool'\n")

    def test_dict_init_key_types_mismatch_2(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v = {True: 5, 1: 4}\n'
            '    print(v)\n',
            '  File "", line 2\n'
            '        v = {True: 5, 1: 4}\n'
            '                      ^\n'
            "CompileError: cannot convert integer to 'bool'\n")

    def test_dict_init_value_types_mismatch_1(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v: {bool: i64} = {True: 5, False: "a"}\n'
            '    print(v)\n',
            '  File "", line 2\n'
            '        v: {bool: i64} = {True: 5, False: "a"}\n'
            '                                          ^\n'
            "CompileError: expected a 'i64', got a 'string'\n")

    def test_dict_init_value_types_mismatch_2(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v = {True: i8(5), False: u8(4)}\n'
            '    print(v)\n',
            '  File "", line 2\n'
            '        v = {True: i8(5), False: u8(4)}\n'
            '                                 ^\n'
            "CompileError: expected a 'i8', got a 'u8'\n")

    def test_only_iterate_over_dict_pairs_supported(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    for item in {1: 2}:\n'
            '        print(item)\n',
            '  File "", line 2\n'
            '        for item in {1: 2}:\n'
            '            ^\n'
            "CompileError: iteration over dict must be done on key/value tuple\n")

    def test_key_type_cannot_be_optional_variable(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v: {i64?: i64} = {}\n',
            '  File "", line 2\n'
            '        v: {i64?: i64} = {}\n'
            '            ^\n'
            "CompileError: dict key type cannot be optional\n")

    def test_value_type_cannot_be_optional_variable(self):
        self.assert_transpile_raises(
            'func foo():\n'
            '    v: {i64: i64?} = {}\n',
            '  File "", line 2\n'
            '        v: {i64: i64?} = {}\n'
            '                 ^\n'
            "CompileError: dict value type cannot be optional\n")

    def test_key_type_cannot_be_optional_global(self):
        self.assert_transpile_raises(
            'FOO: {i64?: i64} = {}\n',
            '  File "", line 1\n'
            '    FOO: {i64?: i64} = {}\n'
            '          ^\n'
            "CompileError: dict key type cannot be optional\n")

    def test_value_type_cannot_be_optional_global(self):
        self.assert_transpile_raises(
            'FOO: {i64: i64?} = {}\n',
            '  File "", line 1\n'
            '    FOO: {i64: i64?} = {}\n'
            '               ^\n'
            "CompileError: dict value type cannot be optional\n")

    def test_key_type_cannot_be_optional_function_parameter(self):
        self.assert_transpile_raises(
            'func foo(x: {i64?: i64}):\n'
            '    pass\n',
            '  File "", line 1\n'
            '    func foo(x: {i64?: i64}):\n'
            '                 ^\n'
            "CompileError: dict key type cannot be optional\n")

    def test_value_type_cannot_be_optional_function_parameter(self):
        self.assert_transpile_raises(
            'func foo(x: {i64: i64?}):\n'
            '    pass\n',
            '  File "", line 1\n'
            '    func foo(x: {i64: i64?}):\n'
            '                      ^\n'
            "CompileError: dict value type cannot be optional\n")
