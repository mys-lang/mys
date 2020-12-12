from collections import defaultdict
from ..parser import ast
from .utils import CompileError
from .utils import is_snake_case
from .utils import is_upper_snake_case
from .utils import is_pascal_case
from .utils import TypeVisitor
from .utils import INTEGER_TYPES

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

    def __init__(self, name, generic_types, members, methods, functions, implements):
        self.name = name
        self.generic_types = generic_types
        self.members = members
        self.methods = methods
        self.functions = functions
        self.implements = implements

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
            raise CompileError(f"there is already a variable called '{name}'", node)

        if name in self.classes:
            raise CompileError(f"there is already a class called '{name}'", node)

        if name in self.traits:
            raise CompileError(f"there is already a trait called '{name}'", node)

        if name in self.enums:
            raise CompileError(f"there is already an enum called '{name}'", node)

        if not is_function:
            if name in self.functions:
                raise CompileError(f"there is already a function called '{name}'",
                                   node)

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
            raise CompileError("parameters must have a type", node)

        if not is_snake_case(node.arg):
            raise CompileError("parameter names must be snake case", node)

        return (node.arg, self.visit(node.annotation))

    def visit_arguments(self, node):
        return [self.visit(arg) for arg in node.args]

    def visit_FunctionDef(self, node):
        if not is_snake_case(node.name):
            raise CompileError("function names must be snake case", node)

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
                    raise CompileError("invalid decorator value", arg)

                if arg.id in values:
                    raise CompileError(f"'{arg.id}' can only be given once", arg)

                values.append(arg.id)
        elif isinstance(decorator, ast.Name):
            name = decorator.id
            values = []

            if name == 'enum':
                values.append('i64')
        else:
            raise CompileError("decorators must be @name or @name()", decorator)

        if name not in allowed_decorators:
            raise CompileError(f"invalid decorator '{name}'", decorator)

        if name in decorators:
            raise CompileError(f"@{name} can only be given once", decorator)

        if name == 'enum':
            if len(values) != 1:
                raise CompileError(f"one parameter expected, got {len(values)}",
                                   decorator)

            if values[0] not in INTEGER_TYPES:
                raise CompileError(f"integer type expected, not '{values[0]}'",
                                   decorator.args[0])

            decorators['enum'] = values[0]
        elif name == 'trait':
            if values:
                raise CompileError("no parameters expected", decorator)

            decorators['trait'] = None
        elif name == 'test':
            if values:
                raise CompileError("no parameters expected", decorator)

            decorators['test'] = None
        elif name == 'generic':
            if not values:
                raise CompileError("at least one parameter required", decorator)

            decorators['generic'] = values
        elif name == 'raises':
            if not values:
                raise CompileError("@raises requires at least one error", decorator)

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
            raise CompileError("invalid enum member name", node)

        name = node.value.id
        value = self.next_enum_value()

        return (name, value)

    def visit_Assign(self, node):
        raise CompileError("global variable types can't be inferred", node)

    def visit_AnnAssign(self, node):
        name = node.target.id

        if not is_upper_snake_case(name):
            raise CompileError(
                "global variable names must be upper case snake case", node)

        self._definitions.define_variable(
            name,
            Variable(name,
                     TypeVisitor().visit(node.annotation),
                     node),
            node)

    def visit_enum_member_assign(self, node):
        if len(node.targets) != 1:
            raise CompileError("invalid enum member syntax", node)

        if not isinstance(node.targets[0], ast.Name):
            raise CompileError("invalid enum member name", node)

        name = node.targets[0].id
        sign = 1

        # ToDo: How to handle embedded C++?
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

        self._enum_value = (value + 1)

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

    def visit_enum(self, node, decorators):
        enum_name = node.name

        if not is_pascal_case(enum_name):
            raise CompileError("enum names must be pascal case", node)

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
            raise CompileError("trait names must be pascal case", node)

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
            raise CompileError("class names must be pascal case", node)

        methods = defaultdict(list)
        functions = defaultdict(list)
        members = {}

        generic_types = decorators.get('generic', [])
        implements = [
            trait.id
            for trait in node.bases
        ]

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
                    raise CompileError("class member names must be snake case", item)

                members[name] = Member(name,
                                       TypeVisitor().visit(item.annotation))

        self._definitions.define_class(class_name,
                                       Class(class_name,
                                             generic_types,
                                             members,
                                             methods,
                                             functions,
                                             implements),
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
