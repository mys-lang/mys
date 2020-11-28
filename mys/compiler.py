from collections import defaultdict
from .parser import ast

class Function:

    def __init__(self, name, args, returns):
        self.name = name
        self.args = args
        self.returns = returns

class Member:

    def __init__(self, name, type_):
        self.name = name
        self.type = type_

class Class:

    def __init__(self, name, members, methods, functions):
        self.name = name
        self.members = members
        self.methods = methods
        self.functions = functions

class Declarations:
    """Declared variables, classes and functions for one module. This
    information is useful when verifying that other modules uses this
    module correctly.

    """

    def __init__(self):
        self.variables = {}
        self.classes = {}
        self.functions = defaultdict(list)

def is_method(node):
    return len(node.args) >= 1 and node.args[0].arg == 'self'

class TypeVisitor(ast.NodeVisitor):

    def visit_Name(self, node):
        return node.id

    def visit_List(self, node):
        return [self.visit(elem) for elem in node.elts]

    def visit_Tuple(self, node):
        return tuple([self.visit(elem) for elem in node.elts])

class FunctionVisitor(TypeVisitor):

    def visit_arg(self, node):
        if node.annotation is None:
            raise Exception('Missing parameter type.')

        return (node.arg, self.visit(node.annotation))

    def visit_arguments(self, node):
        return [self.visit(arg) for arg in node.args]

    def visit_FunctionDef(self, node):
            args = self.visit(node.args)

            if node.returns is None:
                returns = None
            else:
                returns = FunctionVisitor().visit(node.returns)

            return Function(node.name, args, returns)

class MethodVisitor(FunctionVisitor):

    def visit_arguments(self, node):
        if len(node.args) >= 1 and node.args[0].arg == 'self':
            return [self.visit(arg) for arg in node.args[1:]]
        else:
            return []

class DeclarationsVisitor(ast.NodeVisitor):

    def __init__(self):
        super().__init__()
        self._declarations = Declarations()

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

        return self._declarations

    def visit_AnnAssign(self, node):
        name = node.target.id
        self._declarations.variables[name] = None

    def visit_ClassDef(self, node):
        class_name = node.name
        methods = defaultdict(list)
        functions = defaultdict(list)
        members = {}

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                name = item.name

                if is_method(item.args):
                    methods[name].append(MethodVisitor().visit(item))
                else:
                    functions[name].append(FunctionVisitor().visit(item))
            elif isinstance(item, ast.AnnAssign):
                name = item.target.id
                members[name] = Member(name,
                                       TypeVisitor().visit(item.annotation))

        self._declarations.classes[class_name] = Class(class_name,
                                                       members,
                                                       methods,
                                                       functions)

    def visit_FunctionDef(self, node):
        self._declarations.functions[node.name].append(FunctionVisitor().visit(node))

def create_ast(source):
    return ast.parse(source)

def find_declarations(tree):
    """Find all declarations in given tree and return them.

    """

    return DeclarationsVisitor().visit(tree)
