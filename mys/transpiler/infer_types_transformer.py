from ..parser import ast
from .definitions import TypeVisitor
from .utils import is_upper_snake_case


class InferTypesTransformer(ast.NodeTransformer):
    """Traverses the AST and infers variable types.

    """

    def visit_Module(self, node):
        return node
