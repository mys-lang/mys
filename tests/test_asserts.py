from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_asserts(self):
        build_and_test_module('asserts')
