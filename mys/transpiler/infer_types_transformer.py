from ..parser import ast
from .utils import BUILTIN_TYPES
from .utils import CompileError
from .utils import is_upper_snake_case


class Placeholder(ast.AST):
    pass


class TypeVisitor(ast.NodeVisitor):

    def __init__(self, context):
        self.context = context

    def visit_Constant(self, node):
        if isinstance(node.value, int):
            return ast.Name(id='i64')
        elif isinstance(node.value, str):
            return ast.Name(id='string')

        return None

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            function_name = node.func.id

            if function_name in BUILTIN_TYPES:
                return ast.Name(id=function_name)
            else:
                functions = self.context.module_definitions.functions.get(
                    function_name)

                if functions is not None:
                    returns = functions[0].node.returns

                    if returns is not None:
                        return returns

        return None


class Context:

    def __init__(self, module_definitions, definitions):
        self.module_definitions = module_definitions
        self.definitions = definitions
        self.variables = {}
        self.incomplete_variables = {}
        self.stack = [[]]

    def push(self):
        self.stack.append([])

    def pop(self):
        for name in self.stack.pop():
            self.variables.pop(name)

    def define_variable(self, name, mys_type):
        self.variables[name] = mys_type
        self.stack[-1].append(name)

    def define_incomplete_variable(self, name, node, ann_node):
        self.incomplete_variables[name] = (node, ann_node)
        self.stack[-1].append(name)


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

        if variable_name in self.context.variables:
            return node

        if variable_name in self.context.incomplete_variables:
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

        if variable_name in self.context.variables:
            return node

        if variable_name in self.context.incomplete_variables:
            return node

        ann_node = None

        if isinstance(node.value, ast.List):
            if len(node.value.elts) == 0:
                ann_node = ast.AnnAssign(target=ast.Name(id=variable_name),
                                         annotation=ast.List(elts=[Placeholder()]),
                                         value=node.value)
        elif isinstance(node.value, ast.Dict):
            if len(node.value.keys) == 0:
                # Dict or set.
                ann_node = ast.AnnAssign(target=ast.Name(id=variable_name),
                                         annotation=Placeholder(),
                                         value=node.value)
        elif isinstance(node.value, ast.Constant):
            if node.value.value is None:
                ann_node = ast.AnnAssign(target=ast.Name(id=variable_name),
                                         annotation=Placeholder(),
                                         value=node.value)

        if ann_node is not None:
            self.context.define_incomplete_variable(variable_name, node, ann_node)
            node = ann_node
        else:
            self.context.define_variable(variable_name, None)

        return node

    def visit_Return(self, node):
        if not isinstance(node.value, ast.Name):
            return node

        name = node.value.id

        if name in self.context.incomplete_variables:
            ann_node = self.context.incomplete_variables.pop(name)[1]
            ann_node.annotation = self.returns
            self.context.define_variable(name, None)

        return node

    def visit_For(self, node):
        ForLoopTargetVisitor(self.context).visit(node.target)

        for i, item in enumerate(node.body):
            node.body[i] = self.visit(item)

        return node

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                name = node.func.value.id

                if name in self.context.incomplete_variables:
                    ann_node = self.context.incomplete_variables[name][1]

                    if isinstance(ann_node.annotation, ast.List):
                        if node.func.attr == 'append':
                            if len(node.args) == 1:
                                type_node = self.get_type(node.args[0])

                                if type_node is not None:
                                    ann_node.annotation.elts[0] = type_node
                                    self.context.incomplete_variables.pop(name)
                                    self.context.define_variable(name, None)
                        elif node.func.attr == 'extend':
                            if len(node.args) == 1:
                                type_node = self.get_type(node.args[0])

                                if type_node is not None:
                                    ann_node.annotation = type_node
                                    self.context.incomplete_variables.pop(name)
                                    self.context.define_variable(name, None)

        return node

    def get_type(self, node):
        return TypeVisitor(self).visit(node)

    def visit_FunctionDef(self, node):
        self.context = Context(self.module_definitions, self.definitions)

        for arg in node.args.args:
            if arg.arg != 'self':
                self.context.define_variable(arg.arg, None)

        self.returns = node.returns

        for i, item in enumerate(node.body):
            node.body[i] = self.visit(item)

        for assign_node, _ in self.context.incomplete_variables.values():
            raise CompileError('cannot infer variable type', assign_node)

        self.context = None

        return node


class ForLoopTargetVisitor(ast.NodeVisitor):

    def __init__(self, context):
        self.context = context

    def visit_Name(self, node):
        self.context.define_variable(node.id, None)
