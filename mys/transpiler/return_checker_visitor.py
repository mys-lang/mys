from ..parser import ast
from .utils import CompileError


class ReturnCheckerVisitor(ast.NodeVisitor):
    """Check that given function always returns or raises.

    """

    def visit_body(self, node):
        for item in node:
            if self.visit(item):
                return True

        return False

    def visit_FunctionDef(self, node):
        if self.visit_body(node.body):
            return

        raise CompileError('missing return or raise', node)

    def visit_Return(self, _node):
        return True

    def visit_Raise(self, _node):
        return True

    def visit_If(self, node):
        if not self.visit_body(node.body):
            return False

        if node.orelse is None:
            return True
        else:
            return self.visit_body(node.orelse)

    def visit_Match(self, node):
        return all([self.visit_body(case.body) for case in node.cases])

    def visit_Try(self, node):
        if self.visit_body(node.finalbody):
            return True

        if not self.visit_body(node.body):
            return False

        return all([self.visit_body(handler.body) for handler in node.handlers])
