import ast
import unittest
from pprint import pprint

import mys



class NodeDumpVisitor(ast.NodeVisitor):

    def generic_visit(self, node):
        pprint(ast.dump(node))
        super().generic_visit(node)


class MysTest(unittest.TestCase):

    def test_all(self):
        datas = [
            'basics',
            'hello_world'
        ]

        for data in datas:
            with open(f'tests/files/{data}.py') as fin:
                tree = ast.parse(fin.read())

            print()
            print(ast.dump(tree))
            # NodeDumpVisitor().visit(tree)
