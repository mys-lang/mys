import re

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

PRIMITIVE_TYPES = set([
    'i8',
    'i16',
    'i32',
    'i64',
    'u8',
    'u16',
    'u32',
    'u64',
    'f32',
    'f64',
    'bool',
    'char'
])

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

def split_dict_mys_type(mys_type):
    key_mys_type = list(mys_type.keys())[0]
    value_mys_type = list(mys_type.values())[0]

    return key_mys_type, value_mys_type
