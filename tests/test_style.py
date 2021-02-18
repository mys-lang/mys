from .utils import TestCase
from .utils import transpile_source


class Test(TestCase):

    def test_tabs_not_allowed_as_indentation(self):
        with self.assertRaises(Exception) as cm:
            transpile_source('def foo():\n'
                             "\tpass\n")

        self.assert_exception_string(
            cm,
            '  File "<string>", line 2\n'
            "    pass\n"
            "    ^\n"
            'SyntaxError: indentation must be spaces, not tabs\n')
