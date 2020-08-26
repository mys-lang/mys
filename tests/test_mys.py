import unittest
import mys
from .utils import read_file


class MysTest(unittest.TestCase):

    maxDiff = None

    def assert_equal_to_file(self, actual, expected):
        # open(expected, 'w').write(actual)
        self.assertEqual(actual, read_file(expected))

    def test_all(self):
        datas = [
            'basics',
            'hello_world',
            'loops',
            'calc'
        ]

        for data in datas:
            self.assert_equal_to_file(
                mys.transpile(read_file(f'tests/files/{data}.mys')),
                f'tests/files/{data}.mys.dev.cpp')
