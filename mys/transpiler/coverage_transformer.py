from ..parser import ast


class CoverageTransformer(ast.NodeTransformer):
    """Traverses the AST and inserts coverage counters.

    """

    def __init__(self):
        self._variables = {}

    def variables(self):
        return sorted(self._variables.items())

    def visit_Module(self, node):
        body = []

        for item in node.body:
            body.append(self.visit(item))

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

    def visit_FunctionDef(self, node):
        if node.lineno in self._variables:
            return

        variable = f'__MYS_COVERAGE_{node.lineno}'
        self._variables[node.lineno] = variable
        node.body.insert(
            0,
            ast.AugAssign(
                target=ast.Name(id=variable, ctx=ast.Store()),
                op=ast.Add(),
                value=ast.Constant(value=1, kind=None)))

        return node
