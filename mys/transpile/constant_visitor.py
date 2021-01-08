from ..parser import ast


class ConstantVisitor(ast.NodeVisitor):

    def __init__(self):
        self.is_constant = True

    def visit_Constant(self, node):
        pass

    def visit_UnaryOp(self, node):
        self.visit(node.operand)

    def visit_List(self, node):
        for item in node.elts:
            self.visit(item)

    def visit_Tuple(self, node):
        for item in node.elts:
            self.visit(item)

    def visit_Dict(self, node):
        for item in node.keys:
            self.visit(item)

        for item in node.values:
            self.visit(item)

    def generic_visit(self, node):
        self.is_constant = False


def is_constant(node):
    """Returns true if given node is a "constant", that is, is does not
    contain variables, enums, traits or classes.

    """

    visitor = ConstantVisitor()
    visitor.visit(node)

    return visitor.is_constant
