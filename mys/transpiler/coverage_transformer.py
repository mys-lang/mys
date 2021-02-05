from ..parser import ast
from .traits import is_trait_method_pure
from .utils import has_docstring


class CoverageTransformer(ast.NodeTransformer):
    """Traverses the AST and inserts coverage counters.

    """

    def __init__(self, source):
        self._variables = {}
        self._source_lines = source.splitlines()

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
        self.append_variable_lineno(body, node.lineno)

    def append_variable_lineno(self, body, lineno):
        if lineno not in self._variables:
            body.append(self.add_variable(lineno))

    def visit_body(self, node, body=None):
        if body is None:
            body = []

        for item in node:
            self.append_variable(body, item)
            body.append(self.visit(item))

        return body

    def visit_trait(self, node):
        body = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef) and is_trait_method_pure(item):
                body.append(item)
            else:
                body.append(self.visit(item))

        node.body = body

        return node

    def visit_ClassDef(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id == 'trait':
                    return self.visit_trait(node)

        node.body = [self.visit(item) for item in node.body]

        return node

    def visit_FunctionDef(self, node):
        # Ignore tests in coverage.
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id == 'test':
                    return node

        body = []
        self.append_variable(body, node)

        body_iter = iter(node.body)

        if has_docstring(node):
            next(body_iter)

        node.body = self.visit_body(body_iter, body)

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

        if node.orelse:
            last_body_lineno = node.body[-1].end_lineno
            first_orelse_lineno = node.orelse[0].lineno
            body = []

            for lineno in range(last_body_lineno, first_orelse_lineno - 1):
                if self._source_lines[lineno].strip() == 'else:':
                    self.append_variable_lineno(body, lineno + 1)

            node.orelse = self.visit_body(node.orelse, body)

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
