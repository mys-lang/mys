import ast
import unittest
from pprint import pprint

import mys



class NodeDumpVisitor(ast.NodeVisitor):

    def generic_visit(self, node):
        pprint(ast.dump(node))
        super().generic_visit(node)


class MysTest(unittest.TestCase):

    def test_todo(self):
        with open('tests/files/main.py') as fin:
            tree = ast.parse(fin.read())

        print()
        pprint(ast.dump(tree))
        # NodeDumpVisitor().visit(tree)
