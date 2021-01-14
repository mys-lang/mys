import shutil
from unittest.mock import patch

import mys.cli
from mys.transpiler import Source
from mys.transpiler import TranspilerError
from mys.transpiler import transpile

from .utils import Path
from .utils import TestCase
from .utils import remove_build_directory
from .utils import transpile_source


class Test(TestCase):

    def test_imports(self):
        name = 'test_imports'
        remove_build_directory(name)
        shutil.copytree('tests/files/imports', f'tests/build/{name}')

        with Path(f'tests/build/{name}/mypkg'):
            with patch('sys.argv', ['mys', '-d', 'test', '-v']):
                mys.cli.main()

    def test_circular_imports(self):
        name = 'test_circular_imports'
        remove_build_directory(name)
        shutil.copytree('tests/files/circular_imports', f'tests/build/{name}')

        with Path(f'tests/build/{name}'):
            with patch('sys.argv', ['mys', '-d', 'test', '-v']):
                mys.cli.main()

    def test_import_in_function_should_fail(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def main():\n'
                             '    import foo\n',
                             mys_path='<unknown>',
                             has_main=True)

        self.assert_exception_string(
            cm,
            '  File "<unknown>", line 2\n'
            '        import foo\n'
            '        ^\n'
            'CompileError: imports are only allowed on module level\n')

    def test_import_from_in_function_should_fail(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('def main():\n'
                             '    from foo import bar\n',
                             has_main=True)

        self.assert_exception_string(
            cm,
            '  File "", line 2\n'
            '        from foo import bar\n'
            '        ^\n'
            'CompileError: imports are only allowed on module level\n')

    def test_import(self):
        self.assert_transpile_raises(
            'import foo\n',
            '  File "", line 1\n'
            '    import foo\n'
            '    ^\n'
            "CompileError: only 'from <module> import ...' is allowed\n")

    def test_multiple_imports_failure(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('from foo import bar, fie\n',
                             mys_path='<unknown>')

        self.assert_exception_string(
            cm,
            '  File "<unknown>", line 1\n'
            '    from foo import bar, fie\n'
            '    ^\n'
            'CompileError: only one import is allowed, found 2\n')

    def test_relative_import_outside_package(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile_source('from .. import fie\n',
                             mys_path='src/mod.mys',
                             module_hpp='pkg/mod.mys.hpp')

        self.assert_exception_string(
            cm,
            '  File "src/mod.mys", line 1\n'
            '    from .. import fie\n'
            '    ^\n'
            'CompileError: relative import is outside package\n')

    def test_imported_variable_usage(self):
        transpile([
            Source('from foo import BAR\n'
                   '\n'
                   'def fie() -> i32:\n'
                   '    return 2 * BAR\n'),
            Source('BAR: i32 = 1', module='foo.lib')
        ])

    def test_imported_module_does_not_exist(self):
        self.assert_transpile_raises(
            'from kalle import bar\n'
            '\n'
            'def fie() -> i32:\n'
            '    return 2 * bar\n',
            '  File "", line 1\n'
            '    from kalle import bar\n'
            '    ^\n'
            "CompileError: imported module 'kalle.lib' does not exist\n")

    def test_imported_module_does_not_contain(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile([
                Source('from foo import bar\n'
                       '\n'
                       'def fie() -> i32:\n'
                       '    return 2 * bar\n'),
                Source('BOO: i32 = 1', module='foo.lib')
            ])

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    from foo import bar\n'
            '    ^\n'
            "CompileError: imported module 'foo.lib' does not contain 'bar'\n")

    def test_import_private_function_fails(self):
        with self.assertRaises(TranspilerError) as cm:
            transpile([
                Source('from foo import _BAR\n'
                       '\n'
                       'def fie() -> i32:\n'
                       '    return 2 * _BAR\n'),
                Source('_BAR: i32 = 1', module='foo.lib')
            ])

        self.assert_exception_string(
            cm,
            '  File "", line 1\n'
            '    from foo import _BAR\n'
            '    ^\n'
            "CompileError: cannot import private definition '_BAR'\n")

    def test_import_function_ok(self):
        transpile([
            Source('from foo import bar\n'
                   'def fie():\n'
                   '    bar()\n'),
            Source('def bar():\n'
                   '    pass\n',
                   module='foo.lib')
        ])

    def test_import_after_function_definition(self):
        self.assert_transpile_raises(
            'def foo():\n'
            '    pass\n'
            'from bar import fie\n',
            '  File "", line 3\n'
            '    from bar import fie\n'
            '    ^\n'
            "CompileError: imports must be at the beginning of the file\n")

    def test_import_after_variable_definition(self):
        self.assert_transpile_raises(
            'V: bool = True\n'
            'from bar import fie\n',
            '  File "", line 2\n'
            '    from bar import fie\n'
            '    ^\n'
            "CompileError: imports must be at the beginning of the file\n")

    def test_import_after_import(self):
        self.assert_transpile_raises(
            'import bar\n'
            'from bar import fie\n',
            '  File "", line 1\n'
            '    import bar\n'
            '    ^\n'
            "CompileError: only 'from <module> import ...' is allowed\n")
