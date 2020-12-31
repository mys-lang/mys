from ..parser import ast
from .utils import CompileError

class ImportsVisitor(ast.NodeVisitor):

    def __init__(self):
        self._other_found = False

    def visit_Module(self, node):
        body = [
            self.visit(item)
            for item in node.body
        ]

    def visit_ImportFrom(self, node):
        if self._other_found:
            raise CompileError("imports must be at the beginning of the file", node)

    def generic_visit(self, node):
        self._other_found = True
