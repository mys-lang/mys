import re
import textwrap
from ..parser import ast

class LanguageError(Exception):

    def __init__(self, message, lineno, offset):
        self.message = message
        self.lineno = lineno
        self.offset = offset

SNAKE_CASE_RE = re.compile(r'^(_*[a-z][a-z0-9_]*)$')
UPPER_SNAKE_CASE_RE = re.compile(r'^(_*[A-Z][A-Z0-9_]*)$')
PASCAL_CASE_RE = re.compile(r'^_?[A-Z][a-zA-Z0-9]*$')

BOOL_OPS = {
    ast.And: '&&',
    ast.Or: '||'
}

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

INTEGER_TYPES = set(['i8', 'i16', 'i32', 'i64', 'u8', 'u16', 'u32', 'u64'])

def raise_types_differs(left_mys_type, right_mys_type, node):
    left = format_mys_type(left_mys_type)
    right = format_mys_type(right_mys_type)

    raise LanguageError(f"types '{left}' and '{right}' differs",
                        node.lineno,
                        node.col_offset)

def is_snake_case(value):
    return SNAKE_CASE_RE.match(value) is not None

def is_upper_snake_case(value):
    return UPPER_SNAKE_CASE_RE.match(value) is not None

def is_pascal_case(value):
    return PASCAL_CASE_RE.match(value)

def mys_to_cpp_type(mys_type):
    if isinstance(mys_type, tuple):
        items = ', '.join([mys_to_cpp_type(item) for item in mys_type])

        return f'Tuple<{items}>'
    elif isinstance(mys_type, list):
        item = mys_to_cpp_type(mys_type[0])

        return f'std::shared_ptr<List<{item}>>'
    elif isinstance(mys_type, dict):
        key = mys_to_cpp_type(list(mys_type.keys())[0])
        value = mys_to_cpp_type(list(mys_type.values())[0])

        return f'std::shared_ptr<Dict<{key}, {value}>>'
    else:
        if mys_type == 'string':
            return 'String'
        else:
            return mys_type

def format_mys_type(mys_type):
    if isinstance(mys_type, tuple):
        items = ', '.join([format_mys_type(item) for item in mys_type])

        return f'({items})'
    elif isinstance(mys_type, list):
        item = format_mys_type(mys_type[0])

        return f'[{item}]'
    elif isinstance(mys_type, dict):
        key = format_mys_type(list(mys_type.keys())[0])
        value = format_mys_type(list(mys_type.values())[0])

        return f'{{{key}: {value}}}'
    else:
        return mys_type

class TypeVisitor(ast.NodeVisitor):

    def visit_Name(self, node):
        return node.id

    def visit_List(self, node):
        return [self.visit(elem) for elem in node.elts]

    def visit_Tuple(self, node):
        return tuple([self.visit(elem) for elem in node.elts])

    def visit_Dict(self, node):
        return {node.keys[0].id: self.visit(node.values[0])}

class UnpackVisitor(ast.NodeVisitor):

    def visit_Name(self, node):
        return (node.id, node)

    def visit_Tuple(self, node):
        return (tuple([self.visit(elem) for elem in node.elts]), node)

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

        if op_class == ast.Pow:
            return f'ipow({left}, {right})'
        else:
            op = OPERATORS[op_class]

            return f'({left} {op} {right})'

    def visit_UnaryOp(self, node):
        if isinstance(node.op, ast.USub):
            factor = -1
        else:
            factor = 1

        self.factor *= factor

        try:
            value = self.visit(node.operand)
        except LanguageError as e:
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
                return f'{value}ull'
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
            if -0x8000000000000000 <= value <= 0x7fffffffffffffff:
                return str(value)
        else:
            mys_type = format_mys_type(self.type_name)

            raise LanguageError(f"can't convert integer to '{mys_type}'",
                                node.lineno,
                                node.col_offset)

        raise LanguageError(
            f"integer literal out of range for '{self.type_name}'",
            node.lineno,
            node.col_offset)

def make_integer_literal(type_name, node):
    return MakeIntegerLiteralVisitor(type_name).visit(node)

def make_float_literal(type_name, node):
    if type_name == 'f32':
        return str(node.value)
    elif type_name == 'f64':
        return str(node.value)
    else:
        mys_type = format_mys_type(type_name)

        raise LanguageError(f"can't convert float to '{mys_type}'",
                            node.lineno,
                            node.col_offset)

    raise LanguageError(
        f"float literal out of range for '{type_name}'",
        node.lineno,
        node.col_offset)

BUILTIN_CALLS = set(
    list(INTEGER_TYPES) + [
        'print',
        'range',
        'assert_eq',
        'assert_ne',
        'assert_gt',
        'assert_lt',
        'assert_ge',
        'assert_le',
        'assert_true',
        'assert_false',
        'assert_in',
        'assert_not_in',
        'TypeError',
        'ValueError',
        'GeneralError',
        'str',
        'min',
        'max',
        'len',
        'abs',
        'f32',
        'f64'
    ])

class Range:

    def __init__(self, target, begin, end, step, mys_type):
        self.target = target
        self.begin = begin
        self.end = end
        self.step = step
        self.mys_type = mys_type

class Enumerate:

    def __init__(self, target, initial, mys_type):
        self.target = target
        self.initial = initial
        self.mys_type = mys_type

class Slice:

    def __init__(self, begin, end, step):
        self.begin = begin
        self.end = end
        self.step = step

class OpenSlice:

    def __init__(self, begin):
        self.begin = begin

class Reversed:

    pass

class Zip:

    def __init__(self, children):
        self.children = children

class Data:

    def __init__(self, target, value, mys_type):
        self.target = target
        self.value = value
        self.mys_type = mys_type

class Context:

    def __init__(self):
        self._stack = [[]]
        self._variables = {}
        self._classes = {}
        self._traits = {}
        self._functions = {}
        self._enums = {}
        self.return_mys_type = None
        self.mys_type = None
        self.unique_count = 0

    def unique(self, name):
        self.unique_count += 1

        return f'{name}_{self.unique_count}'

    def define_variable(self, name, info, node):
        if self.is_variable_defined(name):
            raise LanguageError(f"redefining variable '{name}'",
                                node.lineno,
                                node.col_offset)

        if not is_snake_case(name):
            raise LanguageError("local variable names must be snake case",
                                node.lineno,
                                node.col_offset)

        self._variables[name] = info
        self._stack[-1].append(name)

    def define_global_variable(self, name, info, node):
        if self.is_variable_defined(name):
            raise LanguageError(f"redefining variable '{name}'",
                                node.lineno,
                                node.col_offset)

        self._variables[name] = info
        self._stack[-1].append(name)

    def is_variable_defined(self, name):
        return name in self._variables

    def get_variable_type(self, name):
        return self._variables[name]

    def define_class(self, name):
        self._classes[name] = None

    def is_class_defined(self, name):
        return name in self._classes

    def define_trait(self, name):
        self._traits[name] = None

    def is_trait_defined(self, name):
        return name in self._traits

    def define_function(self, name, definitions):
        self._functions[name] = definitions

    def is_function_defined(self, name):
        return name in self._functions

    def get_functions(self, name):
        return self._functions[name]

    def define_enum(self, name, type_):
        self._enums[name] = type_

    def is_enum_defined(self, name):
        return name in self._enums

    def get_enum_type(self, name):
        return self._enums[name]

    def push(self):
        self._stack.append([])

    def pop(self):
        for name in self._stack[-1]:
            self._variables.pop(name)

        self._stack.pop()

def make_relative_import_absolute(module_levels, module, node):
    prefix = '.'.join(module_levels[0:-node.level])

    if not prefix:
        raise LanguageError('relative import is outside package',
                            node.lineno,
                            node.col_offset)

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
        raise LanguageError(f'only one import is allowed, found {len(node.names)}',
                            node.lineno,
                            node.col_offset)

    name = node.names[0]

    if name.asname:
        asname = name.asname
    else:
        asname = name.name

    return module, name, asname

def return_type_string(node, source_lines, context, filename):
    if node is None:
        return 'void'
    else:
        return CppTypeVisitor(source_lines, context, filename).visit(node)

def params_string(function_name,
                  args,
                  source_lines,
                  context,
                  defaults=None,
                  filename=''):
    if defaults is None:
        defaults = []

    params = [
        ParamVisitor(source_lines, context, filename).visit(arg)
        for arg in args
    ]

    defaults = [
        BaseVisitor(source_lines, context, filename).visit(default)
        for default in defaults
    ]

    params_with_defaults = params[:len(params) - len(defaults)]

    for param, default in zip(params[-len(defaults):], defaults):
        params_with_defaults.append(f'{param} = {default}')

    params = ', '.join(params_with_defaults)

    if not params:
        params = 'void'

    return params

def indent(string):
    return '\n'.join(['    ' + line for line in string.splitlines() if line])

def dedent(string):
    return '\n'.join([line[4:] for line in string.splitlines() if line])

def handle_string(value):
    if value.startswith('mys-embedded-c++'):
        return '\n'.join([
            '/* mys-embedded-c++ start */\n',
            textwrap.dedent(value[16:]).strip(),
            '\n/* mys-embedded-c++ stop */'])
    else:
        value = value.encode("unicode_escape").decode('utf-8')

        return f'"{value}"'

def is_string(node, source_lines):
    line = source_lines[node.lineno - 1]

    return line[node.col_offset] != "'"

def handle_string_node(node, value, source_lines):
    if is_string(node, source_lines):
        return handle_string(value)
    else:
        raise LanguageError('character literals are not yet supported',
                            node.lineno,
                            node.col_offset)

def find_item_with_length(items):
    for item in items:
        if isinstance(item, (Slice, OpenSlice, Reversed)):
            pass
        elif isinstance(item, Zip):
            return find_item_with_length(item.children[0])
        else:
            return item

class BaseVisitor(ast.NodeVisitor):

    def __init__(self, source_lines, context, filename):
        self.source_lines = source_lines
        self.context = context
        self.filename = filename

    def unique(self, name):
        return self.context.unique(name)

    def return_type_string(self, node):
        return return_type_string(node,
                                  self.source_lines,
                                  self.context,
                                  self.filename)

    def visit_Name(self, node):
        if self.context.is_variable_defined(node.id):
            self.context.mys_type = self.context.get_variable_type(node.id)

        return node.id

    def find_print_kwargs(self, node):
        end = ' << std::endl'
        flush = None

        for keyword in node.keywords:
            if keyword.arg == 'end':
                value = self.visit(keyword.value)
                end = f' << {value}'
            elif keyword.arg == 'flush':
                flush = self.visit(keyword.value)
            else:
                raise LanguageError(
                    f"invalid keyword argument '{keyword.arg}' to print(), only "
                    "'end' and 'flush' are allowed",
                    node.lineno,
                    node.col_offset)

        return end, flush

    def handle_print(self, node, args):
        end, flush = self.find_print_kwargs(node)
        code = 'std::cout'

        if len(args) == 1:
            code += f' << {args[0]}'
        elif len(args) != 0:
            first = args[0]
            args = ' << " " << '.join(args[1:])
            code += f' << {first} << " " << {args}'

        code += end

        if flush:
            code += ';\n'
            code += f'if ({flush}) {{\n'
            code += f'    std::cout << std::flush;\n'
            code += '}'

        self.context.mys_type = None

        return code

    def is_class_or_trait_defined(self, type_string):
        if self.context.is_class_defined(type_string):
            return True

        if self.context.is_trait_defined(type_string):
            return True

        return False

    def visit_Call(self, node):
        mys_type = None

        if isinstance(node.func, ast.Name):
            if self.context.is_function_defined(node.func.id):
                functions = self.context.get_functions(node.func.id)

                if len(functions) != 1:
                    raise LanguageError("overloaded functions are not yet supported",
                                        node.func.lineno,
                                        node.func.col_offset)

                function = functions[0]

                if len(node.args) != len(function.args):
                    raise LanguageError("wrong number of parameters",
                                        node.func.lineno,
                                        node.func.col_offset)

                mys_type = function.returns
                # print(function.name, function.args, function.returns, len(node.args))
            elif self.context.is_class_defined(node.func.id):
                # print('Class:', node.func.id)
                pass
            elif node.func.id in BUILTIN_CALLS:
                # print('Builtin:', node.func.id)
                pass
            else:
                # print(f"can't call {node.func.id}")
                # print(ast.dump(node))
                pass
        elif isinstance(node.func, ast.Attribute):
            # print('Meth:',
            #       self.visit(node.func.value),
            #       self.context.mys_type,
            #       node.func.attr)
            pass
        elif isinstance(node.func, ast.Lambda):
            raise LanguageError('lambda functions are not supported',
                                node.func.lineno,
                                node.func.col_offset)
        else:
            raise LanguageError("not callable",
                                node.func.lineno,
                                node.func.col_offset)

        function_name = self.visit(node.func)
        args = []

        for arg in node.args:
            if isinstance(arg, ast.Name):
                if not self.context.is_variable_defined(arg.id):
                    raise LanguageError(
                        f"undefined variable '{arg.id}'",
                        arg.lineno,
                        arg.col_offset)

            if is_integer_literal(arg):
                args.append(make_integer_literal('i64', arg))
            else:
                args.append(self.visit(arg))

        if isinstance(node.func, ast.Name):
            if self.context.is_class_defined(node.func.id):
                args = ', '.join(args)
                self.context.mys_type = node.func.id

                return f'std::make_shared<{node.func.id}>({args})'

        if function_name == 'print':
            code = self.handle_print(node, args)
        else:
            if function_name in INTEGER_TYPES:
                mys_type = function_name
            elif function_name == 'str':
                mys_type = 'string'
            elif function_name in ['f32', 'f64']:
                mys_type = function_name

            args = ', '.join(args)
            code = f'{function_name}({args})'

        self.context.mys_type = mys_type

        return code

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            self.context.mys_type = 'string'

            return handle_string_node(node, node.value, self.source_lines)
        elif isinstance(node.value, bool):
            self.context.mys_type = 'bool'

            return 'true' if node.value else 'false'
        elif isinstance(node.value, float):
            self.context.mys_type = 'f64'

            return f'{node.value}'
        elif isinstance(node.value, int):
            self.context.mys_type = 'i64'

            return str(node.value)
        else:
            raise LanguageError("internal error",
                                node.lineno,
                                node.col_offset)

    def visit_Expr(self, node):
        return self.visit(node.value) + ';'

    def visit_binop_one_literal(self, other_node, literal_node):
        other = self.visit(other_node)
        other_type = self.context.mys_type

        if isinstance(other_node, ast.Name):
            if not self.context.is_variable_defined(other_node.id):
                raise LanguageError(
                    f"undefined variable '{other_node.id}'",
                    other_node.lineno,
                    other_node.col_offset)

        if self.context.mys_type in INTEGER_TYPES:
            literal_type = self.context.mys_type
            literal = make_integer_literal(literal_type, literal_node)
        else:
            literal = self.visit(literal_node)
            literal_type = self.context.mys_type

        return other, other_type, literal, literal_type

    def visit_BinOp(self, node):
        is_left_literal = is_integer_literal(node.left)
        is_right_literal = is_integer_literal(node.right)
        op_class = type(node.op)

        if is_left_literal and not is_right_literal:
            right, right_type, left, left_type = self.visit_binop_one_literal(
                node.right,
                node.left)
        elif not is_left_literal and is_right_literal:
            left, left_type, right, right_type = self.visit_binop_one_literal(
                node.left,
                node.right)
        else:
            left = self.visit(node.left)
            left_type = self.context.mys_type
            right = self.visit(node.right)
            right_type = self.context.mys_type

        if isinstance(node.left, ast.Name):
            if not self.context.is_variable_defined(node.left.id):
                raise LanguageError(
                    f"undefined variable '{node.left.id}'",
                    node.left.lineno,
                    node.left.col_offset)

        if isinstance(node.right, ast.Name):
            if not self.context.is_variable_defined(node.right.id):
                raise LanguageError(
                    f"undefined variable '{node.right.id}'",
                    node.right.lineno,
                    node.right.col_offset)

        if left_type != right_type:
            raise_types_differs(left_type, right_type, node)

        if op_class == ast.Pow:
            return f'ipow({left}, {right})'
        else:
            op = OPERATORS[op_class]

            return f'({left} {op} {right})'

    def visit_UnaryOp(self, node):
        op = OPERATORS[type(node.op)]
        operand = self.visit(node.operand)

        return f'{op}({operand})'

    def visit_AugAssign(self, node):
        lval = self.visit(node.target)
        op = OPERATORS[type(node.op)]
        rval = self.visit(node.value)

        return f'{lval} {op}= {rval};'

    def visit_Tuple(self, node):
        items = []
        mys_types = []

        for item in node.elts:
            items.append(self.visit(item))
            mys_types.append(self.context.mys_type)

        self.context.mys_type = tuple(mys_types)
        cpp_type = mys_to_cpp_type(self.context.mys_type)

        return f'{cpp_type}({{{", ".join(items)}}})'

    def visit_List(self, node):
        items = []
        item_mys_type = None

        for item in node.elts:
            items.append(self.visit(item))

            if item_mys_type is None:
                item_mys_type = self.context.mys_type

        if item_mys_type is None:
            self.context.mys_type = None
        else:
            self.context.mys_type = [item_mys_type]

        value = ", ".join(items)
        item_cpp_type = mys_to_cpp_type(item_mys_type)

        return (f'std::make_shared<List<{item_cpp_type}>>('
                f'std::initializer_list<{item_cpp_type}>{{{value}}})')

    def visit_Dict(self, node):
        key = self.visit(node.keys[0])
        key_type = self.context.mys_type
        value_type = None

        for value in node.values:
            value = self.visit(value)

            if value_type is None:
                value_type = self.context.mys_type

        self.context.mys_type = {key_type: value_type}

        return 'std::make_shared<Dict<todo>>({})'

    def visit_for_list(self, node, value, mys_type):
        item_mys_type = mys_type[0]
        items = self.unique('items')
        i = self.unique('i')

        if isinstance(node.target, ast.Tuple):
            target = []

            for j, item in enumerate(node.target.elts):
                name = item.id

                if not name.startswith('_'):
                    self.context.define_variable(name, item_mys_type[j], item)
                    target.append(
                        f'    auto {name} = std::get<{j}>(*{items}->get({i}));')

            target = '\n'.join(target)
        else:
            name = node.target.id

            if not name.startswith('_'):
                self.context.define_variable(name, item_mys_type, node.target)

            target = f'    auto {name} = {items}->get({i});'

        body = indent('\n'.join([
            self.visit(item)
            for item in node.body
        ]))

        return '\n'.join([
            f'auto {items} = {value};',
            f'for (auto {i} = 0; {i} < {items}->__len__(); {i}++) {{',
            target,
            body,
            '}'
        ])

    def visit_range_parameter(self, node, expected_mys_type=None):
        value = self.visit(node)
        mys_type = self.context.mys_type

        if mys_type not in INTEGER_TYPES:
            mys_type = format_mys_type(mys_type)

            raise LanguageError(
                f"range() parameter type must be an integer, not '{mys_type}'",
                node.lineno,
                node.col_offset)

        if expected_mys_type is not None and mys_type != expected_mys_type:
            raise_types_differs(mys_type, expected_mys_type, node)

        return value, mys_type

    def visit_for_call_range(self, items, target_value, iter_node, nargs):
        if nargs == 1:
            begin = 0
            end, mys_type = self.visit_range_parameter(iter_node.args[0])
            step = 1
        elif nargs == 2:
            begin, mys_type = self.visit_range_parameter(iter_node.args[0])
            end, _ = self.visit_range_parameter(iter_node.args[1], mys_type)
            step = 1
        elif nargs == 3:
            begin, mys_type = self.visit_range_parameter(iter_node.args[0])
            end, _ = self.visit_range_parameter(iter_node.args[1])
            step, _ = self.visit_range_parameter(iter_node.args[2], mys_type)
        else:
            raise LanguageError(
                f"range() takes one to three parameters, {nargs} given",
                iter_node.lineno,
                iter_node.col_offset)

        items.append(Range(target_value, begin, end, step, mys_type))

    def visit_enumerate_parameter(self, node):
        value = self.visit(node)
        mys_type = self.context.mys_type

        if mys_type not in INTEGER_TYPES:
            raise LanguageError(
                f"enumerate() initial value must be an integer, not '{mys_type}'",
                node.lineno,
                node.col_offset)

        return value, mys_type

    def visit_for_call_enumerate(self,
                                 items,
                                 target_value,
                                 target_node,
                                 iter_node,
                                 nargs):
        if len(target_value) != 2:
            raise LanguageError(
                "can only unpack enumerate into two variables",
                target_node.lineno,
                target_node.col_offset)


        if nargs == 1:
            self.visit_for_call(items,
                                target_value[1],
                                iter_node.args[0]),
            items.append(Enumerate(target_value[0][0], 0, None))
        elif nargs == 2:
            self.visit_for_call(items,
                                target_value[1],
                                iter_node.args[0]),
            initial, mys_type = self.visit_enumerate_parameter(
                iter_node.args[1])
            items.append(Enumerate(target_value[0][0], initial, mys_type))
        else:
            raise LanguageError(
                f"enumerate() takes one or two parameters, {nargs} given",
                iter_node.lineno,
                iter_node.col_offset)

    def visit_for_call_slice(self, items, target, iter_node, nargs):
        self.visit_for_call(items, target, iter_node.args[0]),

        if nargs == 2:
            items.append(OpenSlice(self.visit(iter_node.args[1])))
        elif nargs == 3:
            items.append(Slice(self.visit(iter_node.args[1]),
                               self.visit(iter_node.args[2]),
                               1))
        elif nargs == 4:
            items.append(Slice(self.visit(iter_node.args[1]),
                               self.visit(iter_node.args[2]),
                               self.visit(iter_node.args[3])))
        else:
            raise LanguageError(
                f"slice() takes two to four parameters, {nargs} given",
                iter_node.lineno,
                iter_node.col_offset)

    def visit_for_call_zip(self, items, target_value, target_node, iter_node, nargs):
        if len(target_value) != nargs:
            raise LanguageError(
                f"can't unpack {len(iter_node.args)} values into "
                f"{len(target_value)}",
                target_node.lineno,
                target_node.col_offset)

        children = []

        for value, arg in zip(target_value, iter_node.args):
            items_2 = []
            self.visit_for_call(items_2, value, arg)
            children.append(items_2)

        items.append(Zip(children))

    def visit_for_call_reversed(self, items, target, iter_node, nargs):
        if nargs == 1:
            self.visit_for_call(items, target, iter_node.args[0]),
            items.append(Reversed())
        else:
            raise LanguageError(
                f"reversed() takes one parameter, {nargs} given",
                iter_node.lineno,
                iter_node.col_offset)

    def visit_for_call_data(self, items, target_value, iter_node):
        items.append(Data(target_value,
                          self.visit(iter_node),
                          self.context.mys_type[0]))

    def visit_for_call(self, items, target, iter_node):
        target_value, target_node = target

        if isinstance(iter_node, ast.Call):
            function_name = iter_node.func.id
            nargs = len(iter_node.args)

            if function_name == 'range':
                self.visit_for_call_range(items, target_value, iter_node, nargs)
            elif function_name == 'slice':
                self.visit_for_call_slice(items, target, iter_node, nargs)
            elif function_name == 'enumerate':
                self.visit_for_call_enumerate(items,
                                              target_value,
                                              target_node,
                                              iter_node,
                                              nargs)
            elif function_name == 'zip':
                self.visit_for_call_zip(items,
                                        target_value,
                                        target_node,
                                        iter_node,
                                        nargs)
            elif function_name == 'reversed':
                self.visit_for_call_reversed(items, target, iter_node, nargs)
        else:
            self.visit_for_call_data(items, target_value, iter_node)

    def visit_for_items_init(self, items):
        code = ''

        for i, item in enumerate(items):
            if isinstance(item, Data):
                name = self.unique('data')
                code += f'auto {name}_object = {item.value};\n'
                code += f'auto {name} = Data({name}_object->__len__());\n'
            elif isinstance(item, Enumerate):
                name = self.unique('enumerate')
                prev_name = find_item_with_length(items).name
                code += (f'auto {name} = Enumerate(i64({item.initial}),'
                         f' i64({prev_name}.length()));\n')
            elif isinstance(item, Range):
                name = self.unique('range')
                code += (f'auto {name} = Range(i64({item.begin}), i64({item.end}), '
                         f'i64({item.step}));\n')
            elif isinstance(item, Slice):
                name = self.unique('slice')
                code += (f'auto {name} = Slice(i64({item.begin}), i64({item.end}),'
                         f' i64({item.step}), i64({items[0].name}.length()));\n')

                for item_2 in items[:i]:
                    if not isinstance(item_2, (Slice, OpenSlice)):
                        code += f'{item_2.name}.slice({name});\n'
            elif isinstance(item, OpenSlice):
                name = self.unique('slice')
                code += (f'auto {name} = OpenSlice(i64({item.begin}));\n')

                for item_2 in items[:i]:
                    if not isinstance(item_2, (Slice, OpenSlice, Zip, Reversed)):
                        code += f'{item_2.name}.slice({name});\n'
            elif isinstance(item, Reversed):
                for item_2 in items[:i]:
                    if not isinstance(item_2, (Slice, OpenSlice)):
                        code += f'{item_2.name}.reversed();\n'
            elif isinstance(item, Zip):
                names = []

                for items_2 in item.children:
                    code += self.visit_for_items_init(items_2)
                    names.append(find_item_with_length(items_2).name)

                first_child_name = names[0]
                name = self.unique('zip')
                code += f'auto {name} = {first_child_name}.length();\n'

                for child_name in names[1:]:
                    code += f'if ({name} != {child_name}.length()) {{\n'
                    code += f'    throw ValueError("can\'t zip different lengths");\n'
                    code += '}\n'
            else:
                raise RuntimeError()

            item.name = name

        return code

    def visit_for_items_iter(self, items):
        code = ''

        for item in items:
            if isinstance(item, (Slice, OpenSlice, Reversed)):
                pass
            elif isinstance(item, Zip):
                for items_2 in item.children:
                    code += self.visit_for_items_iter(items_2)
            else:
                code += f'{item.name}.iter();\n'

        return code

    def visit_for_items_len_item(self, items):
        for item in items:
            if isinstance(item, (Slice, OpenSlice, Reversed)):
                pass
            elif isinstance(item, Zip):
                for items_2 in item.children:
                    return self.visit_for_items_len_item(items_2)
            else:
                return item

    def visit_for_items_body(self, items):
        code  = ''

        for item in items[::-1]:
            if isinstance(item, Data):
                code += indent(
                    f'auto {item.target} = '
                    f'{item.name}_object->get({item.name}.next());') + '\n'
            elif isinstance(item, (Slice, OpenSlice, Reversed)):
                continue
            elif isinstance(item, Zip):
                for items_2 in item.children:
                    code += self.visit_for_items_body(items_2)

                continue
            else:
                code += indent(f'auto {item.target} = {item.name}.next();') + '\n'

            if not item.target.startswith('_'):
                self.context.define_variable(item.target, item.mys_type, None)

        return code

    def visit_For(self, node):
        self.context.push()

        if isinstance(node.iter, ast.Call):
            target = UnpackVisitor().visit(node.target)
            items = []
            self.visit_for_call(items, target, node.iter)
            code = self.visit_for_items_init(items)
            length = self.unique('len')
            item = self.visit_for_items_len_item(items)
            code += f'auto {length} = {item.name}.length();\n'
            code += self.visit_for_items_iter(items)
            i = self.unique('i')
            code += f'for (auto {i} = 0; {i} < {length}; {i}++) {{\n'
            code += self.visit_for_items_body(items)
            body = indent('\n'.join([
                self.visit(item)
                for item in node.body
            ]))
            code += body + '\n'
            code += '}'
        else:
            value = self.visit(node.iter)
            mys_type = self.context.mys_type

            if isinstance(mys_type, list):
                code = self.visit_for_list(node, value, mys_type)
            elif isinstance(mys_type, tuple):
                raise LanguageError("it's not allowed to iterate over tuples",
                                    node.iter.lineno,
                                    node.iter.col_offset)
            elif isinstance(mys_type, dict):
                raise LanguageError("it's not yet supported to iterate over dicts",
                                    node.iter.lineno,
                                    node.iter.col_offset)
            else:
                raise LanguageError("iteration over this is not supported",
                                    node.lineno,
                                    node.col_offset)

        self.context.pop()

        return code

    def visit_Attribute(self, node):
        value = self.visit(node.value)

        if self.context.is_enum_defined(value):
            enum_type = self.context.get_enum_type(value)
            self.context.mys_type = enum_type

            return f'({enum_type}){value}::{node.attr}'
        else:
            if value == 'self':
                value = 'this'

            return f'{value}->{node.attr}'

    def visit_compare(self, node):
        value_nodes = [node.left] + node.comparators
        items = []

        for value_node in value_nodes:
            if is_integer_literal(value_node):
                items.append(('integer', value_node))
            elif is_float_literal(value_node):
                items.append(('float', value_node))
            else:
                value = self.visit(value_node)
                items.append((self.context.mys_type, value))

        for i in range(len(node.ops)):
            left_mys_type = items[i][0]
            right_mys_type = items[i + 1][0]

            if isinstance(node.ops[i], (ast.In, ast.NotIn)):
                if not isinstance(right_mys_type, list):
                    raise LanguageError("not an iterable",
                                        value_nodes[i + 1].lineno,
                                        value_nodes[i + 1].col_offset)

        for i, (mys_type, value_node) in enumerate(items[:-1]):
            if mys_type in ['integer', 'float']:
                items[i] = self.visit_compare_resolve_literal(items,
                                                              node.ops,
                                                              i,
                                                              value_node)

        i = len(items) - 1
        mys_type, value_node = items[-1]

        if mys_type in ['integer', 'float']:
            items[i] = self.visit_compare_resolve_literal(items,
                                                          node.ops,
                                                          i,
                                                          value_node)

        for i in range(len(node.ops)):
            left_mys_type = items[i][0]
            right_mys_type = items[i + 1][0]

            if isinstance(node.ops[i], (ast.In, ast.NotIn)):
                if left_mys_type != right_mys_type[0]:
                    raise_types_differs(left_mys_type,
                                        right_mys_type[0],
                                        value_nodes[i])
            else:
                if left_mys_type != right_mys_type:
                    raise_types_differs(left_mys_type,
                                        right_mys_type,
                                        value_nodes[i])

        if len(items) != 2:
            raise LanguageError("can only compare two values",
                                node.lineno,
                                node.col_offset)

        return items, [type(op) for op in node.ops]

    def make_integer_literal_compare(self, mys_type, value_node):
        return mys_type, make_integer_literal(mys_type, value_node)

    def make_float_literal_compare(self, mys_type, value_node):
        return mys_type, make_float_literal(mys_type, value_node)

    def visit_compare_resolve_literal(self, items, ops, i, value_node):
        mys_type = items[i][0]

        for (other_mys_type, _), op in zip(items[i + 1:], ops[i:]):
            if isinstance(op, (ast.In, ast.NotIn)):
                if mys_type == 'integer':
                    return self.make_integer_literal_compare(other_mys_type[0],
                                                             value_node)
                else:
                    return self.make_float_literal_compare(other_mys_type[0],
                                                           value_node)
            elif other_mys_type not in ['integer', 'float']:
                if mys_type == 'integer':
                    return self.make_integer_literal_compare(other_mys_type, value_node)
                elif mys_type == 'float':
                    return self.make_float_literal_compare(other_mys_type, value_node)

        for (other_mys_type, _), op in zip(reversed(items[:i]), reversed(ops[:i])):
            if isinstance(op, (ast.In, ast.NotIn)):
                raise LanguageError("literals are not iteratable",
                                    value_node.lineno,
                                    value_node.col_offset)
            elif other_mys_type not in ['integer', 'float']:
                if mys_type == 'integer':
                    return self.make_integer_literal_compare(other_mys_type, value_node)
                elif mys_type == 'float':
                    return self.make_float_literal_compare(other_mys_type, value_node)

        raise LanguageError("unable to resolve literal type",
                            value_node.lineno,
                            value_node.col_offset)

    def visit_Compare(self, node):
        items, ops = self.visit_compare(node)
        left_type, left = items[0]
        right_type, right = items[1]
        op_class = ops[0]
        self.context.mys_type = 'bool'

        if op_class == ast.In:
            return f'contains({left}, {right})'
        elif op_class == ast.NotIn:
            return f'!contains({left}, {right})'
        else:
            if left_type != right_type:
                raise LanguageError(
                    f"can't compare '{left_type}' and '{right_type}'",
                    node.lineno,
                    node.col_offset)

            return f'({left} {OPERATORS[op_class]} {right})'

    def visit_If(self, node):
        cond = self.visit(node.test)
        body = indent('\n'.join([
            self.visit(item)
            for item in node.body
        ]))
        orelse = indent('\n'.join([
            self.visit(item)
            for item in node.orelse
        ]))

        code = [f'if ({cond}) {{', body]

        if orelse:
            code += [
                '} else {',
                orelse,
                '}'
            ]
        else:
            code += ['}']

        return '\n'.join(code)

    def visit_return_none(self, node):
        if self.context.return_mys_type is not None:
            raise LanguageError("return value missing",
                                node.lineno,
                                node.col_offset + 7)

        self.context.mys_type = None

        return 'return;'

    def visit_return_value(self, node):
        if self.context.return_mys_type is None:
            raise LanguageError(
                "function does not return any value",
                node.value.lineno,
                node.value.col_offset)

        value = self.visit_value(node.value, self.context.return_mys_type)

        if isinstance(node.value, ast.Name):
            if not self.context.is_variable_defined(value):
                raise LanguageError(
                    f"undefined variable '{value}'",
                    node.value.lineno,
                    node.value.col_offset)

        actual = self.context.mys_type
        expected = self.context.return_mys_type

        if actual != expected:
            actual = format_mys_type(actual)
            expected = format_mys_type(expected)

            raise LanguageError(
                f"returning '{actual}' from a function that returns '{expected}'",
                node.value.lineno,
                node.value.col_offset)

        return f'return {value};'

    def visit_Return(self, node):
        if node.value is None:
            return self.visit_return_none(node)
        else:
            return self.visit_return_value(node)

    def visit_Try(self, node):
        body = indent('\n'.join([self.visit(item) for item in node.body]))
        success_variable = self.unique('success')
        or_else_body = '\n'.join([self.visit(item) for item in node.orelse])

        if or_else_body:
            body += '\n'
            body += indent(f'{success_variable} = true;')

        finalbody = indent(
            '\n'.join([self.visit(item) for item in node.finalbody]))
        handlers = []

        for handler in node.handlers:
            if handler.type is None:
                exception = 'std::exception'
            else:
                exception = self.visit(handler.type)

            self.context.push()

            if handler.name is not None:
                self.context.define_variable(handler.name, None, handler)

            handlers.append('\n'.join([
                f'}} catch ({exception}& e) {{',
                indent('\n'.join([self.visit(item) for item in handler.body]))
            ]))
            self.context.pop()

        if handlers:
            code = '\n'.join([
                'try {',
                body,
                '\n'.join(handlers),
                '}'
            ])

            if or_else_body:
                code = f'bool {success_variable} = false;\n' + code
                code += f'\nif ({success_variable}) {{\n' + indent(or_else_body) + '\n}\n'
        else:
            code = dedent(body)

        if finalbody:
            code = '\n'.join([
                'try {',
                indent(code),
                finalbody,
                '} catch (...) {',
                finalbody,
                indent('throw;'),
                '}'
            ])

        return code

    def visit_Raise(self, node):
        if node.exc is None:
            return 'throw;'
        else:
            exception = self.visit(node.exc)
            return f'throw {exception};'

    def visit_inferred_type_assign(self, node, target):
        if is_integer_literal(node.value):
            self.context.mys_type = 'i64'
            cpp_type = 'i64'
            value = make_integer_literal('i64', node.value)
        elif isinstance(node.value, ast.Constant):
            value = self.visit(node.value)
            mys_type = self.context.mys_type

            if mys_type == 'string':
                value = f'String({value})'
                cpp_type = 'String'
            else:
                cpp_type = mys_type
        elif isinstance(node.value, ast.UnaryOp):
            value = self.visit(node.value)
            cpp_type = self.context.mys_type
        else:
            value = self.visit(node.value)
            cpp_type = 'auto'

        self.context.define_variable(target, self.context.mys_type, node)

        return f'{cpp_type} {target} = {value};'

    def visit_Assign(self, node):
        target = node.targets[0]

        if isinstance(target, ast.Tuple):
            value = self.visit(node.value)
            mys_type = self.context.mys_type

            if not isinstance(mys_type, tuple):
                raise LanguageError('only tuples can be unpacked',
                                    node.value.lineno,
                                    node.value.col_offset)

            temp = self.unique('tuple')
            lines = [f'auto {temp} = {value};']

            for i, item in enumerate(target.elts):
                name = self.visit(item)
                self.context.define_variable(name, mys_type[i], item)
                lines.append(f'auto {name} = std::get<{i}>(*{temp}.m_tuple);')

            return '\n'.join(lines)
        else:
            target = self.visit(target)

            if self.context.is_variable_defined(target):
                if target == 'self':
                    raise LanguageError("it's not allowed to assign to 'self'",
                                        node.lineno,
                                        node.col_offset)

                if is_integer_literal(node.value):
                    value = make_integer_literal(
                        self.context.get_variable_type(target),
                        node.value)
                else:
                    value = self.visit(node.value)

                return f'{target} = {value};'
            else:
                return self.visit_inferred_type_assign(node, target)

    def visit_Subscript(self, node):
        value = self.visit(node.value)
        mys_type = self.context.mys_type[0]
        index = self.visit(node.slice)
        self.context.mys_type = mys_type

        return f'{value}->get({index})'

    def visit_value(self, node, mys_type):
        if is_integer_literal(node):
            self.context.mys_type = mys_type

            return make_integer_literal(mys_type, node)
        elif is_float_literal(node):
            self.context.mys_type = mys_type

            return make_float_literal(mys_type, node)
        else:
            return self.visit(node)

    def visit_AnnAssign(self, node):
        if node.value is None:
            raise LanguageError(
                "variables must be initialized when declared",
                node.lineno,
                node.col_offset)

        target = node.target.id
        mys_type = TypeVisitor().visit(node.annotation)

        if isinstance(node.annotation, ast.List):
            cpp_type = CppTypeVisitor(self.source_lines,
                                      self.context,
                                      self.filename).visit(node.annotation.elts[0])

            if isinstance(node.value, ast.Name):
                value = self.visit(node.value)
            else:
                value = ', '.join([self.visit(item)
                                   for item in node.value.elts])

            self.context.define_variable(target, mys_type, node.target)

            return (f'auto {target} = std::make_shared<List<{cpp_type}>>('
                    f'std::initializer_list<{cpp_type}>{{{value}}});')

        cpp_type = CppTypeVisitor(self.source_lines,
                                  self.context,
                                  self.filename).visit(node.annotation)
        value = self.visit_value(node.value, cpp_type)

        if self.context.mys_type != mys_type:
            raise_types_differs(self.context.mys_type, mys_type, node.value)

        self.context.define_variable(target, mys_type, node.target)

        if cpp_type in PRIMITIVE_TYPES:
            return f'{cpp_type} {target} = {value};'
        elif cpp_type == 'String':
            return f'auto {target} = String({value});'
        else:
            return f'auto {target} = {value};'

    def visit_While(self, node):
        condition = self.visit(node.test)
        body = indent('\n'.join([self.visit(item) for item in node.body]))

        return '\n'.join([
            f'while ({condition}) {{',
            body,
            '}'
        ])

    def visit_Pass(self, node):
        return ''

    def visit_Break(self, node):
        return 'break;'

    def visit_Continue(self, node):
        return 'continue;'

    def visit_Assert(self, node):
        prepare = []

        if isinstance(node.test, ast.Compare):
            items, ops = self.visit_compare(node.test)
            variables = []

            for mys_type, value in items:
                variable = self.unique('var')
                cpp_type = mys_to_cpp_type(mys_type)
                prepare.append(f'{cpp_type} {variable} = {value};')
                variables.append(variable)

            conds = []
            messages = []

            for i, op_class in enumerate(ops):
                if op_class == ast.In:
                    conds.append(f'contains({variables[i]}, {variables[i + 1]})')
                    messages.append(f'{variables[i]} << " in "')
                elif op_class == ast.NotIn:
                    conds.append(f'!contains({variables[i]}, {variables[i + 1]})')
                    messages.append(f'{variables[i]} << " not in "')
                else:
                    op = OPERATORS[op_class]
                    conds.append(f'({variables[i]} {op} {variables[i + 1]})')
                    messages.append(f'{variables[i]} << " {op} "')

            messages.append(f'{variables[-1]}')
            cond = ' && '.join(conds)
            message = ' << '.join(messages)
        else:
            message = '"todo"'
            cond = self.visit(node.test)

        filename = self.filename
        line = node.lineno

        return '\n'.join([
            '#if defined(MYS_TEST) || !defined(NDEBUG)'
        ] + prepare + [
            f'if(!({cond})) {{',
            f'    std::cout << "{filename}:{line}: assert " << {message} << '
            '" is not true" << std::endl;',
            f'    throw AssertionError("todo is not true");',
            '}',
            '#endif'
        ])

    def visit_With(self, node):
        items = '\n'.join([
            self.visit(item) + ';'
            for item in node.items
        ])
        body = indent('\n'.join([self.visit(item) for item in node.body]))

        return '\n'.join([
            '{',
            indent(items),
            body,
            '}'
        ])

    def visit_withitem(self, node):
        expr = self.visit(node.context_expr)
        var = self.visit(node.optional_vars)

        return f'auto {var} = {expr}'

    def visit_Lambda(self, node):
        raise LanguageError('lambda functions are not supported',
                            node.lineno,
                            node.col_offset)

    def visit_Import(self, node):
        raise LanguageError('imports are only allowed on module level',
                            node.lineno,
                            node.col_offset)

    def visit_ImportFrom(self, node):
        raise LanguageError('imports are only allowed on module level',
                            node.lineno,
                            node.col_offset)

    def visit_ClassDef(self, node):
        raise LanguageError('class definitions are only allowed on module level',
                            node.lineno,
                            node.col_offset)

    def visit_JoinedStr(self, node):
        if node.values:
            return ' + '.join([
                self.visit(value)
                for value in node.values
            ])
        else:
            return '""'

    def visit_FormattedValue(self, node):
        if isinstance(node.value, ast.Name):
            if not self.context.is_variable_defined(node.value.id):
                raise LanguageError(
                    f"undefined variable '{node.value.id}'",
                    node.value.lineno,
                    node.value.col_offset)

        return f'str({self.visit(node.value)})'

    def visit_BoolOp(self, node):
        values = [self.visit(value) for value in node.values]
        op = BOOL_OPS[type(node.op)]

        return '((' + f') {op} ('.join(values) + '))'

    def is_trait(self, type_name):
        # ToDo: Should check if the trait is defined. That information
        #       in not yet avaialble.
        return type_name[0].isupper()

    def is_class(self, type_name):
        return False

    def visit_trait_match(self, subject, code, node):
        cases = []

        for case in node.cases:
            casted = self.unique('casted')

            if isinstance(case.pattern, ast.Call):
                class_name = case.pattern.func.id
                cases.append(
                    f'auto {casted} = '
                    f'std::dynamic_pointer_cast<{class_name}>({subject});\n'
                    f'if ({casted}) {{\n' +
                    indent('\n'.join([self.visit(item) for item in case.body])) +
                    '\n}')
            elif isinstance(case.pattern, ast.MatchAs):
                if isinstance(case.pattern.pattern, ast.Call):
                    class_name = case.pattern.pattern.func.id
                    self.context.push()
                    self.context.define_variable(case.pattern.name, class_name, case)
                    cases.append(
                        f'auto {casted} = '
                        f'std::dynamic_pointer_cast<{class_name}>({subject});\n'
                        f'if ({casted}) {{\n'
                        f'    auto {case.pattern.name} = std::move({casted});\n' +
                        indent('\n'.join([self.visit(item) for item in case.body])) +
                        '\n}')
                    self.context.pop()
                else:
                    raise LanguageError(
                        'trait match patterns must be classes',
                        case.pattern.lineno,
                        case.pattern.col_offset)
            else:
                raise LanguageError(
                    'trait match patterns must be classes',
                    case.pattern.lineno,
                    case.pattern.col_offset)

        body = ''

        for case in cases[1:][::-1]:
            body = ' else {\n' + indent(case + body) + '\n}'

        return cases[0] + body

    def visit_Match(self, node):
        code = ''

        if isinstance(node.subject, ast.Call):
            subject = self.unique('subject')
            code += f'auto {subject} = {self.visit(node.subject)};\n'
            subject_type = 'i32'
        elif isinstance(node.subject, ast.Name):
            subject = node.subject.id
            subject_type = self.context.get_variable_type(subject)
        else:
            raise LanguageError(
                'match subject can only be variables and return values',
                node.lineno,
                node.col_offset)

        if subject_type is None:
            raise LanguageError('match subject type not supported',
                                node.lineno,
                                node.col_offset)

        if self.is_trait(subject_type):
            return self.visit_trait_match(subject, code, node)
        elif self.is_class(subject_type):
            return ''
        else:
            cases = []

            for case in node.cases:
                pattern = self.visit(case.pattern)
                body = indent('\n'.join([self.visit(item) for item in case.body]))

                if pattern == '_':
                    cases.append(f'{{\n' + body + '\n}')
                else:
                    cases.append(f'if ({subject} == {pattern}) {{\n' + body + '\n}')

            code += ' else '.join(cases)

            return code

    def generic_visit(self, node):
        raise LanguageError('unsupported language construct',
                            node.lineno,
                            node.col_offset)

class CppTypeVisitor(BaseVisitor):

    def visit_Name(self, node):
        type_ = node.id

        if type_ == 'string':
            return 'String'
        elif self.is_class_or_trait_defined(type_):
            return f'std::shared_ptr<{type_}>'
        elif self.context.is_enum_defined(type_):
            return self.context.get_enum_type(type_)
        else:
            return type_

    def visit_List(self, node):
        return f'std::shared_ptr<List<{self.visit(node.elts[0])}>>'

    def visit_Tuple(self, node):
        items = ', '.join([self.visit(elem) for elem in node.elts])

        return f'Tuple<{items}>'

    def visit_Dict(self, node):
        return (f'std::shared_ptr<Dict<{node.keys[0].id}, '
                f'{self.visit(node.values[0])}>>')

class ParamVisitor(BaseVisitor):

    def visit_arg(self, node):
        param_name = node.arg
        self.context.define_variable(param_name,
                                     TypeVisitor().visit(node.annotation),
                                     node)
        cpp_type = CppTypeVisitor(self.source_lines,
                                  self.context,
                                  self.filename).visit(node.annotation)

        if isinstance(node.annotation, ast.Name):
            param_type = node.annotation.id

            if (param_type == 'string'
                or self.is_class_or_trait_defined(param_type)):
                cpp_type = f'const {cpp_type}&'

            return f'{cpp_type} {param_name}'
        else:
            return f'{cpp_type}& {param_name}'
