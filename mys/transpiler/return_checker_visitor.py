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
        return all(self.visit_body(case.body) for case in node.cases)

    def visit_Try(self, node):
        if self.visit_body(node.finalbody):
            return True

        if not self.visit_body(node.body):
            return False

        return all(self.visit_body(handler.body) for handler in node.handlers)

    def visit_While(self, node):
        return WhileVisitor().visit(node)

class WhileVisitor(ast.NodeVisitor):
    """Returns True if the while loop always returns, False otherwise.

    """

    def visit_body(self, node):
        for item in node:
            if self.visit(item):
                return True

        return False

    def visit_While(self, node):
        if not isinstance(node.test, ast.Constant):
            return False

        if node.test.value is not True:
            return False

        return self.visit_body(node.body)

    def visit_For(self, _node):
        return False

    def visit_Break(self, _node):
        return False

    def visit_Return(self, _node):
        return True

    def visit_If(self, node):
        if self.visit_body(node.body):
            return True

        if node.orelse is None:
            return False
        else:
            return self.visit_body(node.orelse)

    def visit_Match(self, node):
        return any(self.visit_body(case.body) for case in node.cases)

    def visit_Try(self, node):
        if self.visit_body(node.finalbody):
            return True

        if not self.visit_body(node.body):
            return False

        return any(self.visit_body(handler.body) for handler in node.handlers)
