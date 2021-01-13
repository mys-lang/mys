from .utils import TestCase
from .utils import build_and_test_module
from .utils import transpile_source


class Test(TestCase):

    def test_regexp(self):
        build_and_test_module('regexp')

    def test_concatenate_with_different_flags(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(re"a"m re"b")\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            '    print(re"a"m re"b")\n'
            "                      ^\n"
            'SyntaxError: cannot mix regexp flags\n')

    def test_mix_bytes_with_regexp_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(re"a"m b"b")\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            '    print(re"a"m b"b")\n'
            "                     ^\n"
            'SyntaxError: cannot mix bytes and nonbytes literals\n')

    def test_mix_bytes_with_regexp_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(b"a" re"b")\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            '    print(b"a" re"b")\n'
            "                    ^\n"
            'SyntaxError: cannot mix bytes and nonbytes literals\n')

    def test_mix_string_with_regexp_1(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(re"a"m "b")\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            '    print(re"a"m "b")\n'
            "                    ^\n"
            'SyntaxError: cannot mix regexp and bytes or unicode literals\n')

    def test_mix_string_with_regexp_2(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print("a" re"b")\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            '    print("a" re"b")\n'
            "                   ^\n"
            'SyntaxError: cannot mix regexp and bytes or unicode literals\n')

    def test_swapped_re_for_er(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             '    print(er"b")\n')

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            '    print(er"b")\n'
            "            ^\n"
            'SyntaxError: invalid syntax\n')

    # ToDo: Remove, only for parser development before regexp is fully
    #       supported by the transpiler.
    def test_to_be_removed(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    print(re"\\d+")\n',
            '  File "", line 2\n'
            '        print(re"\\d+")\n'
            "              ^\n"
            'CompileError: regular expressions are not yet supported - '
            'pattern: "\\d+", flags: ""\n')

    # ToDo: Remove, only for parser development before regexp is fully
    #       supported by the transpiler.
    def test_to_be_removed_with_flags(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    print(re"\\d+"im)\n',
            '  File "", line 2\n'
            '        print(re"\\d+"im)\n'
            "              ^\n"
            'CompileError: regular expressions are not yet supported - '
            'pattern: "\\d+", flags: "im"\n')

    # ToDo: Remove, only for parser development before regexp is fully
    #       supported by the transpiler.
    def test_to_be_removed_concatenate(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    print(re"\\d+" re"apa")\n',
            '  File "", line 2\n'
            '        print(re"\\d+" re"apa")\n'
            "              ^\n"
            'CompileError: regular expressions are not yet supported - '
            'pattern: "\\d+apa", flags: ""\n')

    # ToDo: Remove, only for parser development before regexp is fully
    #       supported by the transpiler.
    def test_to_be_removed_concatenate_with_flags(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    print(re"\\d+"m re"apa"m)\n',
            '  File "", line 2\n'
            '        print(re"\\d+"m re"apa"m)\n'
            "              ^\n"
            'CompileError: regular expressions are not yet supported - '
            'pattern: "\\d+apa", flags: "m"\n')
