from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_fstrings(self):
        with self.assertRaises(SystemExit):
            build_and_test_module('infer_types')
