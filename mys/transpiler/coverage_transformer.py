from ..parser import ast


class CoverageTransformer(ast.NodeTransformer):
    """Traverses the AST and inserts coverage counters.

    """

    def __init__(self):
        self._variables = {}

    def variables(self):
        return sorted(self._variables.items())

    def visit_Module(self, node):
        body = [self.visit(item) for item in node.body]
        variables = []

        for _, variable in self.variables():
            variables.append(
                ast.AnnAssign(
                    target=ast.Name(id=variable, ctx=ast.Store()),
                    annotation=ast.Name(id='i64', ctx=ast.Load()),
                    value=ast.Constant(value=0, kind=None),
                    simple=1))

        node.body = variables + body

        return node

    def add_variable(self, lineno):
        variable = f'__MYS_COVERAGE_{lineno}'
        self._variables[lineno] = variable

        return ast.AugAssign(
            target=ast.Name(id=variable, ctx=ast.Store()),
            op=ast.Add(),
            value=ast.Constant(value=1, kind=None))

    def append_variable(self, body, node):
        if node.lineno not in self._variables:
            body.append(self.add_variable(node.lineno))

    def visit_body(self, node, body=None):
        if body is None:
            body = []

        for item in node:
            self.append_variable(body, item)
            body.append(self.visit(item))

        return body

    def visit_FunctionDef(self, node):
        body = []
        self.append_variable(body, node)
        node.body = self.visit_body(node.body, body)

        return node

    def visit_For(self, node):
        body = []
        self.append_variable(body, node)
        node.body = self.visit_body(node.body, body)

        return node

    def visit_While(self, node):
        body = []
        self.append_variable(body, node)
        node.body = self.visit_body(node.body, body)

        return node

    def visit_If(self, node):
        node.body = self.visit_body(node.body)
        node.orelse = self.visit_body(node.orelse)

        return node

    def visit_Match(self, node):
        for case in node.cases:
            body = [self.add_variable(case.pattern.lineno)]
            case.body = self.visit_body(case.body, body)

        return node

    def visit_Try(self, node):
        node.body = self.visit_body(node.body)

        for handler in node.handlers:
            handler.body = self.visit_body(handler.body)

        node.orelse = self.visit_body(node.orelse)
        node.finalbody = self.visit_body(node.finalbody)

        return node
