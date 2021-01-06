from ..parser import ast
from .utils import is_public
from .utils import INTEGER_TYPES


class ClassTransformer(ast.NodeTransformer):

    def __init__(self, char_lineno):
        self.char_lineno = char_lineno

    def default_value(self, annotation):
        value = None

        if isinstance(annotation, ast.Name):
            type_name = annotation.id

            if type_name in INTEGER_TYPES:
                value = 0
            elif type_name in ['f32', 'f64']:
                value = 0.0
            elif type_name == 'bool':
                value = False
            elif type_name == 'char':
                value = ''

        return ast.Constant(value=value, lineno=self.char_lineno, col_offset=0)

    def visit_ClassDef(self, node):
        init_found = False
        members = []

        # print(ast.dump(node, indent=4))

        # Traits and enums are not yet keywords and should not have
        # __init__ added.
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in ['trait', 'enum']:
                    return node
            elif isinstance(decorator, ast.Call):
                if decorator.func.id == 'enum':
                    return node

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == '__init__':
                    init_found = True
            elif isinstance(item, ast.AnnAssign):
                members.append(item)

        if not init_found:
            args = ast.arguments(posonlyargs=[],
                                 args=[ast.arg(arg='self')],
                                 vararg=None,
                                 kwonlyargs=[],
                                 kw_defaults=[],
                                 kwarg=None,
                                 defaults=[])
            body = []

            for member in members:
                member_name = member.target.id

                if is_public(member_name):
                    args.args.append(ast.arg(arg=member_name,
                                             annotation=member.annotation))
                    value = ast.Name(id=member_name)
                else:
                    value = self.default_value(member.annotation)

                body.append(
                    ast.Assign(
                        targets=[
                            ast.Attribute(
                                value=ast.Name(id='self', ctx=ast.Load()),
                                attr=member_name,
                                ctx=ast.Store())],
                        value=value))

            if not body:
                body.append(ast.Pass())

            node.body.append(ast.FunctionDef(name='__init__',
                                             args=args,
                                             body=body,
                                             decorator_list=[]))
            # print(ast.dump(node, indent=4))

        return node
