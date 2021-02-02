import os

from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_coverage(self):
        build_and_test_module('coverage', ['--coverage'])

        self.assertTrue(
            os.path.exists('tests/build/test_coverage/covhtml/index.html'))
