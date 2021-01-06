import re
from .cpp_reserved import make_cpp_safe_name
from ..parser import ast


class CompileError(Exception):

    def __init__(self, message, node):
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


def has_docstring(node, source_lines):
    """Retuns true if given function or method has a docstring.

    """

    docstring = ast.get_docstring(node)

    if docstring is not None:
        return not docstring.startswith('mys-embedded-c++')
    else:
        return False
