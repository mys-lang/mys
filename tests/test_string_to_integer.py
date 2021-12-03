from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_string_to_integer(self):
        build_and_test_module('string_to_integer')
