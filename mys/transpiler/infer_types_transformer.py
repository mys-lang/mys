from ..parser import ast


class InferTypesTransformer(ast.NodeTransformer):
    """Traverses the AST and infers variable types.

    """

    def visit_Module(self, node):
        return node
