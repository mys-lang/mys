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
            'SyntaxError: indentation must be spaces, not tabs\n')
