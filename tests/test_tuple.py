import os
from .utils import build_and_test_module
from .utils import TestCase


class Test(TestCase):

    def setUp(self):
        os.makedirs('tests/build', exist_ok=True)

    def test_tuple(self):
        build_and_test_module('tuple')
