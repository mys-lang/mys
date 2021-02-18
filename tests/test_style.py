from .utils import TestCase
from .utils import remove_ansi
from .utils import transpile_source


class Test(TestCase):

    def test_tabs_not_allowed_as_indentation(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "\tpass\n")

        self.assertEqual(
            remove_ansi(str(cm.exception).replace('\t', '')),
            '  File "<string>", line 2\n'
            '    pass\n'
            '    ^\n'
            'SyntaxError: indentations must be spaces, not tabs\n')

    def test_indent_2_spaces(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "  pass\n")

        self.assertEqual(
            remove_ansi(str(cm.exception).replace('\t', '')),
            '  File "<string>", line 2\n'
            '    pass\n'
            '    ^\n'
            'SyntaxError: indentations must be 4 spaces\n')

    def test_indent_2_spaces_in_if(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "    if True:\n"
                             "      pass\n")

        self.assertEqual(
            remove_ansi(str(cm.exception).replace('\t', '')),
            '  File "<string>", line 3\n'
            '    pass\n'
            '    ^\n'
            'SyntaxError: indentations must be 4 spaces\n')
