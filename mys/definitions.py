import re
from collections import defaultdict
from .parser import ast
from .utils import LanguageError

SNAKE_CASE_RE = re.compile(r'(_*[a-z][a-z0-9_]*)')
PASCAL_CASE_RE = re.compile(r'_?[A-Z][a-zA-Z0-9]*')

def is_snake_case(value):
    return SNAKE_CASE_RE.match(value)

def is_pascal_case(value):
    return PASCAL_CASE_RE.match(value)

class Function:

    def __init__(self, name, generic_types, raises, args, returns):
        self.name = name
        self.generic_types = generic_types
        self.raises = raises
        self.args = args
        self.returns = returns

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

    def __init__(self, name, type_):
        self.name = name
        self.type = type_

class Definitions:
    """Defined variables, classes, traits, enums and functions for one
    module. This information is useful when verifying that modules
    uses this module correctly.

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

class TypeVisitor(ast.NodeVisitor):

    def visit_Name(self, node):
        return node.id

    def visit_List(self, node):
        return [self.visit(elem) for elem in node.elts]

    def visit_Tuple(self, node):
        return tuple([self.visit(elem) for elem in node.elts])

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
                        args,
                        returns)

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
            raise LanguageError(f"unsupported decorator '{name}'",
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
        else:
            raise LanguageError(f"unsupported decorator '@{name}'",
                                decorator.lineno,
                                decorator.col_offset)

    return decorators

class DefinitionsVisitor(ast.NodeVisitor):

    def __init__(self):
        super().__init__()
        self._definitions = Definitions()

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

        return self._definitions

    def visit_AnnAssign(self, node):
        name = node.target.id
        self._definitions.define_variable(name,
                                          TypeVisitor().visit(node.annotation),
                                          node)

    def visit_enum(self, node, decorators):
        enum_name = node.name

        if not is_pascal_case(enum_name):
            raise LanguageError("enum names must be pascal case",
                                node.lineno,
                                node.col_offset)

        self._definitions.define_enum(enum_name,
                                      Enum(enum_name, decorators['enum']),
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
