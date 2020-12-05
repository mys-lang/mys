from collections import defaultdict
from .parser import ast
from .utils import LanguageError
from .utils import is_snake_case
from .utils import is_upper_snake_case
from .utils import is_pascal_case
from .utils import TypeVisitor
from .utils import is_integer_literal
from .utils import is_float_literal

class Function:

    def __init__(self, name, generic_types, raises, is_test, args, returns, node):
        self.name = name
        self.generic_types = generic_types
        self.raises = raises
        self.is_test = is_test
        self.args = args
        self.returns = returns
        self.node = node

class Member:

    def __init__(self, name, type_):
        self.name = name
        self.type = type_

class Class:

    def __init__(self, name, generic_types, members, methods, functions):
        self.name = name
        self.generic_types = generic_types
        self.members = members
        self.methods = methods
        self.functions = functions

class Trait:

    def __init__(self, name, methods):
        self.name = name
        self.methods = methods

class Enum:

    def __init__(self, name, type_, members):
        self.name = name
        self.type = type_
        self.members = members

class Variable:

    def __init__(self, name, type_, node):
        self.name = name
        self.type = type_
        self.node = node

class Definitions:
    """Defined variables, classes, traits, enums and functions for one
    module. This information is useful when verifying that modules
    uses this module correctly.

    All function and method names are guaranteed to be snake
    case. Same applies to their parameter anmes.

    All classes, traits and enums names are guaranteed to be pascal
    case.

    Variable names can either be lower or upper case snake case.

    """

    def __init__(self):
        self.variables = {}
        self.classes = {}
        self.traits = {}
        self.enums = {}
        self.functions = defaultdict(list)

    def _check_unique_name(self, name, node, is_function=False):
        if name in self.variables:
            raise LanguageError(f"there is already a variable called '{name}'",
                                node.lineno,
                                node.col_offset)

        if name in self.classes:
            raise LanguageError(f"there is already a class called '{name}'",
                                node.lineno,
                                node.col_offset)

        if name in self.traits:
            raise LanguageError(f"there is already a trait called '{name}'",
                                node.lineno,
                                node.col_offset)

        if name in self.enums:
            raise LanguageError(f"there is already an enum called '{name}'",
                                node.lineno,
                                node.col_offset)

        if not is_function:
            if name in self.functions:
                raise LanguageError(f"there is already a function called '{name}'",
                                    node.lineno,
                                    node.col_offset)

    def define_variable(self, name, value, node):
        self._check_unique_name(name, node)
        self.variables[name] = value

    def define_class(self, name, value, node):
        self._check_unique_name(name, node)
        self.classes[name] = value

    def define_trait(self, name, value, node):
        self._check_unique_name(name, node)
        self.traits[name] = value

    def define_enum(self, name, value, node):
        self._check_unique_name(name, node)
        self.enums[name] = value

    def define_function(self, name, value, node):
        self._check_unique_name(name, node, True)
        self.functions[name].append(value)

def is_method(node):
    return len(node.args) >= 1 and node.args[0].arg == 'self'

class FunctionVisitor(TypeVisitor):

    ALLOWED_DECORATORS = ['generic', 'test', 'raises']

    def visit_arg(self, node):
        if node.annotation is None:
            raise LanguageError("parameters must have a type",
                                node.lineno,
                                node.col_offset)

        if not is_snake_case(node.arg):
            raise LanguageError("parameter names must be snake case",
                                node.lineno,
                                node.col_offset)

        return (node.arg, self.visit(node.annotation))

    def visit_arguments(self, node):
        return [self.visit(arg) for arg in node.args]

    def visit_FunctionDef(self, node):
        if not is_snake_case(node.name):
            raise LanguageError("function names must be snake case",
                                node.lineno,
                                node.col_offset)

        decorators = visit_decorator_list(node.decorator_list,
                                          self.ALLOWED_DECORATORS)
        args = self.visit(node.args)

        if node.returns is None:
            returns = None
        else:
            returns = FunctionVisitor().visit(node.returns)

        return Function(node.name,
                        decorators.get('generic', []),
                        decorators.get('raises', []),
                        'test' in decorators,
                        args,
                        returns,
                        node)

class MethodVisitor(FunctionVisitor):

    ALLOWED_DECORATORS = ['generic', 'raises']

    def visit_arguments(self, node):
        return [self.visit(arg) for arg in node.args[1:]]

def visit_decorator_list(decorator_list, allowed_decorators):
    decorators = {}

    for decorator in decorator_list:
        if isinstance(decorator, ast.Call):
            name = decorator.func.id
            values = []

            for arg in decorator.args:
                if not isinstance(arg, ast.Name):
                    raise LanguageError("invalid decorator value",
                                        arg.lineno,
                                        arg.col_offset)

                if arg.id in values:
                    raise LanguageError(f"'{arg.id}' can only be given once",
                                        arg.lineno,
                                        arg.col_offset)

                values.append(arg.id)
        elif isinstance(decorator, ast.Name):
            name = decorator.id
            values = []

            if name == 'enum':
                values.append('i64')
        else:
            raise LanguageError("decorators must be @name or @name()",
                                decorator.lineno,
                                decorator.col_offset)

        if name not in allowed_decorators:
            raise LanguageError(f"invalid decorator '{name}'",
                                decorator.lineno,
                                decorator.col_offset)

        if name in decorators:
            raise LanguageError(f"@{name} can only be given once",
                                decorator.lineno,
                                decorator.col_offset)

        if name == 'enum':
            if len(values) != 1:
                raise LanguageError("invalid enum decorator value",
                                    decorator.lineno,
                                    decorator.col_offset)

            decorators['enum'] = values[0]
        elif name == 'trait':
            if values:
                raise LanguageError("@trait does not take any values",
                                    decorator.lineno,
                                    decorator.col_offset)

            decorators['trait'] = None
        elif name == 'test':
            if values:
                raise LanguageError("@test does not take any values",
                                    decorator.lineno,
                                    decorator.col_offset)

            decorators['test'] = None
        elif name == 'generic':
            if not values:
                raise LanguageError("@generic requires at least one type",
                                    decorator.lineno,
                                    decorator.col_offset)

            decorators['generic'] = values
        elif name == 'raises':
            if not values:
                raise LanguageError("@raises requires at least one error",
                                    decorator.lineno,
                                    decorator.col_offset)

            decorators['raises'] = values

    return decorators

class DefinitionsVisitor(ast.NodeVisitor):

    def __init__(self):
        super().__init__()
        self._definitions = Definitions()
        self._enum_value = 0

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

        return self._definitions

    def next_enum_value(self):
        value = self._enum_value
        self._enum_value += 1

        return value

    def visit_enum_member_expression(self, node):
        if not isinstance(node.value, ast.Name):
            raise LanguageError("invalid enum member name",
                                node.lineno,
                                node.col_offset)

        name = node.value.id
        value = self.next_enum_value()

        return (name, value)

    def visit_Assign(self, node):
        raise LanguageError("global variable types can't be inferred",
                            node.lineno,
                            node.col_offset)

    def visit_AnnAssign(self, node):
        name = node.target.id

        if not is_upper_snake_case(name):
            raise LanguageError(
                "global variable names must be upper case snake case",
                node.lineno,
                node.col_offset)

        self._definitions.define_variable(
            name,
            Variable(name,
                     TypeVisitor().visit(node.annotation),
                     node),
            node)

    def visit_enum_member_assign(self, node):
        if len(node.targets) != 1:
            raise LanguageError("invalid enum member syntax",
                                node.lineno,
                                node.col_offset)

        if not isinstance(node.targets[0], ast.Name):
            raise LanguageError("invalid enum member name",
                                node.lineno,
                                node.col_offset)

        name = node.targets[0].id
        sign = 1

        # ToDo: How to handle embedded C++?
        if isinstance(node.value, ast.UnaryOp):
            if isinstance(node.value.op, ast.USub):
                sign = -1
            else:
                raise LanguageError("invalid enum member value",
                                    node.value.lineno,
                                    node.value.col_offset)

            value = node.value.operand
        else:
            value = node.value

        if isinstance(value, ast.Constant):
            if not isinstance(value.value, int):
                raise LanguageError("invalid enum member value",
                                    value.lineno,
                                    value.col_offset)

            value = sign * value.value
        else:
            raise LanguageError("invalid enum member value",
                                node.value.lineno,
                                node.value.col_offset)

        self._enum_value = (value + 1)

        return (name, value)

    def visit_enum_member(self, node):
        if isinstance(node, ast.Assign):
            name, value = self.visit_enum_member_assign(node)
        elif isinstance(node, ast.Expr):
            name, value = self.visit_enum_member_expression(node)
        else:
            raise LanguageError("invalid enum member syntax",
                                node.lineno,
                                node.col_offset)

        if not is_pascal_case(name):
            raise LanguageError("enum member names must be pascal case",
                                node.lineno,
                                node.col_offset)

        return (name, value)

    def visit_enum(self, node, decorators):
        enum_name = node.name

        if not is_pascal_case(enum_name):
            raise LanguageError("enum names must be pascal case",
                                node.lineno,
                                node.col_offset)

        self._enum_value = 0
        members = []

        for item in node.body:
            members.append(self.visit_enum_member(item))

        self._definitions.define_enum(enum_name,
                                      Enum(enum_name,
                                           decorators['enum'],
                                           members),
                                      node)

    def visit_trait(self, node, decorators):
        trait_name = node.name

        if not is_pascal_case(trait_name):
            raise LanguageError("trait names must be pascal case",
                                node.lineno,
                                node.col_offset)

        methods = defaultdict(list)

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                name = item.name

                if is_method(item.args):
                    methods[name].append(MethodVisitor().visit(item))

        self._definitions.define_trait(trait_name,
                                       Trait(trait_name, methods),
                                       node)

    def visit_class(self, node, decorators):
        class_name = node.name

        if not is_pascal_case(class_name):
            raise LanguageError("class names must be pascal case",
                                node.lineno,
                                node.col_offset)

        methods = defaultdict(list)
        functions = defaultdict(list)
        members = {}

        generic_types = decorators.get('generic', [])

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                name = item.name

                if is_method(item.args):
                    methods[name].append(MethodVisitor().visit(item))
                else:
                    functions[name].append(FunctionVisitor().visit(item))
            elif isinstance(item, ast.AnnAssign):
                name = item.target.id

                if not is_snake_case(name):
                    raise LanguageError("class member names must be snake case",
                                        item.lineno,
                                        item.col_offset)

                members[name] = Member(name,
                                       TypeVisitor().visit(item.annotation))

        self._definitions.define_class(class_name,
                                       Class(class_name,
                                             generic_types,
                                             members,
                                             methods,
                                             functions),
                                       node)

    def visit_ClassDef(self, node):
        decorators = visit_decorator_list(node.decorator_list,
                                          ['enum', 'trait', 'generic'])

        if 'enum' in decorators:
            self.visit_enum(node, decorators)
        elif 'trait' in decorators:
            self.visit_trait(node, decorators)
        else:
            self.visit_class(node, decorators)

    def visit_FunctionDef(self, node):
        self._definitions.define_function(node.name,
                                          FunctionVisitor().visit(node),
                                          node)

def find_definitions(tree):
    """Find all definitions in given tree and return them.

    """

    return DefinitionsVisitor().visit(tree)
