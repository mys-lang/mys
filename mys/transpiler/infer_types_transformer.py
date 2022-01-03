from ..parser import ast
from .utils import is_upper_snake_case


class InferTypesTransformer(ast.NodeTransformer):
    """Traverses the AST and replaces `ast.Assign` with `ast.AnnAssign`
    where types are defined.

    """

    def __init__(self, module_definitions, definitions):
        self.module_definitions = module_definitions
        self.definitions = definitions
        self.variables = None

    def visit_Module(self, node):
        return node

    def visit_Assign(self, node):
        if self.variables is None:
            return node

        if len(node.targets) != 1:
            return node

        if not isinstance(node.targets[0], ast.Name):
            return node

        variable_name = node.targets[0].id

        if is_upper_snake_case(variable_name):
            return node

        if variable_name in self.variables:
            return node

        if isinstance(node.value, ast.List):
            if len(node.value.elts) == 0:
                print(self.variables)
                print(ast.dump(node))
                print('list')
        elif isinstance(node.value, ast.Dict):
            if len(node.value.keys) == 0:
                print(self.variables)
                print(ast.dump(node))
                print('dict')

        self.variables.add(variable_name)

        return node

    def visit_FunctionDef(self, node):
        self.variables = set()

        for arg in node.args.args:
            if arg.arg != 'self':
                self.variables.add(arg.arg)

        for item in node.body:
            self.visit(item)

        self.variables = None

        return node
