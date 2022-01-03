from ..parser import ast
from .utils import is_upper_snake_case


class Context:

    def __init__(self):
        self.variables = {}
        self.variables_with_incomplete_type = {}
        self.stack = [[]]

    def push(self):
        self.stack.append([])

    def pop(self):
        for name in self.stack.pop():
            self.variables.pop(name)

    def define_variable(self, name, mys_type):
        self.variables[name] = mys_type
        self.stack[-1].append(name)

    def define_variable_with_incomplete_type(self, name, mys_type):
        self.variables_with_incomplete_type[name] = mys_type
        self.stack[-1].append(name)

    def is_variable_defined(self, name):
        return name in self.variables


class InferTypesTransformer(ast.NodeTransformer):
    """Traverses the AST and replaces `ast.Assign` with `ast.AnnAssign`
    where types are defined.

    """

    def __init__(self, module_definitions, definitions):
        self.module_definitions = module_definitions
        self.definitions = definitions
        self.context = None

    def visit_Assign(self, node):
        if self.context is None:
            return node

        if len(node.targets) != 1:
            return node

        if not isinstance(node.targets[0], ast.Name):
            return node

        variable_name = node.targets[0].id

        if is_upper_snake_case(variable_name):
            return node

        if self.context.is_variable_defined(variable_name):
            return node

        variable_type = None

        if isinstance(node.value, ast.List):
            if len(node.value.elts) == 0:
                variable_type = list()
        elif isinstance(node.value, ast.Dict):
            if len(node.value.keys) == 0:
                variable_type = dict()

        self.context.define_variable_with_incomplete_type(variable_name,
                                                          variable_type)

        return node

    def visit_FunctionDef(self, node):
        self.context = Context()

        for arg in node.args.args:
            if arg.arg != 'self':
                self.context.define_variable(arg.arg, None)

        for item in node.body:
            self.visit(item)

        self.context = None

        return node
