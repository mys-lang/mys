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

    def define_variable_with_incomplete_type(self, name, node):
        self.variables_with_incomplete_type[name] = node
        self.stack[-1].append(name)

    def is_variable_defined(self, name):
        return name in self.variables

    def is_variable_with_incomplete_type_defined(self, name):
        return name in self.variables_with_incomplete_type


class InferTypesTransformer(ast.NodeTransformer):
    """Traverses the AST and replaces `ast.Assign` with `ast.AnnAssign`
    where types are defined.

    """

    def __init__(self, module_definitions, definitions):
        self.module_definitions = module_definitions
        self.definitions = definitions
        self.context = None
        self.returns = None

    def visit_AnnAssign(self, node):
        if self.context is None:
            return node

        if not isinstance(node.target, ast.Name):
            return node

        variable_name = node.target.id

        if is_upper_snake_case(variable_name):
            return node

        if self.context.is_variable_defined(variable_name):
            return node

        if self.context.is_variable_with_incomplete_type_defined(variable_name):
            return node

        self.context.define_variable(variable_name, None)

        return node

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

        if self.context.is_variable_with_incomplete_type_defined(variable_name):
            return node

        if isinstance(node.value, ast.List):
            if len(node.value.elts) == 0:
                node = ast.AnnAssign(target=ast.Name(id=variable_name),
                                     annotation=ast.Name(id=''),
                                     value=node.value)
        elif isinstance(node.value, ast.Dict):
            if len(node.value.keys) == 0:
                node = ast.AnnAssign(target=ast.Name(id=variable_name),
                                     annotation=ast.Name(id=''),
                                     value=node.value)

        self.context.define_variable_with_incomplete_type(variable_name, node)

        return node

    def visit_Return(self, node):
        if not isinstance(node.value, ast.Name):
            return node

        variable_node = self.context.variables_with_incomplete_type.get(node.value.id)

        if isinstance(variable_node, ast.AnnAssign):
            variable_node.annotation = self.returns

        return node

    def visit_FunctionDef(self, node):
        self.context = Context()

        for arg in node.args.args:
            if arg.arg != 'self':
                self.context.define_variable(arg.arg, None)

        self.returns = node.returns

        for i, item in enumerate(node.body):
            node.body[i] = self.visit(item)

        self.context = None

        return node
