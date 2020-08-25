import ast
import unittest
from pprint import pprint

import mys

from .utils import read_file


class NodeDumpVisitor(ast.NodeVisitor):

    def generic_visit(self, node):
        pprint(ast.dump(node))
        super().generic_visit(node)


class MysTest(unittest.TestCase):

    maxDiff = None

    def assert_equal_to_file(self, actual, expected):
        # open(expected, 'w').write(actual)
        self.assertEqual(actual, read_file(expected))

    def test_all(self):
        datas = [
            'basics',
            'hello_world',
            # 'loops'
        ]

        for data in datas:
            self.assert_equal_to_file(
                mys.transpile(read_file(f'tests/files/{data}.mys')),
                f'tests/files/{data}.mys.dev.cpp')
