import os

from .utils import TestCase
from .utils import build_and_test_module


class Test(TestCase):

    def test_coverage(self):
        build_and_test_module('coverage', ['--coverage'])

        with open('tests/build/test_coverage/.mys-coverage.txt', 'r') as fin:
            mys_coverage = fin.read()

        self.assert_in(
            'File: ./src/coverage.mys\n'
            '1 0\n'
            '4 2\n'
            '8 1\n',
            mys_coverage)

        self.assertTrue(
            os.path.exists('tests/build/test_coverage/covhtml/index.html'))
