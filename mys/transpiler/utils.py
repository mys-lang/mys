import re

from ..parser import ast
from .cpp_reserved import make_cpp_safe_name


class List:

    def __init__(self, value_type):
        self.value_type = value_type

    def __eq__(self, other):
        if not isinstance(other, List):
            return False

        return self.value_type == other.value_type

    def __str__(self):
        return f'List({self.value_type})'


class Set:

    def __init__(self, value_type):
        self.value_type = value_type

    def __eq__(self, other):
        if not isinstance(other, Set):
            return False

        return self.value_type == other.value_type

    def __str__(self):
        return f'Set({self.value_type})'


class Dict:

    def __init__(self, key_type, value_type):
        self.key_type = key_type
        self.value_type = value_type

    def __eq__(self, other):
        if not isinstance(other, Dict):
            return False

        if self.key_type != other.key_type:
            return False

        if self.value_type != other.value_type:
            return False

        return True

    def __str__(self):
        return f'Dict({self.key_type}, {self.value_type})'


class Tuple:

    def __init__(self, value_types):
        self.value_types = value_types

    def __len__(self):
        return len(self.value_types)

    def __getitem__(self, index):
        return self.value_types[index]

    def __eq__(self, other):
        if not isinstance(other, Tuple):
            return False

        return self.value_types == other.value_types

    def __str__(self):
        return f'Tuple({self.value_types})'


class GenericType:

    def __init__(self, name, types, node):
        self.name = name
        self.types = types
        self.node = node

    def __str__(self):
        return f'GenericType(name={self.name}, types={self.types})'


class Optional:

    def __init__(self, mys_type, node):
        self.mys_type = mys_type
        self.node = node

    def __eq__(self, other):
        return isinstance(other, Optional) and self.mys_type == other.mys_type

    def __str__(self):
        return f'Optional(mys_type={self.mys_type})'


class Weak:

    def __init__(self, mys_type, node):
        self.mys_type = mys_type
        self.node = node

    def __eq__(self, other):
        if isinstance(other, Weak):
            return self.mys_type == other.mys_type
        else:
            return self.mys_type == other


class CompileError(Exception):

    def __init__(self, message, node):
        super().__init__()
        self.message = message
        self.lineno = node.lineno
        self.offset = node.col_offset


class InternalError(CompileError):
    pass


class Function:

    def __init__(self, params=None, returns=None):
        if params is None:
            params = []

        self.params = params
        self.returns = returns


SNAKE_CASE_RE = re.compile(r'^(_*[a-z][a-z0-9_]*)$')
UPPER_SNAKE_CASE_RE = re.compile(r'^(_*[A-Z][A-Z0-9_]*)$')
PASCAL_CASE_RE = re.compile(r'^_?[A-Z][a-zA-Z0-9]*$')

INTEGER_TYPES = set(['i8', 'i16', 'i32', 'i64', 'u8', 'u16', 'u32', 'u64'])
NUMBER_TYPES = INTEGER_TYPES | set(['f32', 'f64'])
PRIMITIVE_TYPES = NUMBER_TYPES | set(['bool', 'char'])
BUILTIN_TYPES = PRIMITIVE_TYPES | set(['string', 'bytes'])

METHOD_BIN_OPERATORS = {
    '__add__',
    '__sub__',
    '__mul__',
    '__div__',
    '__eq__',
    '__ne__',
    '__gt__',
    '__ge__',
    '__lt__',
    '__le__'
}

METHOD_AUG_OPERATORS = {
    '__iadd__',
    '__isub__',
    '__imul__',
    '__idiv__'
}

METHOD_OPERATORS = METHOD_BIN_OPERATORS | METHOD_AUG_OPERATORS

METHOD_TO_OPERATOR = {
    '__add__': '+',
    '__sub__': '-',
    '__mul__': '*',
    '__div__': '/',
    '__eq__': '==',
    '__ne__': '!=',
    '__gt__': '>',
    '__ge__': '>=',
    '__lt__': '<',
    '__le__': '<=',
    '__iadd__': '+=',
    '__isub__': '-=',
    '__imul__': '*=',
    '__idiv__': '/='
}

BUILTIN_ERRORS = {
    'KeyError',
    'IndexError',
    'InterruptError',
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
        'bytes',
        'char',
        'list',
        'input',
        'set',
        'regex',
        'str',
        'min',
        'max',
        'abs',
        'f32',
        'f64',
        'enumerate',
        'range',
        'reversed',
        'slice',
        'sum',
        'zip',
        'string',
        'default',
        'any',
        'all',
        'hash',
        'copy',
        'deepcopy',
        '__MYS_TRACEBACK_ENTER',
        '__MYS_TRACEBACK_EXIT',
        '__MYS_TRACEBACK_SET'
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

COMPARISON_METHODS = {
    ast.Eq: '__eq__',
    ast.NotEq: '__ne__',
    ast.Lt: '__lt__',
    ast.LtE: '__le__',
    ast.Gt: '__gt__',
    ast.GtE: '__ge__'
}

OPERATORS_TO_METHOD = {
    ast.Add: '__add__',
    ast.Sub: '__sub__',
    ast.Mult: '__mul__',
    ast.Div: '__div__'
}

OPERATORS_TO_AUG_METHOD = {
    ast.Add: '__iadd__',
    ast.Sub: '__isub__',
    ast.Mult: '__imul__',
    ast.Div: '__idiv__'
}

SET_METHODS = {
    'is_disjoint': Function(['set'], 'bool'),
    'is_subset': Function(['set'], 'bool'),
    'is_proper_subset': Function(['set'], 'bool'),
    'is_superset': Function(['set'], 'bool'),
    'is_proper_superset': Function(['set'], 'bool'),
    'union': Function(['set'], 'set'),
    'update': Function(['set'], 'set'),
    'intersection': Function(['set'], 'set'),
    'intersection_update': Function(['set'], 'set'),
    'difference': Function(['set'], 'set'),
    'difference_update': Function(['set'], 'set'),
    'symmetric_difference': Function(['set'], 'set'),
    'symmetric_difference_update': Function(['set'], 'set'),
    'add': Function(['elem']),
    'clear': Function([]),
    'discard': Function(['elem']),
    'remove': Function(['elem']),
    'length': Function([], 'i64')
}

STRING_METHODS = {
    'to_utf8': Function([], 'bytes'),
    'starts_with': Function(['string'], 'bool'),
    'ends_with': Function(['string'], 'bool'),
    'join': Function([['string']], 'string'),
    'lower': Function([], 'string'),
    'upper': Function([], 'string'),
    'casefold': Function([], 'string'),
    'capitalize': Function([], 'string'),
    'split': Function(['string'], ['string']),
    'strip': Function(['string'], 'string'),
    'strip_left': Function(['string'], 'string'),
    'strip_right': Function(['string'], 'string'),
    'find': Function(['string|char', 'optional<i64>', 'optional<i64>'], 'i64'),
    'find_reverse': Function(['string|char', 'optional<i64>', 'optional<i64>'],
                             'i64'),
    'partition': Function(['string'], Tuple(['string', 'string', 'string'])),
    'replace': Function([None, None], 'string'),
    'is_alpha': Function([], 'bool'),
    'is_digit': Function([], 'bool'),
    'is_numeric': Function([], 'bool'),
    'is_space': Function([], 'bool'),
    'is_upper': Function([], 'bool'),
    'is_lower': Function([], 'bool'),
    'match': Function(['regex'], Optional('regexmatch', None)),
    'length': Function([], 'i64')
}

BYTES_METHODS = {
    'to_hex': Function([], 'string'),
    'find': Function(['string', 'optional<i64>', 'optional<i64>'], 'i64'),
    'reserve': Function(['i64']),
    'resize': Function(['i64']),
    'starts_with': Function(['bytes'], 'bool'),
    'ends_with': Function(['bytes'], 'bool'),
    'copy_into': Function(['bytes', 'i64', 'i64', 'i64']),
    'length': Function([], 'i64')
}

LIST_METHODS = {
    'append': Function(['<listtype>']),
    'extend': Function(['list<listtype>']),
    'insert': Function(['i64', '<listtype>']),
    'remove': Function(['<listtype>']),
    'reverse': Function(),
    'sort': Function(),
    'count': Function(['<listtype>'], 'i64'),
    'pop': Function(['i64'], '<listtype>'),
    'clear': Function(),
    'find': Function(['<listtype>'], 'i64'),
    'length': Function([], 'i64')
}

REGEX_METHODS = {
    'split': Function(['string'], ['string']),
    'match': Function(['string'], Optional('regexmatch', None)),
    'replace': Function(['string', 'string'], 'string')
}

REGEXMATCH_METHODS = {
    'span': Function([None], Tuple(['i64', 'i64'])),
    'begin': Function([None], 'i64'),
    'end': Function([None], 'i64'),
    'group': Function([None], Optional('string', None)),
    'groups': Function([None], ['string']),
    'group_dict': Function([], Dict('string', 'string'))
}

CHAR_METHODS = {
    'is_alpha': Function([], 'bool'),
    'is_digit': Function([], 'bool'),
    'is_numeric': Function([], 'bool'),
    'is_space': Function([], 'bool')
}

SPECIAL_SYMBOLS_TYPES = {
    '__unique_id__': 'i64',
    '__line__': 'u64',
    '__name__': 'string',
    '__file__': 'string',
    '__version__': 'string',
    '__assets__': 'string'
}

BUILTIN_CLASSES = {
    'set': SET_METHODS,
    'string': STRING_METHODS,
    'bytes': BYTES_METHODS,
    'list': LIST_METHODS,
    'regex': REGEX_METHODS,
    'regexmatch': REGEXMATCH_METHODS,
    'char': CHAR_METHODS
}


def get_builtin_method(class_name, method_name, node):
    spec = BUILTIN_CLASSES[class_name].get(method_name)

    if spec is None:
        raise CompileError(f"bad method '{method_name}' on builtin '{class_name}'",
                           node)

    return spec


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


def is_builtin_type(mys_type):
    if not isinstance(mys_type, str):
        return False

    return mys_type in BUILTIN_TYPES


def is_integer_type(mys_type):
    if not isinstance(mys_type, str):
        return False

    return mys_type in INTEGER_TYPES


def is_float_type(mys_type):
    if not isinstance(mys_type, str):
        return False

    return mys_type in ['f32', 'f64']


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
    return f'mys::make_shared<{cpp_type}>({values})'


def shared_list_type(cpp_type, is_weak=False):
    if is_weak:
        return f'mys::weak_ptr<mys::List<{cpp_type}>>'
    else:
        return f'mys::shared_ptr<mys::List<{cpp_type}>>'


def make_shared_list(cpp_type, value):
    return (f'mys::make_shared<mys::List<{cpp_type}>>('
            f'std::initializer_list<{cpp_type}>{{{value}}})')


def make_shared_set(cpp_type, value):
    return (f'mys::make_shared<Set<{cpp_type}>>('
            f'std::initializer_list<{cpp_type}>{{{value}}})')


def shared_dict_type(key_cpp_type, value_cpp_type, is_weak=False):
    if is_weak:
        return f'mys::weak_ptr<mys::Dict<{key_cpp_type}, {value_cpp_type}>>'
    else:
        return f'mys::shared_ptr<mys::Dict<{key_cpp_type}, {value_cpp_type}>>'


def make_shared_dict(key_cpp_type, value_cpp_type, items):
    return (f'mys::make_shared<Dict<{key_cpp_type}, {value_cpp_type}>>('
            f'std::initializer_list<std::pair<{key_cpp_type}, '
            f'{value_cpp_type}>>{{{items}}})')


def shared_set_type(cpp_type, is_weak=False):
    if is_weak:
        return f'mys::weak_ptr<mys::Set<{cpp_type}>>'
    else:
        return f'mys::shared_ptr<mys::Set<{cpp_type}>>'


def shared_tuple_type(items, is_weak=False):
    if is_weak:
        return f'mys::weak_ptr<mys::Tuple<{items}>>'
    else:
        return f'mys::shared_ptr<mys::Tuple<{items}>>'


def mys_to_cpp_type(mys_type, context):
    if isinstance(mys_type, Weak):
        is_weak = True
        mys_type = mys_type.mys_type
    else:
        is_weak = False

    is_optional, mys_type = strip_optional_with_result(mys_type)

    if isinstance(mys_type, Tuple):
        items = ', '.join([mys_to_cpp_type(item, context) for item in mys_type])

        return shared_tuple_type(items, is_weak)
    elif isinstance(mys_type, list):
        item = mys_to_cpp_type(mys_type[0], context)

        return shared_list_type(item, is_weak)
    elif isinstance(mys_type, Dict):
        key = mys_to_cpp_type(mys_type.key_type, context)
        value = mys_to_cpp_type(mys_type.value_type, context)

        return shared_dict_type(key, value, is_weak)
    elif isinstance(mys_type, Set):
        item = mys_to_cpp_type(mys_type.value_type, context)

        return shared_set_type(item, is_weak)
    else:
        if mys_type == 'string':
            return 'mys::String'
        elif mys_type == 'bool':
            return 'mys::Bool'
        elif mys_type == 'char':
            return 'mys::Char'
        elif mys_type == 'bytes':
            return 'mys::Bytes'
        elif mys_type == 'regex':
            return 'mys::Regex'
        elif mys_type == 'regexmatch':
            return 'mys::RegexMatch'
        elif context.is_class_or_trait_defined(mys_type):
            if is_weak:
                return f'mys::weak_ptr<{dot2ns(mys_type)}>'
            else:
                return f'mys::shared_ptr<{dot2ns(mys_type)}>'
        elif context.is_enum_defined(mys_type):
            return context.get_enum_type(mys_type)
        elif is_primitive_type(mys_type):
            if is_optional:
                return f'mys::optional<{mys_type}>'
            else:
                return mys_type
        else:
            return mys_type


def mys_to_cpp_type_param(mys_type, context):
    cpp_type = mys_to_cpp_type(mys_type, context)

    if not is_primitive_type(mys_type):
        if not context.is_enum_defined(mys_type) and mys_type != 'string':
            cpp_type = f'{cpp_type}'

    return cpp_type


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
    else:
        return make_name(method.name)


def format_default(name, param_name, return_cpp_type):
    return f'{return_cpp_type} {name}_{param_name}_default()'


def format_default_call(full_name, param_name):
    return f'{dot2ns(full_name)}_{param_name}_default()'


def is_public(name):
    return not is_private(name)


def is_private(name):
    return name.startswith('_')


def has_docstring(node):
    """Retuns true if given function or method has a docstring.

    """

    return ast.get_docstring(node) is not None


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


class FloatLiteralVisitor(IntegerLiteralVisitor):

    def visit_Constant(self, node):
        return isinstance(node.value, float)


def is_float_literal(node):
    return FloatLiteralVisitor().visit(node)


class MakeIntegerLiteralVisitor(ast.NodeVisitor):

    def __init__(self, type_name):
        self.type_name = type_name
        self.factor = 1

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_class = type(node.op)

        return format_binop(left, right, op_class, True)

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

        if not isinstance(node.op, (ast.UAdd, ast.USub)):
            op = OPERATORS[type(node.op)]
            value = f'{op}{value}'

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
        elif isinstance(self.type_name, Optional):
            type_name = self.type_name
            self.type_name = type_name.mys_type
            value = self.visit_Constant(node)
            self.type_name = type_name

            return value
        else:
            mys_type = format_mys_type(self.type_name)

            raise CompileError(f"cannot convert integer to '{mys_type}'", node)

        raise CompileError(
            f"integer literal out of range for '{self.type_name}'",
            node)


def make_integer_literal(type_name, node):
    return MakeIntegerLiteralVisitor(type_name).visit(node)


class MakeFloatLiteralVisitor(MakeIntegerLiteralVisitor):

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_class = type(node.op)

        return format_binop(left, right, op_class, False)

    def visit_Constant(self, node):
        value = node.value * self.factor

        if self.type_name == 'f32':
            return str(value)
        elif self.type_name == 'f64':
            return str(value)
        elif self.type_name is None:
            raise CompileError("float cannot be None", node)
        else:
            mys_type = format_mys_type(self.type_name)

            raise CompileError(f"cannot convert float to '{mys_type}'", node)

        raise CompileError(
            f"float literal out of range for '{self.type_name}'",
            node)


def make_float_literal(type_name, node):
    return MakeFloatLiteralVisitor(type_name).visit(node)


def format_binop(left, right, op_class, is_integer=True):
    if op_class == ast.Pow:
        if is_integer:
            return f'ipow({left}, {right})'
        else:
            return f'std::pow({left}, {right})'
    elif op_class in [ast.Mod, ast.Div]:
        op = OPERATORS[op_class]

        return f'({left} {op} mys::denominator_not_zero({right}))'
    else:
        op = OPERATORS[op_class]

        return f'({left} {op} {right})'


def format_mys_type(mys_type):
    if isinstance(mys_type, Tuple):
        if len(mys_type) == 1:
            items = f'{format_mys_type(mys_type[0])}, '
        else:
            items = ', '.join([format_mys_type(item) for item in mys_type])

        return f'({items})'
    elif isinstance(mys_type, list):
        item = format_mys_type(mys_type[0])

        return f'[{item}]'
    elif isinstance(mys_type, Dict):
        key = format_mys_type(mys_type.key_type)
        value = format_mys_type(mys_type.value_type)

        return f'{{{key}: {value}}}'
    elif isinstance(mys_type, set):
        item = format_mys_type(list(mys_type)[0])
        return f'{{{item}}}'
    elif isinstance(mys_type, GenericType):
        types = ', '.join(format_mys_type(type) for type in mys_type.types)

        return f'{mys_type.name}[{types}]'
    elif isinstance(mys_type, Optional):
        return f'{format_mys_type(mys_type.mys_type)}?'
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


def make_types_string_parts(mys_types):
    """Makes given list of mys types a new list with separators inserted
    for unique function names.

    """

    parts = []

    for mys_type in mys_types:
        if isinstance(mys_type, str):
            parts.append(mys_type.replace('.', '_'))
        elif isinstance(mys_type, Tuple):
            parts.append('tb')
            parts += make_types_string_parts(mys_type)
            parts.append('te')
        elif isinstance(mys_type, list):
            parts.append('lb')
            parts += make_types_string_parts(mys_type)
            parts.append('le')
        elif isinstance(mys_type, Dict):
            parts.append('db')
            parts += make_types_string_parts([mys_type.key_type])
            parts.append('cn')
            parts += make_types_string_parts([mys_type.value_type])
            parts.append('de')
        else:
            raise Exception(str(mys_type))

    return parts


def make_function_name(name, param_types, returns):
    """Create a function name from given name, parameters and return type.

    """

    parts = [name]
    parts += make_types_string_parts(param_types)

    if returns is not None:
        parts.append('r')
        parts += make_types_string_parts([returns])

    return '_'.join(parts)


def raise_wrong_types(actual_mys_type, expected_mys_type, node):
    actual = format_mys_type(actual_mys_type)
    expected = format_mys_type(expected_mys_type)

    raise CompileError(f"expected a '{expected}', got a '{actual}'", node)


def raise_if_wrong_types(actual_mys_type, expected_mys_type, node):
    if isinstance(expected_mys_type, Optional):
        if actual_mys_type is None:
            return

        expected_mys_type = expected_mys_type.mys_type

    actual_mys_type = strip_optional(actual_mys_type)

    if actual_mys_type == expected_mys_type:
        return

    raise_wrong_types(actual_mys_type, expected_mys_type, node)


def raise_if_wrong_visited_type(context, expected_mys_type, node):
    raise_if_wrong_types(context.mys_type, expected_mys_type, node)


def strip_optional(mys_type):
    if isinstance(mys_type, Optional):
        mys_type = mys_type.mys_type

    return mys_type


def strip_optional_with_result(mys_type):
    if isinstance(mys_type, Optional):
        is_optional = True
        mys_type = mys_type.mys_type
    else:
        is_optional = False

    return is_optional, mys_type


def is_c_string(node):
    return isinstance(node, tuple) and len(node) == 1


def is_regex(node):
    return isinstance(node, tuple) and len(node) == 2


def is_char(node):
    return isinstance(node, tuple) and len(node) == 3


def split_full_name(mys_type):
    module, _, name = mys_type.rpartition('.')

    return module, name
