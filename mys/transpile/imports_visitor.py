from ..parser import ast
from .utils import CompileError

class ImportsVisitor(ast.NodeVisitor):

    def __init__(self):
        self._other_found = False

    def visit_ImportFrom(self, node):
        if self._other_found:
            raise CompileError("imports must be at the beginning of the file", node)

    def visit_ClassDef(self, node):
        self._other_found = True

    def visit_AnnAssign(self, node):
        self._other_found = True

    def visit_FunctionDef(self, node):
        self._other_found = True
