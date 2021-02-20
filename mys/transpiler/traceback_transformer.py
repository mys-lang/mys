from ..parser import ast
from .traits import is_trait_method_pure
from .utils import has_docstring


def create_call_node(name, args):
    return ast.Expr(
        value=ast.Call(
            func=ast.Name(id=name, ctx=ast.Load()),
            args=args,
            keywords=[]))


class TracebackTransformer(ast.NodeTransformer):
    """Traverses the AST and inserts traceback information.

    """

    def __init__(self, source):
        self.entries = []
        self.index = -1
        self.source_lines = source.splitlines()
        self.function = None

    def next_index(self):
        self.index += 1

        return self.index

    def visit_body(self, node, body=None):
        if body is None:
            body = []

        for item in node:
            code = self.source_lines[item.lineno - 1].strip()
            code = code.replace('\\', '').replace('"', '\\"')
            self.entries.append((self.function, item.lineno, code))
            body.append(create_call_node('__MYS_TRACEBACK_SET',
                                         [ast.Constant(value=self.next_index())]))
            body.append(self.visit(item))

        return body

    def visit_FunctionDef(self, node):
        if is_trait_method_pure(node):
            return node

        self.function = node.name

        body = []
        body_iter = iter(node.body)

        if has_docstring(node):
            body.append(next(body_iter))

        body.append(create_call_node('__MYS_TRACEBACK_INIT', []))
        node.body = self.visit_body(body_iter, body)

        return node

    def visit_For(self, node):
        node.body = self.visit_body(node.body)

        return node

    def visit_While(self, node):
        node.body = self.visit_body(node.body)

        return node

    def visit_If(self, node):
        node.body = self.visit_body(node.body)

        if node.orelse:
            node.orelse = self.visit_body(node.orelse)

        return node

    def visit_Match(self, node):
        for case in node.cases:
            case.body = self.visit_body(case.body)

        return node

    def visit_Try(self, node):
        node.body = self.visit_body(node.body)

        for handler in node.handlers:
            handler.body = self.visit_body(handler.body)

        node.orelse = self.visit_body(node.orelse)
        node.finalbody = self.visit_body(node.finalbody)

        return node
