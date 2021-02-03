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
            '2 0\n'
            '4 2\n'
            '5 2\n'
            '7 2\n'
            '8 1\n'
            '9 1\n'
            '11 0\n'
            '15 1\n'
            '17 2\n'
            '18 0\n'
            '20 2\n'
            '21 4\n'
            '22 2\n'
            '23 2\n'
            '24 0\n'
            '26 2\n'
            '29 1\n'
            '30 1\n'
            '31 1\n',
            mys_coverage)

        self.assertTrue(
            os.path.exists('tests/build/test_coverage/covhtml/index.html'))
