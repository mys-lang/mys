from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_bytes(self):
        build_and_test_module('bytes')
