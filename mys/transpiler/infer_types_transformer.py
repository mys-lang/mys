from ..parser import ast
from .definitions import TypeVisitor
from .utils import is_upper_snake_case


class InferTypesTransformer(ast.NodeTransformer):
    """Traverses the AST and replaces `ast.Assign` with `ast.AnnAssign`
    where types are defined.

    """

    def __init__(self, module_definitions, definitions):
        self.module_definitions = module_definitions
        self.definitions = definitions
        self.variables = None
        self.returns = None

    # ToDo: Remove once working.
    def visit_Module(self, node):
        return node

    def visit_Assign(self, node):
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
                print(self.returns)
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

        return_type = TypeVisitor().visit(node.returns)

        for item in node.body:
            visitor = ReturnVisitor(return_type)
            visitor.visit(item)
            print(visitor.returns)

        for item in node.body:
            self.visit(item)

        return node


class ReturnVisitor(ast.NodeVisitor):

    def __init__(self, return_type):
        self.return_type = return_type
        self.returns = {}

    def visit_Return(self, node):
        if isinstance(self.return_type, tuple):
            pass

        print(self.return_type)
        print(ast.dump(node))
