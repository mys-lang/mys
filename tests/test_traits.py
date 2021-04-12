from mys.transpiler import Source
from mys.transpiler import TranspilerError
from mys.transpiler import transpile

from .utils import TestCase
from .utils import build_and_test_module
from .utils import transpile_early_header


class Test(TestCase):

    def test_traits(self):
        build_and_test_module('traits')

    def test_define_empty_trait(self):
        header = transpile_early_header('@trait\n'
                                        'class Foo:\n'
                                        '    pass\n')
        self.assert_in('class Foo : public mys::Object {\n'
                       'public:\n'
                       '    virtual ~Foo() {}\n'
                       '};\n',
                       header)

    def test_define_trait_with_member(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Foo:\n'
            '    a: i32\n',
            '  File "", line 3\n'
            '        a: i32\n'
            '        ^\n'
            "CompileError: traits cannot have members\n")

    def test_define_trait_with_parameter(self):
        self.assert_transpile_raises(
            '@trait(u32)\n'
            'class Foo:\n'
            '    pass\n',
            '  File "", line 1\n'
            '    @trait(u32)\n'
            '     ^\n'
            "CompileError: no parameters expected\n")

    def test_define_trait_with_same_name_twice(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Foo:\n'
            '    pass\n'
            '@trait\n'
            'class Foo:\n'
            '    pass\n',
            '  File "", line 5\n'
            '    class Foo:\n'
            '    ^\n'
            "CompileError: there is already a trait called 'Foo'\n")

    def test_define_trait_with_same_name_as_class(self):
        self.assert_transpile_raises(
            'class Foo:\n'
            '    pass\n'
            '@trait\n'
            'class Foo:\n'
            '    pass\n',
            '  File "", line 4\n'
            '    class Foo:\n'
            '    ^\n'
            "CompileError: there is already a class called 'Foo'\n")

    def test_trait_does_not_exist(self):
        self.assert_transpile_raises(
            'class Foo(Bar):\n'
            '    pass\n',
            '  File "", line 1\n'
            '    class Foo(Bar):\n'
            '              ^\n'
            "CompileError: trait does not exist\n")

    def test_wrong_function_parameter_type_trait(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Base:\n'
            '    pass\n'
            '@trait\n'
            'class WrongBase:\n'
            '    pass\n'
            'class Foo(Base):\n'
            '    pass\n'
            'def foo(a: WrongBase):\n'
            '    pass\n'
            'def bar():\n'
            '    foo(Foo())\n',
            '  File "", line 12\n'
            '        foo(Foo())\n'
            '            ^\n'
            "CompileError: 'foo.lib.Foo' does not implement trait "
            "'foo.lib.WrongBase'\n")

    def test_trait_init(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Foo:\n'
            '    def __init__(self):\n'
            '        pass\n',
            '  File "", line 3\n'
            '        def __init__(self):\n'
            '        ^\n'
            "CompileError: traits cannot have an __init__ method\n")

    def test_pure_trait_method_not_implemented_pass(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Base:\n'
            '    def foo(self):\n'
            '        pass\n'
            'class Foo(Base):\n'
            '    pass\n',
            '  File "", line 5\n'
            '    class Foo(Base):\n'
            '              ^\n'
            "CompileError: pure trait method 'foo' is not implemented\n")

    def test_pure_trait_method_not_implemented_many_pass(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Base:\n'
            '    def foo(self):\n'
            '        pass\n'
            '        pass\n'
            '        pass\n'
            'class Foo(Base):\n'
            '    pass\n',
            '  File "", line 7\n'
            '    class Foo(Base):\n'
            '              ^\n'
            "CompileError: pure trait method 'foo' is not implemented\n")

    def test_pure_trait_method_not_implemented_docstring(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Base:\n'
            '    def foo(self):\n'
            '        "Doc"\n'
            'class Foo(Base):\n'
            '    pass\n',
            '  File "", line 5\n'
            '    class Foo(Base):\n'
            '              ^\n'
            "CompileError: pure trait method 'foo' is not implemented\n")

    def test_pure_trait_method_not_implemented_docstring_and_pass(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Base:\n'
            '    def foo(self):\n'
            '        "Doc"\n'
            '        pass\n'
            'class Foo(Base):\n'
            '    pass\n',
            '  File "", line 6\n'
            '    class Foo(Base):\n'
            '              ^\n'
            "CompileError: pure trait method 'foo' is not implemented\n")

    def test_imported_pure_trait_method_not_implemented(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile([
                Source('@trait\n'
                       'class Base:\n'
                       '    def foo(self):\n'
                       '        pass\n',
                       module='foo.lib'),
                Source('from foo import Base\n'
                       'class Foo(Base):\n'
                       '    pass\n')
            ])

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '    class Foo(Base):\n'
            '              ^\n'
            "CompileError: pure trait method 'foo' is not implemented\n")

    def test_trait_member_access_1(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Base:\n'
            '    pass\n'
            'def foo(v: Base):\n'
            '    v.a = 1\n',
            '  File "", line 5\n'
            '        v.a = 1\n'
            '        ^\n'
            "CompileError: 'foo.lib.Base' has no member 'a'\n")

    def test_trait_member_access_2(self):
        self.assert_transpile_raises(
            'class Foo:\n'
            '    def foo(self, v: bool):\n'
            '        pass\n'
            'def foo(v: Foo):\n'
            '    v.foo()\n',
            '  File "", line 5\n'
            '        v.foo()\n'
            '        ^\n'
            "CompileError: parameter 'v: bool' not given\n")

    def test_wrong_trait_method_parameter_type(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Foo:\n'
            '    def foo(self, v: bool):\n'
            '        pass\n'
            'def foo(v: Foo):\n'
            '    v.foo(b"")\n',
            '  File "", line 6\n'
            '        v.foo(b"")\n'
            '              ^\n'
            "CompileError: expected a 'bool', got a 'bytes'\n")

    def test_trait_pascal_case(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class foo:\n'
            '    pass\n',
            '  File "", line 2\n'
            '    class foo:\n'
            '    ^\n'
            "CompileError: trait names must be pascal case\n")

    def test_trait_member(self):
        self.assert_transpile_raises(
            '@trait\n'
            'class Foo:\n'
            '    x: i32\n',
            '  File "", line 3\n'
            '        x: i32\n'
            '        ^\n'
            "CompileError: traits cannot have members\n")
