from collections import defaultdict

from ..parser import ast
from .context import Context
from .definition_types import Class
from .definition_types import Definitions
from .definition_types import Enum
from .definition_types import Function
from .definition_types import Implement
from .definition_types import Member
from .definition_types import Param
from .definition_types import Test
from .definition_types import Trait
from .definition_types import Variable
from .utils import METHOD_BIN_OPERATORS
from .utils import CompileError
from .utils import Dict
from .utils import GenericType
from .utils import Optional
from .utils import Set
from .utils import Tuple
from .utils import Weak
from .utils import get_import_from_info
from .utils import has_docstring
from .utils import is_char
from .utils import is_integer_type
from .utils import is_pascal_case
from .utils import is_snake_case
from .utils import is_upper_snake_case
from .value_type_visitor import ValueTypeVisitor
from .value_type_visitor import reduce_type


def make_annotation_from_mys_type(mys_type, node):
    if isinstance(mys_type, str):
        return ast.Name(id=mys_type)
    elif isinstance(mys_type, Tuple):
        return ast.Tuple(elts=[
            make_annotation_from_mys_type(item, node) for item in mys_type.value_types
        ])
    elif isinstance(mys_type, list):
        return ast.List(elts=[
            make_annotation_from_mys_type(mys_type[0], node)
        ])
    elif isinstance(mys_type, Dict):
        return ast.Dict(
            keys=[
                make_annotation_from_mys_type(mys_type.key_type, node)
            ],
            values=[
                make_annotation_from_mys_type(mys_type.value_type, node)
            ])
    elif isinstance(mys_type, Set):
        return ast.Set(elts=[
            make_annotation_from_mys_type(mys_type.value_type, node)
        ])
    else:
        raise CompileError("cannot infer global variable type", node)


def is_test(node):
    for decorator in node.decorator_list:
        if isinstance(decorator, ast.Name):
            if decorator.id == 'test':
                return True

    return False


def get_docstring(node, body_iter=None):
    if has_docstring(node):
        docstring = node.body[0].value.value

        if body_iter is not None:
            next(body_iter)
    else:
        docstring = None

    return docstring


def check_global_name(name, node):
    if not is_upper_snake_case(name):
        raise CompileError(
            "global variable names must be upper case snake case", node)


class TypeVisitor(ast.NodeVisitor):

    def visit_Name(self, node):
        return node.id

    def visit_List(self, node):
        nitems = len(node.elts)

        if nitems != 1:
            raise CompileError(f"expected 1 type in list, got {nitems}", node)

        value_type = self.visit(node.elts[0])

        if isinstance(value_type, Optional):
            raise CompileError("list type cannot be optional", node.elts[0])

        return [value_type]

    def visit_Tuple(self, node):
        return Tuple([self.visit(elem) for elem in node.elts])

    def visit_Dict(self, node):
        key_type = self.visit(node.keys[0])

        if isinstance(key_type, Optional):
            raise CompileError("dict key type cannot be optional", node.keys[0])

        value_type = self.visit(node.values[0])

        if isinstance(value_type, Optional):
            raise CompileError("dict value type cannot be optional", node.values[0])

        return Dict(key_type, value_type)

    def visit_Set(self, node):
        nitems = len(node.elts)

        if nitems != 1:
            raise CompileError(f"expected 1 type in set, got {nitems}", node)

        value_type = self.visit(node.elts[0])

        if isinstance(value_type, Optional):
            raise CompileError("set type cannot be optional", node.elts[0])

        return Set(value_type)

    def visit_Subscript(self, node):
        value = self.visit(node.value)

        if value == 'optional':
            return Optional(self.visit(node.slice), node)
        elif value == 'weak':
            return Weak(self.visit(node.slice), node)
        else:
            types = self.visit(node.slice)

            if (isinstance(node.slice, ast.Name)
                or isinstance(types, (Optional, Weak))):
                types = [types]
            else:
                types = list(types)

            return GenericType(value, types, node)


class FormatDefaultVisitor(ast.NodeVisitor):

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return f'"{node.value}"'
        elif is_char(node.value):
            return f"'{node.value[0]}'"
        else:
            return str(node.value)

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)

        if isinstance(node.op, ast.USub):
            return f'-{operand}'
        else:
            return operand

    def visit_List(self, node):
        return '[' + ', '.join([self.visit(elem) for elem in node.elts]) + ']'

    def visit_Tuple(self, node):
        return '(' + ', '.join([self.visit(elem) for elem in node.elts]) + ')'

    def visit_Dict(self, node):
        return '{' + ', '.join([
            f'{self.visit(key)}: {self.visit(value)}'
            for key, value in zip(node.keys, node.values)
        ]) + '}'

    def visit_Set(self, node):
        return '{' + ', '.join([self.visit(elem) for elem in node.elts]) + '}'

    def visit_Call(self, node):
        params = ', '.join([self.visit(arg) for arg in node.args])

        return f'{node.func.id}({params})'

    def visit_Name(self, node):
        return node.id

    def visit_Attribute(self, node):
        return f'{self.visit(node.value)}.{node.attr}'


def check_method(node):
    if len(node.args.args) == 0 or node.args.args[0].arg != 'self':
        raise CompileError("'self' must be the first method parameter", node)


class FunctionVisitor(TypeVisitor):

    ALLOWED_DECORATORS = ['generic', 'raises', 'macro', 'iterator']

    def visit_arg(self, node):
        if node.annotation is None:
            raise CompileError("parameters must have a type", node)

        if not is_snake_case(node.arg):
            raise CompileError("parameter names must be snake case", node)

        return Param(node.arg, self.visit(node.annotation), node)

    def visit_arguments(self, node):
        args = []

        for i, arg in enumerate(node.args[::-1]):
            if i < len(node.defaults):
                args.append((self.visit(arg),
                             node.defaults[len(node.defaults) - i - 1]))
            else:
                args.append((self.visit(arg), None))

        return args[::-1]

    def visit_FunctionDef(self, node):
        decorators = visit_decorator_list(node.decorator_list,
                                          self.ALLOWED_DECORATORS)
        is_macro = 'macro' in decorators
        is_iterator = 'iterator' in decorators

        if is_macro:
            if not is_upper_snake_case(node.name):
                raise CompileError("macro names must be upper case snake case", node)
        else:
            if not is_snake_case(node.name):
                raise CompileError("function names must be snake case", node)

        args = self.visit(node.args)

        if node.returns is None:
            returns = None
        else:
            returns = FunctionVisitor().visit(node.returns)

        return Function(node.name,
                        decorators.get('generic', []),
                        decorators.get('raises', []),
                        is_macro,
                        is_iterator,
                        args,
                        returns,
                        node,
                        None,
                        None,
                        get_docstring(node))


class TestVisitor(TypeVisitor):

    def visit_FunctionDef(self, node):
        if len(node.decorator_list) != 1:
            raise CompileError('tests cannot have decorators', node)

        if len(node.args.args) != 0:
            raise CompileError('tests cannot have parameters', node)

        if node.returns is not None:
            raise CompileError('tests cannot return any value', node)

        if not is_snake_case(node.name):
            raise CompileError("test names must be snake case", node)

        return Test(node.name, node, get_docstring(node))


class MethodVisitor(FunctionVisitor):

    def visit_arguments(self, node):
        args = []

        for i, arg in enumerate(node.args[1:][::-1]):
            if i < len(node.defaults):
                args.append((self.visit(arg),
                             node.defaults[len(node.defaults) - i - 1]))
            else:
                args.append((self.visit(arg), None))

        return args[::-1]


def visit_decorator_list(decorator_list, allowed_decorators):
    decorators = {}

    for decorator in decorator_list:
        if isinstance(decorator, ast.Call):
            name = decorator.func.id
            values = []

            for arg in decorator.args:
                if not isinstance(arg, ast.Name):
                    raise CompileError("invalid decorator value", arg)

                if arg.id in values:
                    raise CompileError(f"'{arg.id}' can only be given once", arg)

                values.append(arg.id)
        elif isinstance(decorator, ast.Name):
            name = decorator.id
            values = []
        else:
            raise CompileError("decorators must be @name or @name()", decorator)

        if name not in allowed_decorators:
            raise CompileError(f"invalid decorator '{name}'", decorator)

        if name in decorators:
            raise CompileError(f"@{name} can only be given once", decorator)

        if name == 'enum':
            if values:
                raise CompileError("no parameters expected", decorator)

            decorators['enum'] = None
        elif name == 'trait':
            if values:
                raise CompileError("no parameters expected", decorator)

            decorators['trait'] = None
        elif name == 'test':
            decorators['test'] = None
        elif name == 'generic':
            if not values:
                raise CompileError("at least one parameter required", decorator)

            decorators['generic'] = values
        elif name == 'raises':
            if not values:
                raise CompileError("@raises requires at least one error", decorator)

            decorators['raises'] = values
        elif name == 'macro':
            decorators['macro'] = None
        elif name == 'iterator':
            decorators['iterator'] = None

    return decorators


def validate_method_signature(method, method_node):
    if method.name in METHOD_BIN_OPERATORS:
        if len(method.args) != 1:
            raise CompileError(
                f'{method.name} must take exactly one parameter', method_node)

        if method.returns is None:
            raise CompileError(f'{method.name} must return a value', method_node)


class DefinitionsVisitor(ast.NodeVisitor):

    def __init__(self, source_lines, module_levels, module_name):
        super().__init__()
        self._source_lines = source_lines
        self._module_levels = module_levels
        self._definitions = Definitions(module_name)
        self._next_enum_value = None
        self._variables_without_annotation = []

    def visit_Module(self, node):
        body_length = len(node.body)
        item_index = 0

        while item_index < body_length:
            item = node.body[item_index]

            if isinstance(item, ast.AnnAssign):
                item_index += self.visit_global_variable(item,
                                                         node.body,
                                                         body_length,
                                                         item_index)
            if isinstance(item, ast.Assign):
                item_index += self.visit_global_variable_without_annotation(
                    item,
                    node.body,
                    body_length,
                    item_index)
            else:
                self.visit(item)

            item_index += 1

        self.infer_variable_types()

        return self._definitions

    def infer_variable_types(self):
        context = Context(self._module_levels,
                          [],
                          [],
                          self._source_lines)
        value_type_visitor = ValueTypeVisitor(context)

        for variable in self._variables_without_annotation:
            try:
                mys_type = value_type_visitor.visit(variable.node.value)
                variable.type = reduce_type(mys_type)
            except Exception:
                mys_type = None

            variable.node.annotation = make_annotation_from_mys_type(variable.type,
                                                                     variable.node)
            self._definitions.define_variable(variable.name, variable, variable.node)

    def visit_ImportFrom(self, node):
        self._definitions.add_import(*get_import_from_info(node, self._module_levels),
                                     node)

    def visit_Assign(self, node):
        raise CompileError("global variable types cannot be inferred", node)

    def get_docstring(self, body, body_length, item_index):
        docstring = None
        docstring_index = item_index + 1

        if body_length > docstring_index:
            docstring_node = body[docstring_index]

            if isinstance(docstring_node, ast.Expr):
                if isinstance(docstring_node.value, ast.Constant):
                    if isinstance(docstring_node.value.value, str):
                        docstring = docstring_node.value.value

        return docstring

    def visit_global_variable(self, node, body, body_length, item_index):
        name = node.target.id
        check_global_name(name, node)
        docstring = self.get_docstring(body, body_length, item_index)
        self._definitions.define_variable(
            name,
            Variable(name,
                     TypeVisitor().visit(node.annotation),
                     node,
                     docstring),
            node)

        if docstring is None:
            return 0
        else:
            return 1

    def visit_global_variable_without_annotation(self,
                                                 node,
                                                 body,
                                                 body_length,
                                                 item_index):
        name = node.targets[0].id
        check_global_name(name, node)
        docstring = self.get_docstring(body, body_length, item_index)
        node = ast.AnnAssign(target=node.targets[0],
                             annotation=None,
                             value=node.value,
                             lineno=node.lineno,
                             col_offset=node.col_offset)
        self._variables_without_annotation.append(Variable(name,
                                                           None,
                                                           node,
                                                           docstring))
        body[item_index] = node

        if docstring is None:
            return 0
        else:
            return 1

    def visit_enum_member_assign(self, node):
        if len(node.targets) != 1:
            raise CompileError("invalid enum member syntax", node)

        if not isinstance(node.targets[0], ast.Name):
            raise CompileError("invalid enum member syntax", node)

        name = node.targets[0].id
        sign = 1

        if isinstance(node.value, ast.Constant):
            if isinstance(node.value.value, tuple):
                if len(node.value.value) == 1:
                    return (name, node.value.value[0])

        if isinstance(node.value, ast.UnaryOp):
            if isinstance(node.value.op, ast.USub):
                sign = -1
            else:
                raise CompileError("invalid enum member value", node.value)

            value = node.value.operand
        else:
            value = node.value

        if isinstance(value, ast.Constant):
            if not isinstance(value.value, int):
                raise CompileError("invalid enum member value", value)

            value = sign * value.value
        else:
            raise CompileError("invalid enum member value", node.value)

        if self._next_enum_value is not None:
            if value < self._next_enum_value:
                raise CompileError("enum member value lower than for previous member",
                                   node.value)

        self._next_enum_value = (value + 1)

        return (name, value)

    def next_enum_value(self):
        if self._next_enum_value is None:
            self._next_enum_value = 0

        value = self._next_enum_value
        self._next_enum_value += 1

        return value

    def visit_enum_member_expression(self, node):
        if not isinstance(node.value, ast.Name):
            raise CompileError("invalid enum member syntax", node)

        name = node.value.id
        value = self.next_enum_value()

        return (name, value)

    def visit_enum_member(self, node):
        if isinstance(node, ast.Assign):
            name, value = self.visit_enum_member_assign(node)
        elif isinstance(node, ast.Expr):
            name, value = self.visit_enum_member_expression(node)
        else:
            raise CompileError("invalid enum member syntax", node)

        if not is_pascal_case(name):
            raise CompileError("enum member names must be pascal case", node)

        return (name, value)

    def visit_enum(self, node):
        enum_name = node.name

        if not is_pascal_case(enum_name):
            raise CompileError("enum names must be pascal case", node)

        if len(node.bases) == 0:
            type_name = 'i64'
        elif len(node.bases) == 1:
            type_name = node.bases[0].id

            if not is_integer_type(type_name):
                raise CompileError(f"integer type expected, not '{type_name}'",
                                   node.bases[0])
        else:
            raise CompileError("multiple enum types given", node)

        self._next_enum_value = None
        members = []
        body_iter = iter(node.body)
        docstring = get_docstring(node, body_iter)

        for item in body_iter:
            members.append(self.visit_enum_member(item))

        self._definitions.define_enum(enum_name,
                                      Enum(enum_name,
                                           type_name,
                                           members,
                                           docstring),
                                      node)

    def visit_trait(self, node, decorators):
        trait_name = node.name

        if not is_pascal_case(trait_name):
            raise CompileError("trait names must be pascal case", node)

        generic_types = decorators.get('generic', [])
        methods = defaultdict(list)
        body_iter = iter(node.body)
        docstring = get_docstring(node, body_iter)

        for item in body_iter:
            if isinstance(item, ast.FunctionDef):
                name = item.name
                check_method(item)
                method = MethodVisitor().visit(item)

                if method.name == '__init__':
                    raise CompileError("traits cannot have an __init__ method",
                                       item)

                if method.is_macro:
                    raise CompileError("traits cannot have macro methods", item)

                methods[name].append(method)
            elif isinstance(item, ast.AnnAssign):
                raise CompileError('traits cannot have members', item)

        self._definitions.define_trait(trait_name,
                                       Trait(trait_name,
                                             generic_types,
                                             methods,
                                             node,
                                             docstring),
                                       node)

    def visit_class(self, node, decorators):
        class_name = node.name

        if not is_pascal_case(class_name):
            raise CompileError("class names must be pascal case", node)

        methods = defaultdict(list)
        members = {}

        generic_types = decorators.get('generic', [])
        implements = [
            Implement(TypeVisitor().visit(trait), trait)
            for trait in node.bases
        ]

        body_iter = iter(node.body)
        docstring = get_docstring(node, body_iter)

        for item in body_iter:
            if isinstance(item, ast.FunctionDef):
                name = item.name
                check_method(item)
                method = MethodVisitor().visit(item)
                validate_method_signature(method, item)
                methods[name].append(method)
            elif isinstance(item, ast.AnnAssign):
                name = item.target.id

                if not is_snake_case(name):
                    raise CompileError("class member names must be snake case", item)

                members[name] = Member(name,
                                       TypeVisitor().visit(item.annotation),
                                       item)

                if item.value is not None:
                    raise CompileError("class members cannot have default values",
                                       item.value)

        self._definitions.define_class(class_name,
                                       Class(class_name,
                                             generic_types,
                                             members,
                                             methods,
                                             implements,
                                             node,
                                             None,
                                             docstring),
                                       node)

    def visit_ClassDef(self, node):
        allowed_decorators = ['enum', 'trait', 'generic']
        decorators = visit_decorator_list(node.decorator_list, allowed_decorators)

        if 'enum' in decorators:
            self.visit_enum(node)
        elif 'trait' in decorators:
            self.visit_trait(node, decorators)
        else:
            self.visit_class(node, decorators)

    def visit_FunctionDef(self, node):
        if is_test(node):
            self._definitions.define_test(node.name,
                                          TestVisitor().visit(node),
                                          node)
        else:
            self._definitions.define_function(node.name,
                                              FunctionVisitor().visit(node),
                                              node)

def find_definitions(tree, source_lines, module_levels, module_name):
    """Find all definitions in given tree and return them.

    """

    return DefinitionsVisitor(source_lines,
                              module_levels,
                              module_name).visit(tree)


class MakeFullyQualifiedNames:

    def __init__(self, module, module_definitions):
        self.module = module
        self.module_definitions = module_definitions

    def process_type(self, mys_type):
        if isinstance(mys_type, list):
            return [self.process_type(mys_type[0])]
        elif isinstance(mys_type, Set):
            return Set(self.process_type(mys_type.value_type))
        elif isinstance(mys_type, Dict):
            return Dict(self.process_type(mys_type.key_type),
                        self.process_type(mys_type.value_type))
        elif isinstance(mys_type, Tuple):
            return Tuple([self.process_type(item) for item in mys_type])
        elif isinstance(mys_type, GenericType):
            mys_type.name = self.process_type(mys_type.name)
            types = []

            for type_ in mys_type.types:
                types.append(self.process_type(type_))

            mys_type.types = types

            return mys_type
        elif isinstance(mys_type, Optional):
            return Optional(self.process_type(mys_type.mys_type), mys_type.node)
        elif isinstance(mys_type, Weak):
            mys_type.mys_type = self.process_type(mys_type.mys_type)

            return mys_type
        elif mys_type in self.module_definitions.classes:
            return f'{self.module}.{mys_type}'
        elif mys_type in self.module_definitions.traits:
            return f'{self.module}.{mys_type}'
        elif mys_type in self.module_definitions.enums:
            return f'{self.module}.{mys_type}'
        elif mys_type in self.module_definitions.imports:
            imported_module, new_type = self.module_definitions.imports[mys_type][0]

            return f'{imported_module}.{new_type}'
        else:
            return mys_type

    def process_function(self, function):
        function.returns = self.process_type(function.returns)

        for param, _ in function.args:
            param.type = self.process_type(param.type)

    def process_variable(self, variable_definition):
        variable_definition.type = self.process_type(variable_definition.type)

    def process_class(self, class_definition):
        for implement in class_definition.implements:
            if implement.name() != 'Error':
                implement.type = self.process_type(implement.type)

        for member in class_definition.members.values():
            member.type = self.process_type(member.type)

        for methods in class_definition.methods.values():
            for method in methods:
                self.process_function(method)

    def process_trait(self, trait_definition):
        for methods in trait_definition.methods.values():
            for method in methods:
                self.process_function(method)

    def process_module(self):
        """Make variable types, members, parameters and return types and
        implemented traits fully qualified names.

        """

        for variable_definition in self.module_definitions.variables.values():
            self.process_variable(variable_definition)

        for class_definition in self.module_definitions.classes.values():
            self.process_class(class_definition)

        for trait_definition in self.module_definitions.traits.values():
            self.process_trait(trait_definition)

        for functions in self.module_definitions.functions.values():
            for function in functions:
                self.process_function(function)

    def process(self):
        return self.process_module()


def make_fully_qualified_names_module(module, module_definitions):
    """Make variable types, members, parameters and return types and
    implemented traits fully qualified names.

    """

    return MakeFullyQualifiedNames(module, module_definitions).process()
