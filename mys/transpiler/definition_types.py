from collections import defaultdict
from textwrap import indent

from ..parser import ast
from .utils import METHOD_TO_OPERATOR
from .utils import CompileError
from .utils import GenericType
from .utils import format_mys_type
from .utils import is_char
from .utils import make_function_name


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


class Function:

    def __init__(self,
                 name,
                 generic_types,
                 raises,
                 is_macro,
                 is_iterator,
                 args,
                 returns,
                 node,
                 module_name=None,
                 is_overloaded=False,
                 docstring=None):
        self.name = name
        self.generic_types = generic_types
        self.raises = raises
        self.is_macro = is_macro
        self.is_iterator = is_iterator
        self.args = args
        self.returns = returns
        self.node = node
        self.module_name = module_name
        self.is_overloaded = is_overloaded
        self.docstring = docstring

    def is_generic(self):
        return bool(self.generic_types)

    def make_name(self):
        if self.is_overloaded:
            return make_function_name(
                self.name,
                [param.type for param, _ in self.args],
                self.returns)
        else:
            return self.name

    def signature_string(self, method):
        params = []

        for param, default in self.args:
            param = f'{param.name}: {format_mys_type(param.type)}'

            if default is not None:
                param += ' = '
                param += FormatDefaultVisitor().visit(default)

            params.append(param)

        params_string = ', '.join(params)

        if len(params_string) > 60:
            if method:
                if params:
                    params = ['self'] + params
                else:
                    params = ['self']

            params_string = indent(',\n'.join(params),
                                   ' ' * (len(self.name) + 6)).strip()
        else:
            if method:
                if params_string:
                    params_string = 'self, ' + params_string
                else:
                    params_string = 'self'

        if self.returns is None:
            returns = ''
        else:
            returns = f' -> {format_mys_type(self.returns)}'

        name = METHOD_TO_OPERATOR.get(self.name, self.name)

        return f'{name}({params_string}){returns}'


class Test:

    def __init__(self, name, node, docstring=None):
        self.name = name
        self.node = node
        self.docstring = docstring


class Param:

    def __init__(self, name, type_, node):
        self.name = name
        self.type = type_
        self.node = node


class Member:

    def __init__(self, name, type_, node):
        self.name = name
        self.type = type_
        self.node = node


class Class:

    def __init__(self,
                 name,
                 generic_types,
                 members,
                 methods,
                 implements,
                 node,
                 module_name=None,
                 docstring=None):
        self.name = name
        self.generic_types = generic_types
        self.members = members
        self.methods = methods
        self.implements = implements
        self.node = node
        self.module_name = module_name
        self.docstring = docstring

    def is_generic(self):
        return bool(self.generic_types)

    def implements_trait(self, name):
        for implement in self.implements:
            if name == implement.name():
                return True

        return False


class Implement:

    def __init__(self, type_, node):
        self.type = type_
        self.node = node

    def name(self):
        if isinstance(self.type, GenericType):
            return self.type.name
        else:
            return self.type


class Trait:

    def __init__(self, name, generic_types, methods, node, docstring):
        self.name = name
        self.generic_types = generic_types
        self.methods = methods
        self.node = node
        self.docstring = docstring

    def is_generic(self):
        return bool(self.generic_types)


class Enum:

    def __init__(self, name, type_, members, docstring):
        self.name = name
        self.type = type_
        self.members = members
        self.member_names = {name for name, _ in members}
        self.docstring = docstring


class Variable:

    def __init__(self,
                 name,
                 type_,
                 node,
                 docstring):
        self.name = name
        self.type = type_
        self.node = node
        self.docstring = docstring


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

    def __init__(self, module_name):
        self.module_name = module_name
        self.variables = {}
        self.classes = {}
        self.traits = {}
        self.enums = {}
        self.functions = defaultdict(list)
        self.imports = defaultdict(list)
        self.tests = {}

    def _check_unique_name(self, name, node, is_function=False):
        if name in self.variables:
            raise CompileError(f"there is already a variable called '{name}'", node)

        if name in self.classes:
            raise CompileError(f"there is already a class called '{name}'", node)

        if name in self.traits:
            raise CompileError(f"there is already a trait called '{name}'", node)

        if name in self.enums:
            raise CompileError(f"there is already an enum called '{name}'", node)

        if name in self.imports:
            raise CompileError(f"'{name}' is already imported", node)

        if not is_function:
            if name in self.functions:
                raise CompileError(f"there is already a function called '{name}'",
                                   node)

    def define_variable(self, name, value, node):
        self._check_unique_name(name, node)
        self.variables[name] = value

    def define_class(self, name, value, node):
        self._check_unique_name(name, node)
        value.module_name = self.module_name
        self.classes[name] = value

    def define_trait(self, name, value, node):
        self._check_unique_name(name, node)
        self.traits[name] = value

    def define_enum(self, name, value, node):
        self._check_unique_name(name, node)
        self.enums[name] = value

    def define_function(self, name, value, node):
        self._check_unique_name(name, node, True)
        value.module_name = self.module_name
        functions = self.functions[name]

        if functions:
            value.is_overloaded = True

            for function in functions:
                function.is_overloaded = True

        functions.append(value)

    def define_test(self, name, value, node):
        if name in self.tests:
            raise CompileError(f"there is already a test called '{name}'", node)

        self.tests[name] = value

    def add_import(self, module, name, asname, node):
        self._check_unique_name(asname, node)
        self.imports[asname].append((module, name))
