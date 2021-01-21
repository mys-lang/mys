import re

from ..parser import ast
from .cpp_reserved import make_cpp_safe_name


class CompileError(Exception):

    def __init__(self, message, node):
        super().__init__()
        self.message = message
        self.lineno = node.lineno
        self.offset = node.col_offset


class InternalError(CompileError):
    pass


SNAKE_CASE_RE = re.compile(r'^(_*[a-z][a-z0-9_]*)$')
UPPER_SNAKE_CASE_RE = re.compile(r'^(_*[A-Z][A-Z0-9_]*)$')
PASCAL_CASE_RE = re.compile(r'^_?[A-Z][a-zA-Z0-9]*$')

INTEGER_TYPES = set(['i8', 'i16', 'i32', 'i64', 'u8', 'u16', 'u32', 'u64'])
NUMBER_TYPES = INTEGER_TYPES | set(['f32', 'f64'])
PRIMITIVE_TYPES = NUMBER_TYPES | set(['bool', 'char'])
BUILTIN_TYPES = PRIMITIVE_TYPES | set(['string', 'bytes'])

METHOD_OPERATORS = {
    '__add__': '+',
    '__sub__': '-',
    '__iadd__': '+=',
    '__isub__': '-=',
    '__eq__': '==',
    '__ne__': '!=',
    '__gt__': '>',
    '__ge__': '>=',
    '__lt__': '<',
    '__le__': '<='
}

BUILTIN_ERRORS = {
    'NoneError',
    'KeyError',
    'IndexError',
    'NotImplementedError',
    'AssertionError',
    'SystemExitError',
    'ValueError',
    'UnreachableError'
}

BUILTIN_CALLS = set(
    list(INTEGER_TYPES)
    + list(BUILTIN_ERRORS) + [
        'print',
        'char',
        'list',
        'input',
        'assert_eq',
        'str',
        'min',
        'max',
        'len',
        'abs',
        'f32',
        'f64',
        'enumerate',
        'range',
        'reversed',
        'slice',
        'sum',
        'zip'
    ])

OPERATORS = {
    ast.Add: '+',
    ast.Sub: '-',
    ast.Mult: '*',
    ast.Div: '/',
    ast.Mod: '%',
    ast.LShift: '<<',
    ast.RShift: '>>',
    ast.BitOr: '|',
    ast.BitXor: '^',
    ast.BitAnd: '&',
    ast.FloorDiv: '/',
    ast.Not: '!',
    ast.Invert: '~',
    ast.UAdd: '+',
    ast.USub: '-',
    ast.Is: '==',
    ast.Eq: '==',
    ast.NotEq: '!=',
    ast.Lt: '<',
    ast.LtE: '<=',
    ast.Gt: '>',
    ast.GtE: '>='
}

STRING_METHODS = {
    'to_utf8': [[], 'bytes'],
    'upper': [[], None],
    'lower': [[], None],
    'casefold': [[], None],
    'capitalize': [[], None],
    'starts_with': [['string'], 'bool'],
    'ends_with': [['string'], 'bool'],
    'join': [[['string']], 'string'],
    'to_lower': [[], 'string'],
    'to_upper': [[], 'string'],
    'to_casefold': [[], 'string'],
    'to_capitalize': [[], 'string'],
    'split': [['string'], ['string']],
    'strip': [['string'], None],
    'strip_left': [['string'], None],
    'strip_right': [['string'], None],
    'find': [['string|char', 'optional<i64>', 'optional<i64>'], 'i64'],
    'find_reverse': [['string|char', 'optional<i64>', 'optional<i64>'], 'i64'],
    'cut': [['string'], 'string'],
    'replace': [[None, None], None],
    'is_alpha': [[], 'bool'],
    'is_digit': [[], 'bool'],
    'is_numeric': [[], 'bool'],
    'is_space': [[], 'bool'],
    'match': [['regex'], 'regexmatch']
}

LIST_METHODS = {
    'append': [['<listtype>'], None],
    'extend': [['list<listtype>'], None],
    'insert': [['i64', '<listtype>'], None],
    'remove': [['<listtype>'], None],
    'reverse': [[], None],
    'sort': [[], None],
    'count': [['<listtype>'], 'i64'],
    'pop': [['i64'], '<listtype>'],
    'clear': [[], None]
}

REGEX_METHODS = {
    'split': [['string'], ['string']],
    'match': [['string'], 'regexmatch'],
    'replace': [['string', 'string'], 'string']
}

REGEXMATCH_METHODS = {
    'span': [[None], ('i64', 'i64')],
    'start': [[None], 'i64'],
    'end': [[None], 'i64'],
    'group': [[None], 'string'],
    'groups': [[None], ['string']],
    'group_dict': [[], {'string': 'string'}]
}


def is_snake_case(value):
    return SNAKE_CASE_RE.match(value) is not None


def is_upper_snake_case(value):
    return UPPER_SNAKE_CASE_RE.match(value) is not None


def is_pascal_case(value):
    return PASCAL_CASE_RE.match(value)


def is_primitive_type(mys_type):
    if not isinstance(mys_type, str):
        return False

    return mys_type in PRIMITIVE_TYPES


def dot2ns(name):
    # Hack...
    if name not in BUILTIN_CALLS and name != 'Error':
        name = f'mys.{name}'

    # ToDo: Super hack...
    if name == 'mys.fiber.lib.Fiber':
        name = 'Fiber'

    return name.replace('.', '::')


def make_name(name):
    return make_cpp_safe_name(name)


def split_dict_mys_type(mys_type):
    key_mys_type = list(mys_type.keys())[0]
    value_mys_type = list(mys_type.values())[0]

    return key_mys_type, value_mys_type


def make_relative_import_absolute(module_levels, module, node):
    prefix = '.'.join(module_levels[0:-node.level])

    if not prefix:
        raise CompileError('relative import is outside package', node)

    if module is None:
        module = prefix
    else:
        module = f'{prefix}.{module}'

    return module


def is_relative_import(node):
    return node.level > 0


def get_import_from_info(node, module_levels):
    module = node.module

    if is_relative_import(node):
        module = make_relative_import_absolute(module_levels, module, node)

    if '.' not in module:
        module += '.lib'

    if len(node.names) != 1:
        raise CompileError(f'only one import is allowed, found {len(node.names)}',
                           node)

    name = node.names[0]

    if name.asname:
        asname = name.asname
    else:
        asname = name.name

    return module, name.name, asname


def make_shared(cpp_type, values):
    return f'std::make_shared<{cpp_type}>({values})'


def shared_list_type(cpp_type):
    return f'SharedList<{cpp_type}>'


def make_shared_list(cpp_type, value):
    return (f'std::make_shared<List<{cpp_type}>>('
            f'std::initializer_list<{cpp_type}>{{{value}}})')


def shared_dict_type(key_cpp_type, value_cpp_type):
    return f'SharedDict<{key_cpp_type}, {value_cpp_type}>'


def make_shared_dict(key_cpp_type, value_cpp_type, items):
    return (f'std::make_shared<Dict<{key_cpp_type}, {value_cpp_type}>>('
            f'std::initializer_list<robin_hood::pair<{key_cpp_type}, '
            f'{value_cpp_type}>>{{{items}}})')


def shared_tuple_type(items):
    return f'SharedTuple<{items}>'


def mys_to_cpp_type(mys_type, context):
    if isinstance(mys_type, tuple):
        items = ', '.join([mys_to_cpp_type(item, context) for item in mys_type])

        return shared_tuple_type(items)
    elif isinstance(mys_type, list):
        item = mys_to_cpp_type(mys_type[0], context)

        return shared_list_type(item)
    elif isinstance(mys_type, dict):
        key_mys_type, value_mys_type = split_dict_mys_type(mys_type)
        key = mys_to_cpp_type(key_mys_type, context)
        value = mys_to_cpp_type(value_mys_type, context)

        return shared_dict_type(key, value)
    else:
        if mys_type == 'string':
            return 'String'
        elif mys_type == 'bool':
            return 'Bool'
        elif mys_type == 'char':
            return 'Char'
        elif mys_type == 'bytes':
            return 'Bytes'
        elif mys_type == 'regexmatch':
            return 'RegexMatch'
        elif context.is_class_or_trait_defined(mys_type):
            return f'std::shared_ptr<{dot2ns(mys_type)}>'
        elif context.is_enum_defined(mys_type):
            return context.get_enum_type(mys_type)
        else:
            return mys_type


def mys_to_cpp_type_param(mys_type, context):
    cpp_type = mys_to_cpp_type(mys_type, context)

    if not is_primitive_type(mys_type):
        if not context.is_enum_defined(mys_type):
            cpp_type = f'const {cpp_type}&'

    return cpp_type


def format_parameters(args, context):
    parameters = []

    for param, _ in args:
        cpp_type = mys_to_cpp_type_param(param.type, context)
        parameters.append(f'{cpp_type} {make_name(param.name)}')

    if parameters:
        return ', '.join(parameters)
    else:
        return 'void'


def format_return_type(returns, context):
    if returns is not None:
        return mys_to_cpp_type(returns, context)
    else:
        return 'void'


def format_method_name(method, class_name):
    if method.name == '__init__':
        return class_name
    elif method.name == '__del__':
        return f'~{class_name}'
    elif method.name in METHOD_OPERATORS:
        return 'operator' + METHOD_OPERATORS[method.name]
    else:
        return method.name


def format_default(name, param_name, return_cpp_type):
    return f'{return_cpp_type} {name}_{param_name}_default()'


def format_default_call(full_name, param_name):
    return f'{dot2ns(full_name)}_{param_name}_default()'


def is_public(name):
    return not is_private(name)


def is_private(name):
    return name.startswith('_')


def is_string(node, source_lines):
    line = source_lines[node.lineno - 1]

    return line[node.col_offset] != "'"


def has_docstring(node):
    """Retuns true if given function or method has a docstring.

    """

    docstring = ast.get_docstring(node)

    if docstring is not None:
        return not docstring.startswith('mys-embedded-c++')
    else:
        return False


class IntegerLiteralVisitor(ast.NodeVisitor):

    def visit_BinOp(self, node):
        return self.visit(node.left) and self.visit(node.right)

    def visit_UnaryOp(self, node):
        return self.visit(node.operand)

    def visit_Constant(self, node):
        if isinstance(node.value, bool):
            return False
        else:
            return isinstance(node.value, int)

    def generic_visit(self, node):
        return False


def is_integer_literal(node):
    return IntegerLiteralVisitor().visit(node)


def is_float_literal(node):
    if isinstance(node, ast.Constant):
        return isinstance(node.value, float)

    return False


class MakeIntegerLiteralVisitor(ast.NodeVisitor):

    def __init__(self, type_name):
        self.type_name = type_name
        self.factor = 1

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_class = type(node.op)

        return format_binop(left, right, op_class)

    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.USub):
            factor = -1
        else:
            factor = 1

        self.factor *= factor

        try:
            value = self.visit(node.operand)
        except CompileError as e:
            e.lineno = node.lineno
            e.offset = node.col_offset

            raise e

        self.factor *= factor

        return value

    def visit_Constant(self, node):
        value = node.value * self.factor

        if self.type_name == 'u8':
            if 0 <= value <= 0xff:
                return str(value)
        elif self.type_name == 'u16':
            if 0 <= value <= 0xffff:
                return str(value)
        elif self.type_name == 'u32':
            if 0 <= value <= 0xffffffff:
                return str(value)
        elif self.type_name == 'u64':
            if 0 <= value <= 0xffffffffffffffff:
                return f'u64({value}ull)'
        elif self.type_name == 'i8':
            if -0x80 <= value <= 0x7f:
                return str(value)
        elif self.type_name == 'i16':
            if -0x8000 <= value <= 0x7fff:
                return str(value)
        elif self.type_name == 'i32':
            if -0x80000000 <= value <= 0x7fffffff:
                return str(value)
        elif self.type_name == 'i64':
            if -0x7fffffffffffffff <= value <= 0x7fffffffffffffff:
                return str(value)
            if -0x8000000000000000 == value:
                # g++ warns for -0x8000000000000000.
                return '(-0x7fffffffffffffff - 1)'
        elif self.type_name is None:
            raise CompileError("integers cannot be None", node)

        else:
            mys_type = format_mys_type(self.type_name)

            raise CompileError(f"cannot convert integer to '{mys_type}'", node)

        raise CompileError(
            f"integer literal out of range for '{self.type_name}'",
            node)


def make_integer_literal(type_name, node):
    return MakeIntegerLiteralVisitor(type_name).visit(node)


def make_float_literal(type_name, node):
    if type_name == 'f32':
        return str(node.value)
    elif type_name == 'f64':
        return str(node.value)
    elif type_name is None:
        raise CompileError("floats cannot be None", node)
    else:
        mys_type = format_mys_type(type_name)

        raise CompileError(f"cannot convert float to '{mys_type}'", node)

    raise CompileError(f"float literal out of range for '{type_name}'", node)


def format_binop(left, right, op_class):
    if op_class == ast.Pow:
        return f'ipow({left}, {right})'
    else:
        op = OPERATORS[op_class]

        return f'({left} {op} {right})'


def format_mys_type(mys_type):
    if isinstance(mys_type, tuple):
        if len(mys_type) == 1:
            items = f'{format_mys_type(mys_type[0])}, '
        else:
            items = ', '.join([format_mys_type(item) for item in mys_type])

        return f'({items})'
    elif isinstance(mys_type, list):
        item = format_mys_type(mys_type[0])

        return f'[{item}]'
    elif isinstance(mys_type, dict):
        key_mys_type, value_mys_type = split_dict_mys_type(mys_type)
        key = format_mys_type(key_mys_type)
        value = format_mys_type(value_mys_type)

        return f'{{{key}: {value}}}'
    else:
        return str(mys_type)


def raise_types_differs(left_mys_type, right_mys_type, node):
    left = format_mys_type(left_mys_type)
    right = format_mys_type(right_mys_type)

    raise CompileError(f"types '{left}' and '{right}' differs", node)


def raise_if_types_differs(left_mys_type, right_mys_type, node):
    if left_mys_type != right_mys_type:
        raise_types_differs(left_mys_type, right_mys_type, node)


def indent_lines(lines):
    return ['    ' + line for line in lines if line]


def indent(string):
    return '\n'.join(indent_lines(string.splitlines()))


def dedent(string):
    return '\n'.join([line[4:] for line in string.splitlines() if line])
