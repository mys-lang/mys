from ..parser import ast
from .utils import CompileError


class ImportsVisitor(ast.NodeVisitor):
    """Raises an error if not all imports are at the beginning of the
    file.

    """

    def __init__(self):
        self._other_found = False

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

    def visit_Import(self, node):
        raise CompileError("only 'from <module> import ...' is allowed", node)

    def visit_ImportFrom(self, node):
        if self._other_found:
            raise CompileError("imports must be at the beginning of the file", node)

    def generic_visit(self, node):
        self._other_found = True
