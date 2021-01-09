from .utils import build_and_test_module
from .utils import TestCase


class Test(TestCase):

    def test_bytes(self):
        build_and_test_module('bytes')
