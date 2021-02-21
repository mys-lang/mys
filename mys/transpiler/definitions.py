from collections import defaultdict
from textwrap import indent

from ..parser import ast
from .utils import INTEGER_TYPES
from .utils import METHOD_BIN_OPERATORS
from .utils import CompileError
from .utils import GenericType
from .utils import format_mys_type
from .utils import get_import_from_info
from .utils import has_docstring
from .utils import is_pascal_case
from .utils import is_snake_case
from .utils import is_upper_snake_case
from .utils import make_function_name


class TypeVisitor(ast.NodeVisitor):

    def visit_Name(self, node):
        return node.id

    def visit_List(self, node):
        nitems = len(node.elts)

        if nitems != 1:
            raise CompileError(f"expected 1 type in list, got {nitems}", node)

        return [self.visit(elem) for elem in node.elts]

    def visit_Tuple(self, node):
        return tuple(self.visit(elem) for elem in node.elts)

    def visit_Dict(self, node):
        return {node.keys[0].id: self.visit(node.values[0])}

    def visit_Set(self, node):
        nitems = len(node.elts)

        if nitems != 1:
            raise CompileError(f"expected 1 type in set, got {nitems}", node)

        return {self.visit(node.elts[0])}

    def visit_Subscript(self, node):
        types = self.visit(node.slice)

        if isinstance(node.slice, ast.Name):
            types = [types]
        else:
            types = list(types)

        return GenericType(self.visit(node.value), types, node)


class FormatDefaultVisitor(ast.NodeVisitor):

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return f'"{node.value}"'
        elif isinstance(node.value, tuple) and len(node.value) == 3:
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

class Function:

    def __init__(self,
                 name,
                 generic_types,
                 raises,
                 is_test,
                 args,
                 returns,
                 node,
                 module_name=None,
                 is_overloaded=False,
                 docstring=None):
        self.name = name
        self.generic_types = generic_types
        self.raises = raises
        self.is_test = is_test
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
                                   ' ' * (len(self.name) + 5)).strip()
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

        return f'{self.name}({params_string}){returns}'

    def __str__(self):
        args = [f'{param.name}: {param.type}' for param, _ in self.args]

        return (
            f'Function(name={self.name}, generic_types={self.generic_types}, '
            f'args={args}, returns={self.returns}, module_name={self.module_name}, '
            f'is_overloaded={self.is_overloaded})')

class Param:

    def __init__(self, name, type_, node):
        self.name = name
        self.type = type_
        self.node = node

    def __str__(self):
        return f'Param(name={self.name}, type={self.type})'

class Member:

    def __init__(self, name, type_, node):
        self.name = name
        self.type = type_
        self.node = node

    def __str__(self):
        return f'Member(name={self.name}, type={self.type})'


class Class:

    def __init__(self,
                 name,
                 generic_types,
                 members,
                 methods,
                 functions,
                 implements,
                 node,
                 module_name=None,
                 docstring=None):
        self.name = name
        self.generic_types = generic_types
        self.members = members
        self.methods = methods
        self.functions = functions
        self.implements = implements
        self.node = node
        self.module_name = module_name
        self.docstring = docstring

    def is_generic(self):
        return bool(self.generic_types)

    def __str__(self):
        members = [str(member) for member in self.members.values()]
        methods = []
        functions = []

        for methods_by_name in self.methods.values():
            for method in methods_by_name:
                methods.append(str(method))

        for functions_by_name in self.functions.values():
            for function in functions_by_name:
                functions.append(str(function))

        return (
            f'Class(name={self.name}, generic_types={self.generic_types}, '
            f'members={members}, methods={methods}, '
            f'functions={functions}, implements={self.implements})')


class Trait:

    def __init__(self, name, methods, node, docstring):
        self.name = name
        self.methods = methods
        self.node = node
        self.docstring = docstring


class Enum:

    def __init__(self, name, type_, members, docstring):
        self.name = name
        self.type = type_
        self.members = members
        self.member_names = {name for name, _ in members}
        self.docstring = docstring


class Variable:

    def __init__(self, name, type_, node):
        self.name = name
        self.type = type_
        self.node = node

    def __str__(self):
        return f'Variable(name={self.name}, type={self.type})'

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
            functions[0].is_overloaded = True

        functions.append(value)

    def add_import(self, module, name, asname):
        self.imports[asname].append((module, name))

    def __str__(self):
        result = ['Definitions:']

        result.append('  Variables:')

        for definition in self.variables.values():
            result.append(f'    {definition.name}: {definition.type}')

        result.append('  Classes:')

        for definition in self.classes.values():
            bases = ', '.join(definition.implements)
            result.append(f'    {definition.name}({bases}):')

            for member in definition.members.values():
                result.append(f'      {member.name}: {member.type}')

            for methods in definition.methods.values():
                for method in methods:
                    params = ', '.join([
                        f'{param.name}: {param.type}'
                        for param, _ in method.args
                    ])
                    result.append(
                        f'      {method.name}({params}) -> {method.returns}')

        result.append('  Traits:')

        for definition in self.traits.values():
            result.append(f'    {definition.name}:')

            for methods in definition.methods.values():
                for method in methods:
                    params = ', '.join([
                        f'{param.name}: {param.type}'
                        for param, _ in method.args
                    ])
                    result.append(
                        f'      {method.name}({params}) -> {method.returns}')

        result.append('  Enums:')

        for enum in self.enums:
            result.append(f'    {enum}')

        result.append('  Functions:')

        for functions in self.functions.values():
            for function in functions:
                params = ', '.join([
                    f'{param.name}: {param.type}'
                    for param, _ in function.args
                ])
                result.append(
                    f'    {function.name}({params}) -> {function.returns}')

        return '\n'.join(result)


def is_method(node):
    return len(node.args) >= 1 and node.args[0].arg == 'self'


class FunctionVisitor(TypeVisitor):

    ALLOWED_DECORATORS = ['generic', 'test', 'raises']

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
        if not is_snake_case(node.name):
            raise CompileError("function names must be snake case", node)

        decorators = visit_decorator_list(node.decorator_list,
                                          self.ALLOWED_DECORATORS)
        args = self.visit(node.args)

        if node.returns is None:
            returns = None
        else:
            returns = FunctionVisitor().visit(node.returns)

        if has_docstring(node):
            docstring = node.body[0].value.value
        else:
            docstring = None

        return Function(node.name,
                        decorators.get('generic', []),
                        decorators.get('raises', []),
                        'test' in decorators,
                        args,
                        returns,
                        node,
                        None,
                        None,
                        docstring)


class MethodVisitor(FunctionVisitor):

    ALLOWED_DECORATORS = ['generic', 'raises']

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

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

        return self._definitions

    def visit_ImportFrom(self, node):
        self._definitions.add_import(*get_import_from_info(node, self._module_levels))

    def visit_Assign(self, node):
        raise CompileError("global variable types cannot be inferred", node)

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

    def visit_enum(self, node, decorators):
        enum_name = node.name

        if not is_pascal_case(enum_name):
            raise CompileError("enum names must be pascal case", node)

        self._next_enum_value = None
        members = []
        body_iter = iter(node.body)

        if has_docstring(node):
            docstring = node.body[0].value.value
            next(body_iter)
        else:
            docstring = None

        for item in body_iter:
            members.append(self.visit_enum_member(item))

        self._definitions.define_enum(enum_name,
                                      Enum(enum_name,
                                           decorators['enum'],
                                           members,
                                           docstring),
                                      node)

    def visit_trait(self, node):
        trait_name = node.name

        if not is_pascal_case(trait_name):
            raise CompileError("trait names must be pascal case", node)

        methods = defaultdict(list)
        body_iter = iter(node.body)

        if has_docstring(node):
            docstring = node.body[0].value.value
            next(body_iter)
        else:
            docstring = None

        for item in body_iter:
            if isinstance(item, ast.FunctionDef):
                name = item.name

                if is_method(item.args):
                    methods[name].append(MethodVisitor().visit(item))
            elif isinstance(item, ast.AnnAssign):
                raise CompileError('traits cannot have members', item)

        self._definitions.define_trait(trait_name,
                                       Trait(trait_name, methods, node, docstring),
                                       node)

    def visit_class(self, node, decorators):
        class_name = node.name

        if not is_pascal_case(class_name):
            raise CompileError("class names must be pascal case", node)

        methods = defaultdict(list)
        functions = defaultdict(list)
        members = {}

        generic_types = decorators.get('generic', [])
        implements = {
            trait.id: trait
            for trait in node.bases
        }
        body_iter = iter(node.body)

        if has_docstring(node):
            docstring = node.body[0].value.value
            next(body_iter)
        else:
            docstring = None

        for item in body_iter:
            if isinstance(item, ast.FunctionDef):
                name = item.name

                if is_method(item.args):
                    method = MethodVisitor().visit(item)
                    validate_method_signature(method, item)
                    methods[name].append(method)
                else:
                    functions[name].append(FunctionVisitor().visit(item))
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
                                             functions,
                                             implements,
                                             node,
                                             None,
                                             docstring),
                                       node)

    def visit_ClassDef(self, node):
        decorators = visit_decorator_list(node.decorator_list,
                                          ['enum', 'trait', 'generic'])

        if 'enum' in decorators:
            self.visit_enum(node, decorators)
        elif 'trait' in decorators:
            self.visit_trait(node)
        else:
            self.visit_class(node, decorators)

    def visit_FunctionDef(self, node):
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
        elif isinstance(mys_type, set):
            return {self.process_type(list(mys_type)[0])}
        elif isinstance(mys_type, dict):
            return {
                self.process_type(list(mys_type.keys())[0]):
                self.process_type(list(mys_type.values())[0])
            }
        elif isinstance(mys_type, tuple):
            return tuple(self.process_type(item) for item in mys_type)
        elif isinstance(mys_type, GenericType):
            mys_type.name = self.process_type(mys_type.name)
            types = []

            for type_ in mys_type.types:
                types.append(self.process_type(type_))

            mys_type.types = types

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
        for base in list(class_definition.implements):
            node = class_definition.implements.pop(base)

            if base in self.module_definitions.traits:
                base = self.process_type(base)
            elif base in self.module_definitions.imports:
                imported_module, name = self.module_definitions.imports[base][0]
                base = f'{imported_module}.{name}'
            elif base == 'Error':
                pass
            else:
                raise CompileError('trait does not exist', node)

            class_definition.implements[base] = node

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
