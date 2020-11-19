import ast

class Public:

    def __init__(self):
        self.variables = {}
        self.classes = {}
        self.functions = {}

class PublicVisitor(ast.NodeVisitor):

    def __init__(self):
        super().__init__()
        self._public = Public()

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

        return self._public

    def visit_AnnAssign(self, node):
        name = node.target.id
        
        if not name.startswith('_'):
            self._public.variables[name] = None

    def visit_ClassDef(self, node):
        name = node.name
        
        if not name.startswith('_'):
            self._public.classes[name] = None

    def visit_FunctionDef(self, node):
        name = node.name

        if not name.startswith('_'):
            self._public.functions[name] = None

def create_ast(source):
    return ast.parse(source)

def find_public(tree):
    """Find all public definitions in given tree and return them.

    """

    return PublicVisitor().visit(tree)
