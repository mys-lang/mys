from ..parser import ast
from .utils import INTEGER_TYPES
from .utils import CompileError
from .utils import is_primitive_type
from .utils import is_private
from .utils import is_public


def member_title(delim, member_name, pre=''):
    return ast.Constant(value=f'{delim}{member_name}={pre}')


def formatted_value_member(member_name):
    return ast.FormattedValue(
        value=ast.Attribute(
            value=ast.Name(id='self'),
            attr=member_name),
        conversion=-1)


class ClassTransformer(ast.NodeTransformer):
    """Traverses the AST and adds missing __init__(), __del__() and
    __str__() methods to classes.

    """

    def default_member_value(self, annotation):
        """Default value of private member.

        """

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
                value = ('', '', '')

        return ast.Constant(value=value)

    def add_init(self, node, members):
        """Add __init__() to the class as it was missing.

        """

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
                value = self.default_member_value(member.annotation)

            body.append(
                ast.Assign(
                    targets=[
                        ast.Attribute(
                            value=ast.Name(id='self'),
                            attr=member_name)
                    ],
                    value=value))

        if not body:
            body.append(ast.Pass())

        node.body.append(ast.FunctionDef(name='__init__',
                                         args=args,
                                         body=body,
                                         decorator_list=[]))

    def add_del(self, node):
        """Add __del__() to the class as it was missing.

        """

        node.body.append(
            ast.FunctionDef(name='__del__',
                            args=ast.arguments(posonlyargs=[],
                                               args=[ast.arg(arg='self')],
                                               vararg=None,
                                               kwonlyargs=[],
                                               kw_defaults=[],
                                               kwarg=None,
                                               defaults=[]),
                            body=[],
                            decorator_list=[]))

    def add_str_string(self, body, values, delim, member_name):
        body += [
            ast.If(
                test=ast.Compare(
                    left=ast.Attribute(
                        value=ast.Name(id='self'),
                        attr=member_name),
                    ops=[ast.Is()],
                    comparators=[ast.Constant(value=None)]),
                body=[
                    ast.Assign(
                        targets=[ast.Name(id=member_name)],
                        value=ast.Constant(value='None'))
                ],
                orelse=[
                    ast.Assign(
                        targets=[ast.Name(id=member_name)],
                        value=ast.JoinedStr(
                            values=[
                                ast.Constant(value='"'),
                                ast.FormattedValue(
                                    value=ast.Attribute(
                                        value=ast.Name(id='self'),
                                        attr=member_name),
                                    conversion=-1),
                                ast.Constant(value='"')
                            ]))
                ])
        ]
        values += [
            member_title(delim, member_name),
            ast.FormattedValue(
                value=ast.Name(id=member_name),
                conversion=-1)
        ]

    def add_str_char(self, values, delim, member_name):
        values += [
            member_title(delim, member_name, "'"),
            formatted_value_member(member_name),
            ast.Constant(value="'")
        ]

    def add_str_other(self, values, delim, member_name):
        values += [
            member_title(delim, member_name),
            formatted_value_member(member_name)
        ]

    def add_str(self, node, members):
        """Add __str__() to the class as it was missing.

        """

        body = []
        values = [ast.Constant(value=f'{node.name}(')]
        delim = ''

        for member in members:
            member_name = member.target.id

            if isinstance(member.annotation, ast.Name):
                if member.annotation.id == 'string':
                    self.add_str_string(body, values, delim, member_name)
                elif member.annotation.id == 'char':
                    self.add_str_char(values, delim, member_name)
                else:
                    self.add_str_other(values, delim, member_name)
            else:
                self.add_str_other(values, delim, member_name)

            delim = ', '

        values.append(ast.Constant(value=')'))
        body.append(ast.Return(value=ast.JoinedStr(values=values)))
        node.body.append(
            ast.FunctionDef(name='__str__',
                            args=ast.arguments(posonlyargs=[],
                                               args=[ast.arg(arg='self')],
                                               vararg=None,
                                               kwonlyargs=[],
                                               kw_defaults=[],
                                               kwarg=None,
                                               defaults=[]),
                            body=body,
                            decorator_list=[],
                            returns=ast.Name(id='string')))

    def add_eq(self, node, members):
        """Add __eq__(self, other: Self) to the class as it was missing.

        """

        body = [
            ast.If(
                test=ast.Compare(
                    left=ast.Name(id='other'),
                    ops=[
                        ast.Is()],
                    comparators=[
                        ast.Constant(value=None)]),
                body=[
                    ast.Return(
                        value=ast.Constant(value=False))],
                orelse=[])
        ]

        for member in members:
            member_name = member.target.id

            # ToDo: Compare private members as well once the can be
            #       accessed.
            if is_private(member_name):
                continue

            # ToDo: Support more...
            if not isinstance(member.annotation, ast.Name):
                continue

            if not is_primitive_type(member.annotation.id):
                continue

            body.append(
                ast.If(
                    test=ast.UnaryOp(
                        op=ast.Not(),
                        operand=ast.Compare(
                            left=ast.Attribute(
                                value=ast.Name(id='self'),
                                attr=member_name),
                            ops=[ast.Eq()],
                            comparators=[
                                ast.Attribute(
                                    value=ast.Name(id='other'),
                                    attr=member_name)])),
                    body=[
                        ast.Return(
                            value=ast.Constant(value=False))],
                    orelse=[]))

        body.append(ast.Return(value=ast.Constant(value=True)))
        node.body.append(
            ast.FunctionDef(name='__eq__',
                            args=ast.arguments(
                                posonlyargs=[],
                                args=[
                                    ast.arg(arg='self'),
                                    ast.arg(arg='other',
                                            annotation=ast.Name(id=node.name))
                                ],
                                vararg=None,
                                kwonlyargs=[],
                                kw_defaults=[],
                                kwarg=None,
                                defaults=[]),
                            body=body,
                            decorator_list=[],
                            returns=ast.Name(id='bool')))

    def add_hash(self, node, members):
        """Add __hash__(self) -> i64 to the class as it was missing.

        """

        body = [
            ast.Assign(
                targets=[ast.Name(id='hash')],
                value=ast.Constant(value=0))
        ]

        for member in members:
            member_name = member.target.id

            # ToDo: Support more...
            if not isinstance(member.annotation, ast.Name):
                continue

            if not is_primitive_type(member.annotation.id):
                continue

            body.append(
                ast.AugAssign(
                    target=ast.Name(id='hash'),
                    op=ast.Add(),
                    value=ast.Call(
                        func=ast.Name(id='hash'),
                        args=[
                            ast.Attribute(
                                value=ast.Name(id='self'),
                                attr=member_name)
                        ])))

        body.append(ast.Return(value=ast.Name(id='hash')))
        node.body.append(
            ast.FunctionDef(name='__hash__',
                            args=ast.arguments(
                                posonlyargs=[],
                                args=[ast.arg(arg='self')],
                                vararg=None,
                                kwonlyargs=[],
                                kw_defaults=[],
                                kwarg=None,
                                defaults=[]),
                            body=body,
                            decorator_list=[],
                            returns=ast.Name(id='i64')))

    def visit_ClassDef(self, node):
        init_found = False
        del_found = False
        str_found = False
        eq_found = False
        hash_found = False
        members = []

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
                elif item.name == '__del__':
                    del_found = True
                elif item.name == '__str__':
                    str_found = True
                elif item.name == '__eq__':
                    eq_found = True
                elif item.name == '__hash__':
                    hash_found = True
            elif isinstance(item, ast.AnnAssign):
                if not isinstance(item.target, ast.Name):
                    raise CompileError('invalid syntax', item)

                members.append(item)

        if not init_found:
            self.add_init(node, members)

        if not del_found:
            self.add_del(node)

        if not str_found:
            self.add_str(node, members)

        if not eq_found:
            self.add_eq(node, members)

        if not hash_found:
            self.add_hash(node, members)

        return node
