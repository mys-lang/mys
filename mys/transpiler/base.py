import textwrap

from ..parser import ast
from .comprehension import DictComprehension
from .comprehension import ListComprehension
from .constant_visitor import is_constant
from .generics import generic_class_setup
from .generics import specialize_function
from .utils import BUILTIN_CALLS
from .utils import BUILTIN_ERRORS
from .utils import INTEGER_TYPES
from .utils import LIST_METHODS
from .utils import NUMBER_TYPES
from .utils import OPERATORS
from .utils import REGEX_METHODS
from .utils import REGEXMATCH_METHODS
from .utils import STRING_METHODS
from .utils import CompileError
from .utils import InternalError
from .utils import dedent
from .utils import dot2ns
from .utils import format_binop
from .utils import format_default_call
from .utils import format_mys_type
from .utils import indent
from .utils import is_float_literal
from .utils import is_integer_literal
from .utils import is_primitive_type
from .utils import is_private
from .utils import is_snake_case
from .utils import is_string
from .utils import make_float_literal
from .utils import make_integer_literal
from .utils import make_name
from .utils import make_shared
from .utils import make_shared_dict
from .utils import make_shared_list
from .utils import mys_to_cpp_type
from .utils import raise_types_differs
from .utils import split_dict_mys_type
from .value_type_visitor import Dict
from .value_type_visitor import ValueTypeVisitor
from .value_type_visitor import intersection_of
from .value_type_visitor import reduce_type
from .variables import Variables

BOOL_OPS = {
    ast.And: '&&',
    ast.Or: '||'
}

FOR_LOOP_FUNCS = set(['enumerate', 'range', 'reversed', 'slice', 'zip'])


def mys_type_to_target_cpp_type(mys_type):
    if is_primitive_type(mys_type):
        return 'auto'
    else:
        return 'const auto&'


def wrap_not_none(obj, mys_type):
    if is_primitive_type(mys_type):
        return obj
    elif obj == 'this':
        return obj
    elif mys_type == 'string':
        return f'string_not_none({obj})'
    elif mys_type == 'regex':
        return f'regex_not_none({obj})'
    elif mys_type == 'regexmatch':
        return f'regexmatch_not_none({obj})'
    elif mys_type == 'bytes':
        return f'bytes_not_none({obj})'
    else:
        return f'shared_ptr_not_none({obj})'


def compare_is_variable(variable, variable_mys_type):
    if variable != 'nullptr':
        if variable_mys_type == 'string':
            variable = f'{variable}.m_string'
        elif variable_mys_type == 'regexmatch':
            variable = f'{variable}.m_match_data'
        elif variable_mys_type == 'bytes':
            variable = f'{variable}.m_bytes'

    return variable


def compare_is_variables(left, left_mys_type, right, right_mys_type):
    left = compare_is_variable(left, left_mys_type)
    right = compare_is_variable(right, right_mys_type)

    return left, right


def compare_assert_is_variable(variable):
    if variable[1] == 'string':
        variable = f'{variable[0]}.m_string'
    elif variable[1] == 'bytes':
        variable = f'{variable[0]}.m_bytes'
    elif variable[1] == 'regexmatch':
        variable = f'{variable[0]}.m_match_data'
    else:
        variable = variable[0]

    return variable


def compare_assert_is_variables(variable_1, variable_2):
    variable_1 = compare_assert_is_variable(variable_1)
    variable_2 = compare_assert_is_variable(variable_2)

    return variable_1, variable_2


def is_allowed_dict_key_type(mys_type):
    if is_primitive_type(mys_type):
        return True
    elif mys_type == 'string':
        return True

    return False


def raise_if_self(name, node):
    if name == 'self':
        raise CompileError("it's not allowed to assign to 'self'", node)


def raise_if_wrong_number_of_parameters(actual_nargs,
                                        expected_nargs,
                                        node,
                                        min_args=None):
    if min_args is None:
        min_args = expected_nargs

    if min_args <= actual_nargs <= expected_nargs:
        return

    if expected_nargs == 1:
        raise CompileError(
            f"expected {expected_nargs} parameter, got {actual_nargs}",
            node)
    else:
        raise CompileError(
            f"expected {expected_nargs} parameters, got {actual_nargs}",
            node)


def format_str(value, mys_type, context):
    if is_primitive_type(mys_type):
        return f'String({value})'
    elif mys_type == 'string':
        return f'string_str({value})'
    elif mys_type == 'bytes':
        return f'bytes_str({value})'
    elif mys_type == 'regexmatch':
        return f'regexmatch_str({value})'
    elif context.is_enum_defined(mys_type):
        return f'String({value})'
    else:
        none = handle_string("None")

        return f'({value} ? shared_ptr_not_none({value})->__str__() : {none})'


def format_assert_str(value, mys_type, context):
    if is_primitive_type(mys_type):
        return f'String({value})'
    elif mys_type == 'string':
        return f'string_with_quotes({value})'
    elif mys_type == 'bytes':
        return f'bytes_str({value})'
    elif mys_type == 'regexmatch':
        return f'regexmatch_str({value})'
    elif context.is_enum_defined(mys_type):
        return f'String({value})'
    else:
        none = handle_string("None")

        return f'({value} ? shared_ptr_not_none({value})->__str__() : {none})'


def format_print_arg(arg):
    value, mys_type = arg

    if mys_type == 'i8':
        value = f'(int){value}'
    elif mys_type == 'u8':
        value = f'(unsigned){value}'
    elif mys_type == 'string':
        value = f'PrintString({value})'
    elif mys_type == 'char':
        value = f'PrintChar({value})'

    return value


def format_arg(arg):
    value, mys_type = arg

    if mys_type == 'i8':
        value = f'(int){value}'
    elif mys_type == 'u8':
        value = f'(unsigned){value}'

    return value


def raise_wrong_types(actual_mys_type, expected_mys_type, node):
    if is_primitive_type(expected_mys_type) and actual_mys_type is None:
        raise CompileError(f"'{expected_mys_type}' cannot be None", node)
    else:
        actual = format_mys_type(actual_mys_type)
        expected = format_mys_type(expected_mys_type)

        raise CompileError(f"expected a '{expected}', got a '{actual}'", node)


def raise_if_wrong_types(actual_mys_type, expected_mys_type, node, context):
    if actual_mys_type == expected_mys_type:
        return

    if actual_mys_type is None:
        if context.is_class_or_trait_defined(expected_mys_type):
            return
        elif expected_mys_type in ['string', 'bytes']:
            return
        elif isinstance(expected_mys_type, (list, tuple, dict)):
            return

    raise_wrong_types(actual_mys_type, expected_mys_type, node)


def raise_if_not_bool(mys_type, node, context):
    raise_if_wrong_types(mys_type, 'bool', node, context)


def raise_if_wrong_visited_type(context, expected_mys_type, node):
    raise_if_wrong_types(context.mys_type,
                         expected_mys_type,
                         node,
                         context)


class TypeVisitor(ast.NodeVisitor):

    def __init__(self, context):
        self.context = context

    def visit_Name(self, node):
        name = node.id

        if self.context.is_class_defined(name):
            name = self.context.make_full_name(name)
        elif self.context.is_enum_defined(name):
            name = self.context.make_full_name(name)
        elif self.context.is_trait_defined(name):
            name = self.context.make_full_name(name)

        return name

    def visit_List(self, node):
        nitems = len(node.elts)

        if nitems != 1:
            raise CompileError(f"expected 1 type in list, got {nitems}", node)

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


class Range:

    def __init__(self, target, target_node, begin, end, step, mys_type):
        self.target = target
        self.target_node = target_node
        self.begin = begin
        self.end = end
        self.step = step
        self.mys_type = mys_type


class Enumerate:

    def __init__(self, target, target_node, initial, mys_type):
        self.target = target
        self.target_node = target_node
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

    def __init__(self, target, target_node, value, mys_type):
        self.target = target
        self.target_node = target_node
        self.value = value
        self.mys_type = mys_type


def is_ascii(value):
    return len(value) == len(value.encode('utf-8'))


def handle_string(value):
    if value.startswith('mys-embedded-c++'):
        return '\n'.join([
            '/* mys-embedded-c++ start */\n',
            textwrap.dedent(value[16:]).strip(),
            '\n/* mys-embedded-c++ stop */'])
    elif is_ascii(value):
        value = value.encode("unicode_escape").decode('utf-8')
        value = value.replace('"', '\\"')

        return f'String("{value}")'
    else:
        values = []

        for ch in value:
            values.append(f'Char({ord(ch)})')

        value = ', '.join(values)

        return f'String({{{value}}})'


def find_item_with_length(items):
    for item in items:
        if isinstance(item, (Slice, OpenSlice, Reversed)):
            pass
        elif isinstance(item, Zip):
            return find_item_with_length(item.children[0])
        else:
            return item

    raise Exception("no length")


class BaseVisitor(ast.NodeVisitor):

    def __init__(self, source_lines, context, filename):
        self.source_lines = source_lines
        self.context = context
        self.filename = filename
        self.constants = []

    def unique_number(self):
        return self.context.unique_number()

    def unique(self, name):
        return self.context.unique(name)

    def mys_to_cpp_type(self, mys_type):
        return mys_to_cpp_type(mys_type, self.context)

    def visit_Name(self, node):
        name = node.id

        if name == '__unique_id__':
            self.context.mys_type = 'i64'

            return str(self.unique_number())
        elif name == '__line__':
            self.context.mys_type = 'u64'

            return str(node.lineno)
        elif name == '__name__':
            self.context.mys_type = 'string'

            return handle_string(self.context.name)
        elif name == '__file__':
            self.context.mys_type = 'string'

            return handle_string(self.filename)
        elif self.context.is_local_variable_defined(name):
            self.context.mys_type = self.context.get_local_variable_type(name)

            if name == 'self':
                return 'shared_from_this()'
            else:
                return make_name(name)
        elif self.context.is_global_variable_defined(name):
            self.context.mys_type = self.context.get_global_variable_type(name)

            return dot2ns(self.context.make_full_name(name))
        else:
            raise CompileError(f"undefined variable '{name}'", node)

    def find_print_kwargs(self, node):
        end = ' << std::endl'
        flush = None

        for keyword in node.keywords:
            if keyword.arg == 'end':
                value = self.visit(keyword.value)
                end = f' << PrintString({value})'
            elif keyword.arg == 'flush':
                flush = self.visit(keyword.value)
            else:
                raise CompileError(
                    f"invalid keyword argument '{keyword.arg}' to print(), only "
                    "'end' and 'flush' are allowed",
                    node)

        return end, flush

    def handle_print(self, node):
        args = []

        for arg in node.args:
            if is_integer_literal(arg):
                args.append((make_integer_literal('i64', arg), 'i64'))
                self.context.mys_type = 'i64'
            else:
                args.append((self.visit(arg), self.context.mys_type))

                if self.context.mys_type is None:
                    raise CompileError("None cannot be printed", arg)

        end, flush = self.find_print_kwargs(node)
        code = 'std::cout'

        if len(args) == 1:
            code += f' << {format_print_arg(args[0])}'
        elif len(args) != 0:
            first = format_print_arg(args[0])
            args = ' << " " << '.join([format_print_arg(arg) for arg in args[1:]])
            code += f' << {first} << " " << {args}'

        code += end

        if flush:
            code += ';\n'
            code += f'if ({flush}) {{\n'
            code += '    std::cout << std::flush;\n'
            code += '}'

        self.context.mys_type = None

        return code

    def visit_values_of_same_type(self, value_nodes):
        items = []
        mys_type = None

        for value_node in value_nodes:
            if is_integer_literal(value_node):
                items.append(('integer', value_node))
            elif is_float_literal(value_node):
                items.append(('float', value_node))
            else:
                value = self.visit(value_node)
                items.append((self.context.mys_type, value))

                if mys_type is None:
                    mys_type = self.context.mys_type

        if mys_type is None:
            if items[0][0] == 'integer':
                mys_type = 'i64'
            else:
                mys_type = 'f64'

        values = []

        for i, (item_mys_type, value_node) in enumerate(items):
            if item_mys_type in ['integer', 'float']:
                value = self.visit_value_check_type(value_node, mys_type)
            else:
                raise_if_wrong_types(item_mys_type,
                                     mys_type,
                                     value_nodes[i],
                                     self.context)
                value = value_node

            values.append(value)

        self.context.mys_type = mys_type

        return values

    def handle_min_max(self, node, name):
        nargs = len(node.args)

        if nargs == 0:
            raise CompileError("expected at least one parameter", node)
        elif nargs == 1:
            values = [self.visit(node.args[0])]

            if not isinstance(self.context.mys_type, list):
                raise CompileError('expected a list', node.args[0])

            self.context.mys_type = self.context.mys_type[0]
        else:
            values = self.visit_values_of_same_type(node.args)

        items = ', '.join(values)

        return f'{name}({items})'

    def handle_sum(self, node):
        nargs = len(node.args)

        if nargs != 1:
            raise CompileError("expected one parameter", node)

        values = self.visit(node.args[0])
        if not isinstance(self.context.mys_type, list):
            raise CompileError('expected a list', node.args[0])

        self.context.mys_type = self.context.mys_type[0]

        return f'sum({values})'

    def handle_len(self, node):
        raise_if_wrong_number_of_parameters(len(node.args), 1, node)
        value = self.visit(node.args[0])
        mys_type = self.context.mys_type
        self.context.mys_type = 'u64'

        if mys_type == 'string':
            if value.startswith('"'):
                return f'strlen({value})'
            else:
                return f'{value}.__len__()'
        elif mys_type == 'bytes':
            return f'{value}.__len__()'
        else:
            return f'shared_ptr_not_none({value})->__len__()'

    def handle_str(self, node):
        raise_if_wrong_number_of_parameters(len(node.args), 1, node)
        value = self.visit(node.args[0])
        mys_type = self.context.mys_type
        self.context.mys_type = 'string'

        return format_str(value, mys_type, self.context)

    def handle_list(self, node):
        raise_if_wrong_number_of_parameters(len(node.args), 1, node)
        value = self.visit(node.args[0])
        mys_type = self.context.mys_type

        if isinstance(mys_type, dict):
            key_mys_type, value_mys_type = list(mys_type.items())[0]
            self.context.mys_type = [(key_mys_type, value_mys_type)]
            key_cpp_type = self.mys_to_cpp_type(key_mys_type)
            value_cpp_type = self.mys_to_cpp_type(value_mys_type)

            return (f'create_list_from_dict<{key_cpp_type}, {value_cpp_type}>('
                    f'{value})')
        else:
            raise CompileError("not supported", node)

    def handle_char(self, node):
        raise_if_wrong_number_of_parameters(len(node.args), 1, node)
        value = self.visit_value_check_type(node.args[0], 'i32')
        self.context.mys_type = 'char'

        return f'Char({value})'

    def handle_input(self, node):
        raise_if_wrong_number_of_parameters(len(node.args), 1, node)
        prompt = self.visit_value_check_type(node.args[0], 'string')
        self.context.mys_type = 'string'

        return f'input({prompt})'

    def visit_call_params_keywords(self, function, node):
        keyword_args = {}
        params = {param.name: param.type for param, _ in function.args}
        positional_params_names = [
            param.name for param, _ in function.args[:len(node.args)]
        ]

        if node.keywords:
            for keyword in node.keywords:
                param_name = keyword.arg

                if param_name not in params:
                    raise CompileError(f"invalid parameter '{param_name}'",
                                       keyword)

                if param_name in positional_params_names:
                    param_type = format_mys_type(params[param_name])

                    raise CompileError(
                        f"parameter '{param_name}: {param_type}' given more than "
                        "once",
                        keyword)

                if param_name in keyword_args:
                    param_type = format_mys_type(params[param_name])

                    raise CompileError(
                        f"parameter '{param_name}: {param_type}' given more than "
                        "once",
                        keyword)

                keyword_args[param_name] = keyword.value

        return keyword_args

    def visit_call_params(self, full_name, function, node):
        keyword_args = self.visit_call_params_keywords(function, node)
        call_args = []

        for i, (param, default) in enumerate(function.args):
            if i < len(node.args):
                value = self.visit_value_check_type(node.args[i], param.type)
            else:
                value = keyword_args.get(param.name)

                if value is None:
                    if is_constant(default):
                        value = self.visit_value_check_type(default, param.type)
                    elif default is not None:
                        value = format_default_call(full_name, param.name)
                    else:
                        param_type = format_mys_type(param.type)

                        raise CompileError(
                            f"parameter '{param.name}: {param_type}' not given",
                            node)
                else:
                    value = self.visit_value_check_type(value, param.type)

            call_args.append(value)

        min_args = len([default for _, default in function.args if default is None])
        raise_if_wrong_number_of_parameters(len(node.args) + len(node.keywords),
                                            len(function.args),
                                            node.func,
                                            min_args)

        return call_args

    def visit_call_function(self, full_name, node):
        functions = self.context.get_functions(full_name)

        if len(functions) != 1:
            raise CompileError("overloaded functions are not yet supported",
                               node.func)

        function = functions[0]
        args = self.visit_call_params(full_name, function, node)
        self.context.mys_type = function.returns

        return f'{dot2ns(full_name)}({", ".join(args)})'

    def visit_call_class(self, mys_type, node):
        cls = self.context.get_class_definitions(mys_type)
        args = []
        function = cls.methods['__init__'][0]
        args = self.visit_call_params(f'{mys_type}_{cls.name}', function, node)
        args = ', '.join(args)
        self.context.mys_type = mys_type

        return make_shared(dot2ns(mys_type), args)

    def visit_call_enum(self, mys_type, node):
        raise_if_wrong_number_of_parameters(len(node.args), 1, node)
        cpp_type = self.context.get_enum_type(mys_type)
        value = self.visit_value_check_type(node.args[0], cpp_type)
        full_name = self.context.make_full_name(mys_type)
        self.context.mys_type = full_name

        return f'{dot2ns(full_name)}_from_value({value})'

    def visit_call_builtin(self, name, node):
        if name == 'print':
            code = self.handle_print(node)
        elif name in ['min', 'max']:
            code = self.handle_min_max(node, name)
        elif name == 'sum':
            code = self.handle_sum(node)
        elif name == 'len':
            code = self.handle_len(node)
        elif name == 'str':
            code = self.handle_str(node)
        elif name == 'list':
            code = self.handle_list(node)
        elif name == 'char':
            code = self.handle_char(node)
        elif name in FOR_LOOP_FUNCS:
            raise CompileError('function can only be used in for-loops', node)
        elif name == 'input':
            code = self.handle_input(node)
        elif name in BUILTIN_ERRORS:
            args = []

            for arg in node.args:
                if is_integer_literal(arg):
                    args.append((make_integer_literal('i64', arg), 'i64'))
                    self.context.mys_type = 'i64'
                else:
                    args.append((self.visit(arg), self.context.mys_type))

            args = ', '.join([value for value, _ in args])
            code = make_shared(name, args)
            self.context.mys_type = name
        else:
            args = []

            for arg in node.args:
                if is_integer_literal(arg):
                    args.append((make_integer_literal('i64', arg), 'i64'))
                    self.context.mys_type = 'i64'
                else:
                    args.append((self.visit(arg), self.context.mys_type))

            args = ', '.join([value for value, _ in args])

            if name in INTEGER_TYPES:
                if self.context.mys_type == 'string':
                    args += '.__int__()'

                mys_type = name
            elif name in ['f32', 'f64']:
                mys_type = name
            elif name == 'abs':
                mys_type = self.context.mys_type
            else:
                mys_type = None

            code = f'{name}({args})'
            self.context.mys_type = mys_type

        return code

    def visit_call_method_list(self, name, mys_type, args, node):
        spec = LIST_METHODS.get(name)
        if spec is None:
            raise CompileError('list method not implemented', node)

        if spec[1] == '<listtype>':
            self.context.mys_type = mys_type[0]
        else:
            self.context.mys_type = spec[1]
        if name == 'pop' and len(args) == 0:
            args.append('std::nullopt')
        raise_if_wrong_number_of_parameters(len(args), len(spec[0]), node)

    def visit_call_method_dict(self, name, mys_type, args, node):
        if name == 'keys':
            raise_if_wrong_number_of_parameters(len(args), 0, node)
            self.context.mys_type = list(mys_type.keys())
        elif name == 'values':
            raise_if_wrong_number_of_parameters(len(args), 0, node)
            self.context.mys_type = list(mys_type.values())
        elif name == 'get':
            raise_if_wrong_number_of_parameters(len(args), 2, node)
            self.context.mys_type = list(mys_type.values())[0]
        elif name == 'pop':
            raise_if_wrong_number_of_parameters(len(args), 2, node)
            self.context.mys_type = list(mys_type.values())[0]
        elif name == 'clear':
            raise_if_wrong_number_of_parameters(len(args), 0, node)
            self.context.mys_type = None
        elif name == 'update':
            raise_if_wrong_number_of_parameters(len(args), 1, node)
            self.context.mys_type = None
        else:
            raise CompileError('dict method not implemented', node)

    def visit_call_method_string(self, name, args, node):
        spec = STRING_METHODS.get(name)

        if spec is None:
            raise CompileError('string method not implemented', node)

        self.context.mys_type = spec[1]
        if name in ['find', 'find_reverse'] and 1 <= len(args) < 3:
            for _ in range(3 - len(args)):
                args.append('std::nullopt')
        elif name in ['strip', 'strip_left', 'strip_right'] and len(args) == 0:
            args.append('std::nullopt')

        raise_if_wrong_number_of_parameters(len(args), len(spec[0]), node)

        return '.', args

    def visit_call_method_regexmatch(self, name, node):
        spec = REGEXMATCH_METHODS.get(name)

        if spec is None:
            raise CompileError('regex match method not implemented', node)

        self.context.mys_type = spec[1]

        return '.'

    def visit_call_method_regex(self, name, node):
        spec = REGEX_METHODS.get(name)

        if spec is None:
            raise CompileError('regex method not implemented', node)

        self.context.mys_type = spec[1]

        return '.'

    def visit_call_method_class(self, name, mys_type, value, node):
        definitions = self.context.get_class_definitions(mys_type)

        if name in definitions.methods:
            method = definitions.methods[name][0]
            args = self.visit_call_params(f'{mys_type}_{name}', method, node)
            self.context.mys_type = method.returns
        else:
            raise CompileError(
                f"class '{mys_type}' has no method '{name}'",
                node)

        if value == 'shared_from_this()':
            value = 'this'
        elif is_private(name):
            raise CompileError(f"class '{mys_type}' method '{name}' is private",
                               node)

        return value, args

    def visit_call_method_trait(self, name, mys_type, node):
        definitions = self.context.get_trait_definitions(mys_type)

        if name in definitions.methods:
            method = definitions.methods[name][0]
            args = self.visit_call_params(name, method, node)
            self.context.mys_type = method.returns
        else:
            raise CompileError(
                f"trait '{mys_type}' has no function '{name}'",
                node)

        return args

    def visit_call_method(self, node):
        name = node.func.attr
        args = []
        arg_types = []

        for arg in node.args:
            if is_integer_literal(arg):
                args.append(make_integer_literal('i64', arg))
                arg_types.append('i64')
                self.context.mys_type = 'i64'
            else:
                args.append(self.visit(arg))
                arg_types.append(self.context.mys_type)

        value = self.visit(node.func.value)
        mys_type = self.context.mys_type
        op = '->'

        if isinstance(mys_type, list):
            self.visit_call_method_list(name, mys_type, args, node.func)
        elif isinstance(mys_type, dict):
            self.visit_call_method_dict(name, mys_type, args, node.func)
        elif mys_type == 'string':
            op, args = self.visit_call_method_string(name, args, node.func)
        elif mys_type == 'regexmatch':
            op = self.visit_call_method_regexmatch(name, node.func)
        elif mys_type == 'regex':
            op = self.visit_call_method_regex(name, node.func)
        elif mys_type == 'bytes':
            raise CompileError('bytes method not implemented', node.func)
        elif self.context.is_class_defined(mys_type):
            value, args = self.visit_call_method_class(name, mys_type, value, node)
        elif self.context.is_trait_defined(mys_type):
            args = self.visit_call_method_trait(name, mys_type, node)
        elif is_primitive_type(mys_type):
            raise CompileError(f"primitive type '{mys_type}' do not have methods",
                               node.func)
        elif mys_type is None:
            raise CompileError('None has no methods', node.func)
        else:
            mys_type = format_mys_type(mys_type)

            raise CompileError(f"'{mys_type}' not defined", node.func)

        value = wrap_not_none(value, mys_type)
        args = ', '.join(args)

        return f'{value}{op}{name}({args})'

    def visit_call_generic_function(self, node):
        name = node.func.value.id
        full_name = self.context.make_full_name(name)
        function = self.context.get_functions(full_name)[0]
        types_slice = node.func.slice
        chosen_types = []

        if isinstance(types_slice, ast.Name):
            type_name = types_slice.id

            if not self.context.is_type_defined(type_name):
                raise CompileError(f"undefined type '{type_name}'", types_slice)
            elif self.context.is_class_defined(type_name):
                type_name = self.context.make_full_name(type_name)

            chosen_types.append(type_name)
        elif isinstance(types_slice, ast.Tuple):
            for item in types_slice.elts:
                if not isinstance(item, ast.Name):
                    raise CompileError('unsupported generic type', node)

                type_name = item.id

                if not self.context.is_type_defined(type_name):
                    raise CompileError(f"undefined type '{type_name}'", item)
                elif self.context.is_class_defined(type_name):
                    type_name = self.context.make_full_name(type_name)

                chosen_types.append(type_name)
        else:
            raise CompileError('invalid specialization of generic function', node)

        joined_chosen_types = '_'.join([
            chosen_type.replace('.', '_')
            for chosen_type in chosen_types
        ])
        specialized_name = f'{name}_{joined_chosen_types}'
        specialized_full_name = f'{full_name}_{joined_chosen_types}'

        if self.context.is_specialized_function_defined(specialized_full_name):
            specialized_function = self.context.get_specialized_function(
                specialized_full_name)
        else:
            specialized_function = specialize_function(function,
                                                       specialized_name,
                                                       chosen_types,
                                                       node)
            self.context.define_specialized_function(specialized_full_name,
                                                     specialized_function,
                                                     node)

        args = self.visit_call_params(specialized_full_name,
                                      specialized_function,
                                      node)
        self.context.mys_type = specialized_function.returns

        return f'{dot2ns(specialized_full_name)}({", ".join(args)})'

    def visit_call_generic_class(self, node):
        specialized_class, specialized_full_name = generic_class_setup(
            node,
            self.context)

        method = specialized_class.methods['__init__'][0]
        args = self.visit_call_params(specialized_full_name,
                                      method,
                                      node)
        args = ', '.join(args)
        self.context.mys_type = specialized_full_name

        return make_shared(dot2ns(specialized_full_name), args)

    def visit_call_generic(self, node):
        if isinstance(node.func.value, ast.Name):
            if self.context.is_class_defined(node.func.value.id):
                return self.visit_call_generic_class(node)
            else:
                return self.visit_call_generic_function(node)
        else:
            raise CompileError('only generic functions and classes are supported',
                               node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            name = node.func.id

            if name in BUILTIN_CALLS:
                return self.visit_call_builtin(name, node)
            else:
                full_name = self.context.make_full_name(name)

                if full_name is None:
                    if is_snake_case(name):
                        raise CompileError(f"undefined function '{name}'", node)
                    else:
                        raise CompileError(f"undefined class/trait/enum '{name}'",
                                           node)
                elif self.context.is_function_defined(full_name):
                    return self.visit_call_function(full_name, node)
                elif self.context.is_class_defined(full_name):
                    return self.visit_call_class(full_name, node)
                elif self.context.is_enum_defined(full_name):
                    return self.visit_call_enum(name, node)
                else:
                    raise InternalError('call', node)
        elif isinstance(node.func, ast.Attribute):
            return self.visit_call_method(node)
        elif isinstance(node.func, ast.Lambda):
            raise CompileError('lambda functions are not supported', node.func)
        elif isinstance(node.func, ast.Subscript):
            return self.visit_call_generic(node)
        else:
            raise CompileError("not callable", node.func)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            if is_string(node, self.source_lines):
                self.context.mys_type = 'string'

                return handle_string(node.value)
            else:
                self.context.mys_type = 'char'

                if node.value:
                    try:
                        value = ord(node.value)
                    except TypeError:
                        raise CompileError("bad character literal", node)
                else:
                    value = -1

                return f"Char({value})"
        elif isinstance(node.value, bool):
            self.context.mys_type = 'bool'

            return f'Bool({str(node.value).lower()})'
        elif isinstance(node.value, float):
            self.context.mys_type = 'f64'

            return str(node.value)
        elif isinstance(node.value, int):
            self.context.mys_type = 'i64'

            return str(node.value)
        elif node.value is None:
            self.context.mys_type = None

            return 'nullptr'
        elif isinstance(node.value, bytes):
            self.context.mys_type = 'bytes'
            values = ', '.join([str(v) for v in node.value])

            return f'Bytes({{{values}}})'
        elif isinstance(node.value, tuple):
            self.context.mys_type = 'regex'
            args = ', '.join([handle_string(s) for s in node.value])
            return f'Regex({args})'
        else:
            raise InternalError("constant node", node)

    def visit_Expr(self, node):
        return self.visit(node.value) + ';'

    def visit_BinOp(self, node):
        left_value_type = ValueTypeVisitor(self.source_lines,
                                           self.context).visit(node.left)
        right_value_type = ValueTypeVisitor(self.source_lines,
                                            self.context).visit(node.right)

        is_string_mult = False

        if left_value_type == 'string' or right_value_type == 'string':
            if ((left_value_type == 'string')
                and (set(right_value_type) == INTEGER_TYPES)
                and isinstance(node.op, ast.Mult)):
                is_string_mult = True
            elif ((right_value_type == 'string')
                  and (set(left_value_type) == INTEGER_TYPES)
                  and isinstance(node.op, ast.Mult)):
                is_string_mult = True
            elif ((right_value_type == 'string')
                  and (left_value_type == 'string')
                  and isinstance(node.op, ast.Add)):
                pass
            else:
                raise CompileError('Bad string operation', node)
        else:
            left_value_type, right_value_type = intersection_of(
                left_value_type,
                right_value_type,
                node)

        left_value_type = reduce_type(left_value_type)
        right_value_type = reduce_type(right_value_type)
        left = self.visit_value_check_type(node.left, left_value_type)
        right = self.visit_value_check_type(node.right, right_value_type)

        if is_string_mult:
            self.context.mys_type = 'string'

        return format_binop(left, right, type(node.op))

    def visit_UnaryOp(self, node):
        operand = self.visit(node.operand)
        op = OPERATORS[type(node.op)]

        if isinstance(node.op, ast.Not):
            raise_if_not_bool(self.context.mys_type, node.operand, self.context)
        elif isinstance(node.op, (ast.UAdd, ast.USub)):
            if self.context.mys_type not in NUMBER_TYPES:
                raise CompileError(f"unary '{op}' can only operate on numbers",
                                   node)

        return f'{op}({operand})'

    def visit_AugAssign(self, node):
        lval = self.visit(node.target)
        lval = wrap_not_none(lval, self.context.mys_type)
        op = OPERATORS[type(node.op)]

        if is_primitive_type(self.context.mys_type):
            rval = self.visit_value_check_type(node.value, self.context.mys_type)
        else:
            rval = self.visit(node.value)

        return f'{lval} {op}= {rval};'

    def visit_Tuple(self, node):
        items = []
        mys_types = []

        for item in node.elts:
            items.append(self.visit(item))
            mys_types.append(self.context.mys_type)

        self.context.mys_type = tuple(mys_types)
        cpp_type = self.mys_to_cpp_type(self.context.mys_type)
        items = ', '.join(items)

        return make_shared(cpp_type[6:], items)

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
        item_cpp_type = self.mys_to_cpp_type(item_mys_type)

        return make_shared_list(item_cpp_type, value)

    def visit_Dict(self, node):
        key_mys_type = None
        keys = []

        for key_node in node.keys:
            keys.append(self.visit(key_node))

            if key_mys_type is not None:
                raise_if_wrong_visited_type(self.context, key_mys_type, key_node)

            if key_mys_type is None:
                key_mys_type = self.context.mys_type

        value_mys_type = None
        values = []

        for value_node in node.values:
            value = self.visit(value_node)
            values.append(value)

            if value_mys_type is not None:
                raise_if_wrong_visited_type(self.context, value_mys_type, value_node)

            if value_mys_type is None:
                value_mys_type = self.context.mys_type

        self.context.mys_type = {key_mys_type: value_mys_type}

        key_cpp_type = self.mys_to_cpp_type(key_mys_type)
        value_cpp_type = self.mys_to_cpp_type(value_mys_type)
        items = ', '.join([f'{{{key}, {value}}}' for key, value in zip(keys, values)])

        return make_shared_dict(key_cpp_type, value_cpp_type, items)

    def visit_for_list(self, node, value, mys_type):
        item_mys_type = mys_type[0]
        items = self.unique('items')
        i = self.unique('i')
        target_type = mys_type_to_target_cpp_type(item_mys_type)

        if isinstance(node.target, ast.Tuple):
            target = []

            for j, item in enumerate(node.target.elts):
                name = item.id

                if not name.startswith('_'):
                    self.context.define_local_variable(name, item_mys_type[j], item)
                    target.append(
                        f'    {target_type} {make_name(name)} = '
                        f'std::get<{j}>('
                        f'shared_ptr_not_none({items}->get({i}))->m_tuple);')

            target = '\n'.join(target)
        else:
            name = node.target.id

            if not name.startswith('_'):
                self.context.define_local_variable(name, item_mys_type, node.target)

            target = f'    {target_type} {name} = {items}->get({i});'

        body = indent('\n'.join([
            self.visit(item)
            for item in node.body
        ]))

        return [
            f'const auto& {items} = {value};',
            f'for (auto {i} = 0; {i} < {items}->__len__(); {i}++) {{',
            target,
            body,
            '}'
        ]

    def visit_for_dict(self, node, dvalue, mys_type):
        key_mys_type, value_mys_type = split_dict_mys_type(mys_type)
        items = self.unique('items')
        i = self.unique('i')

        if (not isinstance(node.target, ast.Tuple)
            or len(node.target.elts) != 2):
            raise CompileError(
                "iteration over dict must be done on key/value tuple",
                node.target)

        key = node.target.elts[0]
        key_name = key.id

        if not key_name.startswith('_'):
            self.context.define_local_variable(key_name, key_mys_type, key)

        value = node.target.elts[1]
        value_name = value.id

        if not value_name.startswith('_'):
            self.context.define_local_variable(value_name, value_mys_type, value)

        body = indent('\n'.join([
            self.visit(item)
            for item in node.body
        ]))

        return [
            f'const auto& {items} = {dvalue};',
            f'for (const auto& {i} : {items}->m_map) {{',
            f'    const auto& {make_name(key_name)} = {i}.first;',
            f'    const auto& {make_name(value_name)} = {i}.second;',
            body,
            '}'
        ]

    def visit_for_string(self, node, value):
        items = self.unique('items')
        i = self.unique('i')
        name = node.target.id

        if not name.startswith('_'):
            self.context.define_local_variable(name, 'char', node.target)

        target = f'    auto {name} = {items}.get({i});'
        body = indent('\n'.join([
            self.visit(item)
            for item in node.body
        ]))

        return [
            f'const auto& {items} = {value};',
            f'for (auto {i} = 0; {i} < {items}.__len__(); {i}++) {{',
            target,
            body,
            '}'
        ]

    def visit_iter_parameter(self, node, expected_mys_type=None):
        value = self.visit(node)
        mys_type = self.context.mys_type

        if mys_type not in INTEGER_TYPES:
            mys_type = format_mys_type(mys_type)

            raise CompileError(
                f"parameter type must be an integer, not '{mys_type}'",
                node)

        if expected_mys_type is not None and mys_type != expected_mys_type:
            raise_types_differs(mys_type, expected_mys_type, node)

        return value, mys_type

    def visit_for_call_range(self,
                             items,
                             target_value,
                             target_node,
                             iter_node,
                             nargs):
        if nargs == 1:
            begin = 0
            end, mys_type = self.visit_iter_parameter(iter_node.args[0], 'i64')
            step = 1
        elif nargs == 2:
            begin, mys_type = self.visit_iter_parameter(iter_node.args[0], 'i64')
            end, _ = self.visit_iter_parameter(iter_node.args[1], mys_type)
            step = 1
        elif nargs == 3:
            begin, mys_type = self.visit_iter_parameter(iter_node.args[0], 'i64')
            end, _ = self.visit_iter_parameter(iter_node.args[1], mys_type)
            step, _ = self.visit_iter_parameter(iter_node.args[2], mys_type)
        else:
            raise CompileError(f"expected 1 to 3 parameters, got {nargs}",
                               iter_node)

        items.append(Range(target_value, target_node, begin, end, step, mys_type))

    def visit_enumerate_parameter(self, node):
        value = self.visit(node)
        mys_type = self.context.mys_type

        if mys_type not in INTEGER_TYPES:
            raise CompileError(f"initial value must be an integer, not '{mys_type}'",
                               node)

        return value, mys_type

    def visit_for_call_enumerate(self,
                                 items,
                                 target_value,
                                 target_node,
                                 iter_node,
                                 nargs):
        actual_count = len(target_value)

        if actual_count != 2:
            raise CompileError(
                f"can only unpack enumerate into two variables, got {actual_count}",
                target_node)

        if nargs == 1:
            self.visit_for_call(items,
                                target_value[1],
                                iter_node.args[0])
            items.append(Enumerate(target_value[0][0], target_node, 0, 'i64'))
        elif nargs == 2:
            self.visit_for_call(items,
                                target_value[1],
                                iter_node.args[0])
            initial, mys_type = self.visit_enumerate_parameter(
                iter_node.args[1])
            items.append(Enumerate(target_value[0][0],
                                   target_node,
                                   initial,
                                   mys_type))
        else:
            raise CompileError(f"expected 1 or 2 parameters, got {nargs}",
                               iter_node)

    def visit_for_call_slice(self, items, target, iter_node, nargs):
        self.visit_for_call(items, target, iter_node.args[0])

        if nargs == 2:
            end, _ = self.visit_iter_parameter(iter_node.args[1], 'i64')
            items.append(OpenSlice(end))
        elif nargs == 3:
            begin, mys_type = self.visit_iter_parameter(iter_node.args[1], 'i64')
            end, _ = self.visit_iter_parameter(iter_node.args[2], mys_type)
            items.append(Slice(begin, end, 1))
        elif nargs == 4:
            begin, mys_type = self.visit_iter_parameter(iter_node.args[1], 'i64')
            end, _ = self.visit_iter_parameter(iter_node.args[2], mys_type)
            step, _ = self.visit_iter_parameter(iter_node.args[3], mys_type)
            items.append(Slice(begin, end, step))
        else:
            raise CompileError(f"expected 2 to 4 parameters, got {nargs}",
                               iter_node)

    def visit_for_call_zip(self, items, target_value, target_node, iter_node, nargs):
        if len(target_value) != nargs:
            raise CompileError(
                f"cannot unpack {nargs} values into {len(target_value)}",
                target_node)

        children = []

        for value, arg in zip(target_value, iter_node.args):
            items_2 = []
            self.visit_for_call(items_2, value, arg)
            children.append(items_2)

        items.append(Zip(children))

    def visit_for_call_reversed(self, items, target, iter_node, nargs):
        raise_if_wrong_number_of_parameters(nargs, 1, iter_node)
        self.visit_for_call(items, target, iter_node.args[0])
        items.append(Reversed())

    def visit_for_call_data(self, items, target_value, target_node, iter_node):
        iter_value = self.visit(iter_node)

        if self.context.mys_type == 'string':
            mys_type = 'char'
        else:
            mys_type = self.context.mys_type[0]

        items.append(Data(target_value, target_node, iter_value, mys_type))

    def visit_for_call(self, items, target, iter_node):
        target_value, target_node = target

        if isinstance(iter_node, ast.Call):
            if isinstance(iter_node.func, ast.Name):
                function_name = iter_node.func.id
                nargs = len(iter_node.args)

                if function_name == 'range':
                    self.visit_for_call_range(items,
                                              target_value,
                                              target_node,
                                              iter_node,
                                              nargs)
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
                    self.visit_for_call_data(items,
                                             target_value,
                                             target_node,
                                             iter_node)
            else:
                self.visit_for_call_data(items, target_value, target_node, iter_node)
        else:
            self.visit_for_call_data(items, target_value, target_node, iter_node)

    def visit_for_items_init(self, items):
        code = []

        for i, item in enumerate(items):
            if isinstance(item, Data):
                if item.mys_type == 'char':
                    op = '.'
                else:
                    op = '->'

                name = self.unique('data')
                code.append(f'const auto& {name}_object = {item.value};')
                code.append(f'auto {name} = Data({name}_object{op}__len__());')
            elif isinstance(item, Enumerate):
                name = self.unique('enumerate')
                prev_name = find_item_with_length(items).name
                code.append(f'auto {name} = Enumerate(i64({item.initial}),'
                            f' i64({prev_name}.length()));')
            elif isinstance(item, Range):
                name = self.unique('range')
                code.append(f'auto {name} = Range(i64({item.begin}), '
                            f'i64({item.end}), i64({item.step}));')
            elif isinstance(item, Slice):
                name = self.unique('slice')
                code.append(f'auto {name} = Slice(i64({item.begin}), i64({item.end}),'
                            f' i64({item.step}), i64({items[0].name}.length()));')

                for item_2 in items[:i]:
                    if not isinstance(item_2, (Slice, OpenSlice)):
                        code.append(f'{item_2.name}.slice({name});')
            elif isinstance(item, OpenSlice):
                name = self.unique('slice')
                code.append(f'auto {name} = OpenSlice(i64({item.begin}));')

                for item_2 in items[:i]:
                    if not isinstance(item_2, (Slice, OpenSlice, Zip, Reversed)):
                        code.append(f'{item_2.name}.slice({name});')
            elif isinstance(item, Reversed):
                for item_2 in items[:i]:
                    if not isinstance(item_2, (Slice, OpenSlice)):
                        code.append(f'{item_2.name}.reversed();')
            elif isinstance(item, Zip):
                names = []

                for items_2 in item.children:
                    code += self.visit_for_items_init(items_2)
                    names.append(find_item_with_length(items_2).name)

                first_child_name = names[0]
                name = self.unique('zip')
                code.append(f'auto {name} = {first_child_name}.length();')

                for child_name in names[1:]:
                    code.append(f'if ({name} != {child_name}.length()) {{')
                    code.append(
                        '    std::make_shared<ValueError>("can\'t zip different '
                        'lengths")->__throw();')
                    code.append('}')
            else:
                raise RuntimeError()

            item.name = name

        return code

    def visit_for_items_iter(self, items):
        code = []

        for item in items:
            if isinstance(item, (Slice, OpenSlice, Reversed)):
                pass
            elif isinstance(item, Zip):
                for items_2 in item.children:
                    code += self.visit_for_items_iter(items_2)
            else:
                code.append(f'{item.name}.iter();')

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

        raise Exception("no length")

    def visit_for_items_body(self, items):
        code = []

        for item in items[::-1]:
            if isinstance(item, Data):
                if isinstance(item.target, tuple):
                    for i, ((target, _), mys_type) in enumerate(zip(item.target,
                                                                    item.mys_type)):
                        target_type = mys_type_to_target_cpp_type(mys_type)
                        code.append(f'    {target_type} {make_name(target)} = '
                                    f'std::get<{i}>({item.name}_object->get('
                                    f'{item.name}.next())->m_tuple);')
                else:
                    target_type = mys_type_to_target_cpp_type(item.mys_type)

                    if item.mys_type == 'char':
                        op = '.'
                    else:
                        op = '->'

                    code.append(
                        f'    {target_type} {make_name(item.target)} = '
                        f'{item.name}_object{op}get({item.name}.next());')
            elif isinstance(item, (Slice, OpenSlice, Reversed)):
                continue
            elif isinstance(item, Zip):
                for items_2 in item.children:
                    code += self.visit_for_items_body(items_2)

                continue
            else:
                target_type = mys_type_to_target_cpp_type(item.mys_type)
                code.append(
                    f'    {target_type} {make_name(item.target)} = '
                    f'{item.name}.next();')

            if isinstance(item.target, tuple):
                for (target, node), mys_type in zip(item.target, item.mys_type):
                    if not target.startswith('_'):
                        self.context.define_local_variable(target, mys_type, node)
            else:
                if not item.target.startswith('_'):
                    self.context.define_local_variable(item.target,
                                                 item.mys_type,
                                                 item.target_node)

        return code

    def visit_For(self, node):
        if node.orelse:
            raise CompileError('for else clause not supported', node)

        self.context.push()

        if isinstance(node.iter, ast.Call):
            target = UnpackVisitor().visit(node.target)
            items = []
            self.visit_for_call(items, target, node.iter)
            code = self.visit_for_items_init(items)
            length = self.unique('len')
            item = self.visit_for_items_len_item(items)
            code.append(f'auto {length} = {item.name}.length();')
            code += self.visit_for_items_iter(items)
            i = self.unique('i')
            code.append(f'for (auto {i} = 0; {i} < {length}; {i}++) {{')
            code += self.visit_for_items_body(items)
            code += [
                indent(self.visit(item))
                for item in node.body
            ]
            code.append('}')
        else:
            value = self.visit(node.iter)
            mys_type = self.context.mys_type

            if isinstance(mys_type, list):
                code = self.visit_for_list(node, value, mys_type)
            elif isinstance(mys_type, dict):
                code = self.visit_for_dict(node, value, mys_type)
            elif isinstance(mys_type, tuple):
                raise CompileError('iteration over tuples not allowed',
                                   node.iter)
            elif mys_type == 'string':
                code = self.visit_for_string(node, value)
            else:
                raise CompileError(f'iteration over {mys_type} not supported',
                                   node.iter)

        self.context.pop()

        return '\n'.join(code)

    def visit_attribute_class(self, name, mys_type, value, node):
        definitions = self.context.get_class_definitions(mys_type)

        if name in definitions.members:
            self.context.mys_type = definitions.members[name].type
        else:
            raise CompileError(
                f"class '{mys_type}' has no member '{name}'",
                node)

        if value == 'self':
            value = 'this'
        elif is_private(name):
            raise CompileError(f"class '{mys_type}' member '{name}' is private",
                               node)

        return value

    def visit_Attribute(self, node):
        name = node.attr

        if isinstance(node.value, ast.Name):
            value = node.value.id

            if self.context.is_enum_defined(value):
                enum_type = self.context.get_enum_type(value)
                full_name = self.context.make_full_name(value)
                self.context.mys_type = full_name

                return f'({enum_type}){dot2ns(full_name)}::{name}'
            elif self.context.is_local_variable_defined(value):
                mys_type = self.context.get_local_variable_type(value)
            elif self.context.is_global_variable_defined(value):
                mys_type = self.context.get_global_variable_type(value)
                value = dot2ns(self.context.make_full_name(value))
            else:
                raise InternalError("attribute", node)
        else:
            value = self.visit(node.value)
            mys_type = self.context.mys_type

        if self.context.is_class_defined(mys_type):
            value = self.visit_attribute_class(name, mys_type, value, node)
        else:
            raise CompileError(f"'{mys_type}' has no member '{name}'", node)

        value = wrap_not_none(value, mys_type)

        return f'{value}->{make_name(node.attr)}'

    def create_constant(self, cpp_type, value):
        if value == 'nullptr':
            return value
        elif is_primitive_type(cpp_type):
            return value

        constant = self.context.constants.get(value)

        if constant is None:
            variable = self.unique('constant')
            self.context.constants[value] = (
                variable,
                f'static const {cpp_type} {variable} = {value};')
        else:
            variable = constant[0]

        return variable

    def visit_compare(self, node):
        if len(node.comparators) != 1:
            raise CompileError("can only compare two values", node)

        left_value_type = ValueTypeVisitor(self.source_lines,
                                           self.context).visit(node.left)
        right_value_type = ValueTypeVisitor(self.source_lines,
                                            self.context).visit(node.comparators[0])

        if isinstance(node.ops[0], (ast.In, ast.NotIn)):
            if isinstance(right_value_type, Dict):
                left_value_type, right_key_value_type = intersection_of(
                    left_value_type,
                    right_value_type.key_type,
                    node)
                right_value_type = Dict(right_key_value_type,
                                        right_value_type.value_type)
            elif isinstance(right_value_type, list) and len(right_value_type) == 1:
                left_value_type, right_value_type = intersection_of(
                    left_value_type,
                    right_value_type[0],
                    node)
                right_value_type = [right_value_type]
            else:
                raise CompileError("not an iterable", node.comparators[0])
        else:
            if not isinstance(node.ops[0], (ast.Is, ast.IsNot)):
                if left_value_type is None or right_value_type is None:
                    raise CompileError("use 'is' and 'is not' to compare to None",
                                       node)

            left_value_type, right_value_type = intersection_of(
                    left_value_type,
                    right_value_type,
                    node)

        left_value_type = reduce_type(left_value_type)
        right_value_type = reduce_type(right_value_type)

        left_value = self.visit_value_check_type(node.left, left_value_type)
        right_value = self.visit_value_check_type(node.comparators[0],
                                                  right_value_type)

        if is_constant(node.left):
            left_value = self.create_constant(
                mys_to_cpp_type(left_value_type, self.context),
                left_value)

        if is_constant(node.comparators[0]):
            right_value = self.create_constant(
                mys_to_cpp_type(right_value_type, self.context),
                right_value)

        items = [
            (left_value_type, left_value),
            (right_value_type, right_value)
        ]

        return items, [type(op) for op in node.ops]

    def visit_Compare(self, node):
        items, ops = self.visit_compare(node)
        left_mys_type, left = items[0]
        right_mys_type, right = items[1]
        op_class = ops[0]
        self.context.mys_type = 'bool'

        if op_class == ast.In:
            return f'Bool(contains({left}, {right}))'
        elif op_class == ast.NotIn:
            return f'Bool(!contains({left}, {right}))'
        elif op_class == ast.Is:
            left, right = compare_is_variables(left,
                                               left_mys_type,
                                               right,
                                               right_mys_type)

            return f'Bool(is({left}, {right}))'
        elif op_class == ast.IsNot:
            left, right = compare_is_variables(left,
                                               left_mys_type,
                                               right,
                                               right_mys_type)

            return f'Bool(!is({left}, {right}))'
        else:
            if left_mys_type != right_mys_type:
                raise CompileError(
                    f"cannot compare '{left_mys_type}' and '{right_mys_type}'",
                    node)

            return f'Bool({left} {OPERATORS[op_class]} {right})'

    def variables_code(self, variables, node):
        before = []
        per_branch = []
        after = []

        for name, info in variables.defined().items():
            self.context.define_local_variable(name, info, node)
            variable_name = self.unique(name)
            cpp_type = mys_to_cpp_type(info, self.context)
            before.append(f'{cpp_type} {variable_name};')
            per_branch.append(f'    {variable_name} = {make_name(name)};')
            after.append(f'auto {make_name(name)} = {variable_name};')

        return (before, per_branch, after)

    def visit_If(self, node):
        variables = Variables()
        cond = self.visit(node.test)
        raise_if_not_bool(self.context.mys_type, node.test, self.context)

        self.context.push()
        body = indent('\n'.join([
            self.visit(item)
            for item in node.body
        ]))
        state = self.context.pop()
        raises = state.raises

        if not state.raises:
            variables.add_branch(state.variables)

        self.context.push()
        orelse = indent('\n'.join([self.visit(item) for item in node.orelse]))
        state = self.context.pop()
        branch_variables = state.variables
        self.context.set_always_raises(raises and state.raises)

        if not state.raises:
            variables.add_branch(branch_variables)

        code, per_branch, after = self.variables_code(variables, node)
        code += [f'if ({cond}) {{', body] + ([] if raises else per_branch)

        if orelse:
            code += [
                '} else {',
                orelse
            ] + ([] if state.raises else per_branch) + [
                '}'
            ]
        else:
            code += ['}']

        code += after

        return '\n'.join(code)

    def visit_return_none(self, node):
        if self.context.return_mys_type is not None:
            raise CompileError("return value missing", node)

        self.context.mys_type = None

        return 'return;'

    def visit_return_value(self, node):
        if self.context.return_mys_type is None:
            raise CompileError("function does not return any value", node.value)

        value = self.visit_value_check_type(node.value,
                                            self.context.return_mys_type)

        return f'return {value};'

    def visit_Return(self, node):
        if node.value is None:
            return self.visit_return_none(node)
        else:
            return self.visit_return_value(node)

    def visit_Try(self, node):
        variables = Variables()
        self.context.push()
        body = indent('\n'.join([self.visit(item) for item in node.body]))
        try_variables = self.context.pop().variables
        variables.add_branch(try_variables)
        success_variable = self.unique('success')
        or_else_body = ''
        or_else_before = ''

        if node.orelse:
            body += '\n'
            body += f'    {success_variable} = true;'
            self.context.push()

            for variable_name, variable_mys_type in try_variables.items():
                unique_variable_name = self.unique(variable_name)
                cpp_type = self.mys_to_cpp_type(variable_mys_type)
                body += f'\n    {unique_variable_name} = {variable_name};'
                or_else_before += f'{cpp_type} {unique_variable_name};\n'
                or_else_body += '\n'
                or_else_body += f'auto {variable_name} = {unique_variable_name};\n'
                self.context.define_local_variable(variable_name,
                                                   variable_mys_type,
                                                   node)

            or_else_body += '\n'.join([self.visit(item) for item in node.orelse])
            variables.add_branch(self.context.pop().variables)

        self.context.push()
        finalbody = indent(
            '\n'.join([self.visit(item) for item in node.finalbody]))
        _finalbody_variables = self.context.pop().variables
        handlers = []

        for handler in node.handlers:
            if handler.type is None:
                exception = '__Error'
            else:
                exception = f'__{handler.type.id}'

            self.context.push()

            temp = self.unique('e')
            variable = ''

            if handler.name is not None:
                full_name = self.context.make_full_name(handler.type.id)

                if exception == '__Error':
                    variable = f'    const auto& {handler.name} = {temp}.m_error;'
                else:
                    variable = (
                        f'    const auto& {handler.name} = std::dynamic_pointer_cast'
                        f'<{dot2ns(full_name)}>({temp}.m_error);')

                self.context.define_local_variable(handler.name, full_name, node)

            handlers.append('\n'.join([
                f'}} catch (const {exception}& {temp}) {{',
                variable,
                indent('\n'.join([self.visit(item) for item in handler.body]))
            ]))
            variables.add_branch(self.context.pop().variables)

        before, per_branch, after = self.variables_code(variables, node)
        code = '\n'.join(before)
        code += or_else_before

        if code:
            code += '\n'

        if handlers:
            if per_branch:
                after_handler = '\n' + '\n'.join(per_branch)
            else:
                after_handler = ''

            code += '\n'.join([
                'try {',
                body
            ] + per_branch + [
                '\n'.join([handler + after_handler for handler in handlers]),
                '}'
            ])

            if or_else_body:
                code = f'bool {success_variable} = false;\n' + code
                code += '\n'.join([
                    f'\nif ({success_variable}) {{',
                    indent(or_else_body)
                ] + per_branch + [
                    '}\n'
                ])
        else:
            code = '\n'.join([dedent(body)] + per_branch)

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

        if after:
            code += '\n'
            code += '\n'.join(after)

        return code

    def visit_Raise(self, node):
        self.context.set_always_raises(True)

        if node.exc is None:
            return 'throw;'
        else:
            exception = self.visit(node.exc)
            mys_type = self.context.mys_type

            if mys_type in BUILTIN_ERRORS:
                pass
            elif mys_type == 'Error':
                pass
            elif self.context.is_class_defined(mys_type):
                definitions = self.context.get_class_definitions(mys_type)

                if 'Error' not in definitions.implements:
                    raise CompileError(
                        'errors must implement the Error trait',
                        node.exc)
            else:
                raise CompileError('errors must implement the Error trait', node.exc)

            return f'{exception}->__throw();'

    def visit_inferred_type_assign(self, node, target):
        value_type = ValueTypeVisitor(self.source_lines,
                                      self.context).visit(node.value)

        if value_type is None:
            raise CompileError("cannot infer type from None", node)
        elif isinstance(value_type, Dict):
            if value_type.key_type is None:
                raise CompileError("cannot infer type from empty dict", node)
        elif value_type == []:
            raise CompileError("cannot infer type from empty list", node)

        value_type = reduce_type(value_type)
        value = self.visit_value_check_type(node.value, value_type)
        self.context.define_local_variable(target, self.context.mys_type, node)

        return f'auto {make_name(target)} = {value};'

    def visit_assign_tuple_unpack(self, node, target):
        value = self.visit(node.value)
        mys_type = self.context.mys_type

        if not isinstance(mys_type, tuple):
            raise CompileError('only tuples can be unpacked', node.value)

        value_nargs = len(mys_type)
        target_nargs = len(target.elts)

        if value_nargs != target_nargs:
            raise CompileError(
                f'expected {target_nargs} values to unpack, got {value_nargs}',
                node)

        temp = self.unique('tuple')
        lines = [f'auto {temp} = {value};']

        for i, item in enumerate(target.elts):
            if isinstance(item, ast.Name):
                target = item.id

                if self.context.is_local_variable_defined(target):
                    raise_if_self(target, node)
                    target_mys_type = self.context.get_local_variable_type(target)
                    raise_if_wrong_types(mys_type[i],
                                         target_mys_type,
                                         item,
                                         self.context)
                else:
                    self.context.define_local_variable(target, mys_type[i], item)
                    target = f'auto {target}'
            else:
                target = self.visit(item)

            lines.append(f'{target} = std::get<{i}>({temp}->m_tuple);')

        return '\n'.join(lines)

    def visit_assign_variable(self, node, target):
        target = target.id

        if self.context.is_local_variable_defined(target):
            raise_if_self(target, node)
            target_mys_type = self.context.get_local_variable_type(target)
            value = self.visit_value_check_type(node.value, target_mys_type)
            code = f'{target} = {value};'
        elif self.context.is_global_variable_defined(target):
            target_mys_type = self.context.get_global_variable_type(target)
            value = self.visit_value_check_type(node.value, target_mys_type)
            code = f'{dot2ns(self.context.make_full_name(target))} = {value};'
        else:
            code = self.visit_inferred_type_assign(node, target)

        return code

    def visit_assign_subscript(self, node, target):
        base = self.visit(target.value)

        if isinstance(self.context.mys_type, dict):
            key_mys_type, value_mys_type = split_dict_mys_type(
                self.context.mys_type)
            key = self.visit_value_check_type(target.slice, key_mys_type)
            value = self.visit_value_check_type(node.value, value_mys_type)

            return f'shared_ptr_not_none({base})->__setitem__({key}, {value});'
        else:
            return self.visit_assign_other(node, target)

    def visit_assign_other(self, node, target):
        target = self.visit(target)
        target_mys_type = self.context.mys_type
        value = self.visit_value_check_type(node.value, target_mys_type)

        return f'{target} = {value};'

    def visit_Assign(self, node):
        target = node.targets[0]

        if isinstance(target, ast.Tuple):
            return self.visit_assign_tuple_unpack(node, target)
        elif isinstance(target, ast.Name):
            return self.visit_assign_variable(node, target)
        elif isinstance(target, ast.Subscript):
            return self.visit_assign_subscript(node, target)
        else:
            return self.visit_assign_other(node, target)

    def visit_subscript_tuple(self, node, value, mys_type):
        if not is_integer_literal(node.slice):
            raise CompileError(
                "tuple indexes must be compile time known integers",
                node.slice)

        index = make_integer_literal('i64', node.slice)

        try:
            index = int(index)
        except ValueError:
            raise CompileError(
                "tuple indexes must be compile time known integers",
                node.slice)

        if not (0 <= index < len(mys_type)):
            raise CompileError("tuple index out of range", node.slice)

        self.context.mys_type = mys_type[index]

        return f'std::get<{index}>({value}->m_tuple)'

    def visit_subscript_dict(self, node, value, mys_type):
        key_mys_type, value_mys_type = split_dict_mys_type(mys_type)
        key = self.visit_value_check_type(node.slice, key_mys_type)
        self.context.mys_type = value_mys_type

        return f'({value})->get({key})'

    def visit_subscript_list(self, node, value, mys_type):
        index = self.visit(node.slice)
        self.context.mys_type = mys_type[0]

        return f'{value}->get({index})'

    def visit_subscript_string(self, node, value):
        index = self.visit(node.slice)
        self.context.mys_type = 'char'

        if isinstance(index, tuple):
            self.context.mys_type = 'string'
            opt = ", ".join(i if i is not None else "std::nullopt" for i in index)
            return f'{value}.get({opt})'
        else:
            return f'{value}.get({index})'

    def visit_subscript_bytes(self, node, value):
        index = self.visit(node.slice)
        self.context.mys_type = 'u8'

        return f'{value}[{index}]'

    def visit_Subscript(self, node):
        value = self.visit(node.value)
        mys_type = self.context.mys_type
        value = wrap_not_none(value, mys_type)

        if isinstance(mys_type, tuple):
            return self.visit_subscript_tuple(node, value, mys_type)
        elif isinstance(mys_type, dict):
            return self.visit_subscript_dict(node, value, mys_type)
        elif isinstance(mys_type, list):
            return self.visit_subscript_list(node, value, mys_type)
        elif mys_type == 'string':
            return self.visit_subscript_string(node, value)
        elif mys_type == 'bytes':
            return self.visit_subscript_bytes(node, value)
        else:
            raise CompileError("subscript of this type is not yet implemented",
                               node)

    def visit_value_check_type_tuple(self, node, mys_type):
        if not isinstance(mys_type, tuple):
            mys_type = format_mys_type(mys_type)

            raise CompileError(f"cannot convert tuple to '{mys_type}'", node)

        values = []
        types = []

        for i, item in enumerate(node.elts):
            values.append(self.visit_value_check_type(item, mys_type[i]))
            types.append(self.context.mys_type)

        raise_if_wrong_types(tuple(types), mys_type, node, self.context)
        self.context.mys_type = mys_type
        cpp_type = self.mys_to_cpp_type(mys_type)
        values = ", ".join(values)

        return make_shared(cpp_type[6:], values)

    def visit_value_check_type_list(self, node, mys_type):
        if not isinstance(mys_type, list):
            mys_type = format_mys_type(mys_type)

            raise CompileError(f"cannot convert list to '{mys_type}'", node)

        values = []
        item_mys_type = mys_type[0]

        for item in node.elts:
            values.append(self.visit_value_check_type(item, item_mys_type))

        self.context.mys_type = mys_type
        value = ", ".join(values)
        item_cpp_type = self.mys_to_cpp_type(item_mys_type)

        return make_shared_list(item_cpp_type, value)

    def visit_value_check_type_dict(self, node, mys_type):
        if not isinstance(mys_type, dict):
            mys_type = format_mys_type(mys_type)

            raise CompileError(f"cannot convert dict to '{mys_type}'", node)

        key_mys_type, value_mys_type = split_dict_mys_type(mys_type)

        if not is_allowed_dict_key_type(key_mys_type):
            raise CompileError("invalid key type", node)

        keys = []
        values = []

        for key, value in zip(node.keys, node.values):
            keys.append(self.visit_value_check_type(key, key_mys_type))
            values.append(self.visit_value_check_type(value, value_mys_type))

        self.context.mys_type = mys_type
        items = ", ".join([f'{{{key}, {value}}}' for key, value in zip(keys, values)])
        key_cpp_type = self.mys_to_cpp_type(key_mys_type)
        value_cpp_type = self.mys_to_cpp_type(value_mys_type)

        return make_shared_dict(key_cpp_type, value_cpp_type, items)

    def visit_value_check_type_list_comp(self, node, mys_type):
        return ListComprehension(node, mys_type, self).generate()

    def visit_value_check_type_dict_comp(self, node, mys_type):
        return DictComprehension(node, mys_type, self).generate()

    def visit_value_check_type_other(self, node, mys_type):
        value = self.visit(node)

        if self.context.is_trait_defined(mys_type):
            if self.context.is_class_defined(self.context.mys_type):
                definitions = self.context.get_class_definitions(
                    self.context.mys_type)

                if mys_type not in definitions.implements:
                    trait_type = format_mys_type(mys_type)
                    class_type = self.context.mys_type

                    raise CompileError(
                        f"'{class_type}' does not implement trait '{trait_type}'",
                        node)
        else:
            raise_if_wrong_visited_type(self.context, mys_type, node)

        return value

    def visit_value_check_type(self, node, mys_type):
        if is_integer_literal(node):
            value = make_integer_literal(mys_type, node)
            self.context.mys_type = mys_type
        elif is_float_literal(node):
            value = make_float_literal(mys_type, node)
            self.context.mys_type = mys_type
        elif isinstance(node, ast.Tuple):
            value = self.visit_value_check_type_tuple(node, mys_type)
        elif isinstance(node, ast.List):
            value = self.visit_value_check_type_list(node, mys_type)
        elif isinstance(node, ast.Dict):
            value = self.visit_value_check_type_dict(node, mys_type)
        elif isinstance(node, ast.ListComp):
            value = self.visit_value_check_type_list_comp(node, mys_type)
        elif isinstance(node, ast.DictComp):
            value = self.visit_value_check_type_dict_comp(node, mys_type)
        elif is_constant(node):
            value = self.visit(node)

            if self.context.mys_type is None:
                if not is_primitive_type(mys_type):
                    self.context.mys_type = mys_type

            raise_if_wrong_visited_type(self.context, mys_type, node)
        else:
            value = self.visit_value_check_type_other(node, mys_type)

        return value

    def visit_ann_assign(self, node):
        target = node.target.id

        if node.value is None:
            raise CompileError("variables must be initialized when declared", node)

        mys_type = TypeVisitor(self.context).visit(node.annotation)

        if not self.context.is_type_defined(mys_type):
            mys_type = format_mys_type(mys_type)

            raise CompileError(f"undefined type '{mys_type}'", node.annotation)

        code = self.visit_value_check_type(node.value, mys_type)
        cpp_type = self.mys_to_cpp_type(mys_type)

        return target, mys_type, cpp_type, make_name(target), code

    def visit_AnnAssign(self, node):
        target, mys_type, cpp_type, cpp_target, code = self.visit_ann_assign(node)
        self.context.define_local_variable(target, mys_type, node.target)
        code = f'{cpp_type} {cpp_target} = {code};'

        return code

    def visit_While(self, node):
        if node.orelse:
            raise CompileError('while else clause not supported', node)

        condition = self.visit(node.test)
        raise_if_not_bool(self.context.mys_type, node.test, self.context)
        self.context.push()
        body = indent('\n'.join([self.visit(item) for item in node.body]))
        self.context.pop()

        return '\n'.join([
            f'while ({condition}) {{',
            body,
            '}'
        ])

    def visit_Pass(self, _node):
        return ''

    def visit_Break(self, _node):
        return 'break;'

    def visit_Continue(self, _node):
        return 'continue;'

    def visit_assert_compare(self, node, prepare):
        items, ops = self.visit_compare(node.test)
        variables = []

        for mys_type, value in items:
            variable = self.unique('var')
            cpp_type = self.mys_to_cpp_type(mys_type)
            prepare.append(f'const {cpp_type} {variable} = {value};')
            variables.append((variable, mys_type))

        conds = []
        message = []

        for i, op_class in enumerate(ops):
            message.append(format_assert_str(*variables[i], self.context))

            if op_class == ast.In:
                conds.append(
                    f'contains({variables[i][0]}, {variables[i + 1][0]})')
                message.append('" in "')
            elif op_class == ast.NotIn:
                conds.append(
                    f'!contains({variables[i][0]}, {variables[i + 1][0]})')
                message.append('" not in "')
            elif op_class == ast.Is:
                variable_1, variable_2 = compare_assert_is_variables(
                    variables[i],
                    variables[i + 1])
                conds.append(f'is({variable_1}, {variable_2})')
                message.append('" is "')
            elif op_class == ast.IsNot:
                variable_1, variable_2 = compare_assert_is_variables(
                    variables[i],
                    variables[i + 1])
                conds.append(f'!is({variable_1}, {variable_2})')
                message.append('" is not "')
            else:
                op = OPERATORS[op_class]
                conds.append(f'({variables[i][0]} {op} {variables[i + 1][0]})')
                message.append(f'" {op} "')

        message.append(f'{format_assert_str(*variables[-1], self.context)}')
        cond = ' && '.join(conds)
        message = ' + '.join(message)

        return cond, message

    def visit_Assert(self, node):
        prepare = []

        if isinstance(node.test, ast.Compare):
            cond, message = self.visit_assert_compare(node, prepare)
        else:
            cond = self.visit(node.test)
            message = 'String("todo")'

        filename = self.filename
        line = node.lineno

        return '\n'.join([
            '#if defined(MYS_TEST) || !defined(NDEBUG)'
        ] + prepare + [
            f'if (!({cond})) {{',
            f'    std::cout << "{filename}:{line}: assert " << '
            f'PrintString({message}) << " is not true" << std::endl;',
            f'    std::make_shared<AssertionError>({message} + " is not true")'
            '->__throw();',
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
        raise CompileError('lambda functions are not supported', node)

    def visit_Import(self, node):
        raise CompileError('imports are only allowed on module level', node)

    def visit_ImportFrom(self, node):
        raise CompileError('imports are only allowed on module level', node)

    def visit_ClassDef(self, node):
        raise CompileError('class definitions are only allowed on module level',
                           node)

    def visit_JoinedStr(self, node):
        if node.values:
            return ' + '.join([
                self.visit(value)
                for value in node.values
            ])
        else:
            return '""'

    def visit_FormattedValue(self, node):
        value = self.visit(node.value)
        value = format_arg((value, self.context.mys_type))
        value = format_str(value, self.context.mys_type, self.context)
        self.context.mys_type = 'string'

        return value

    def visit_BoolOp(self, node):
        values = []

        for value in node.values:
            values.append(self.visit(value))

            if self.context.mys_type is None:
                raise CompileError("None is not a 'bool'", value)
            else:
                raise_if_not_bool(self.context.mys_type, value, self.context)

        op = BOOL_OPS[type(node.op)]

        return '((' + f') {op} ('.join(values) + '))'

    def visit_trait_match(self, subject_variable, node):
        cases = []

        for case in node.cases:
            if case.guard is not None:
                raise CompileError("guards are not supported", case.guard)

            casted = self.unique('casted')

            if isinstance(case.pattern, ast.Call):
                class_name = case.pattern.func.id
                cases.append(
                    f'const auto& {casted} = '
                    f'std::dynamic_pointer_cast<{class_name}>({subject_variable});\n'
                    f'if ({casted}) {{\n' +
                    indent('\n'.join([self.visit(item) for item in case.body])) +
                    '\n}')
            elif isinstance(case.pattern, ast.MatchAs):
                if isinstance(case.pattern.pattern, ast.Call):
                    class_name = case.pattern.pattern.func.id
                    self.context.push()
                    self.context.define_local_variable(case.pattern.name,
                                                       class_name, case)
                    cases.append(
                        f'const auto& {casted} = '
                        f'std::dynamic_pointer_cast<{class_name}>('
                        f'{subject_variable});\n'
                        f'if ({casted}) {{\n'
                        f'    const auto& {case.pattern.name} = '
                        f'std::move({casted});\n' +
                        indent('\n'.join([self.visit(item) for item in case.body])) +
                        '\n}')
                    self.context.pop()
                else:
                    raise CompileError('trait match patterns must be class objects',
                                       case.pattern)
            elif isinstance(case.pattern, ast.Name):
                if case.pattern.id == '_':
                    cases.append('\n'.join([self.visit(item) for item in case.body]))
                else:
                    raise CompileError('trait match patterns must be class objects',
                                       case.pattern)
            else:
                raise CompileError('trait match patterns must be classes',
                                   case.pattern)

        body = ''

        for case in cases[1:][::-1]:
            body = ' else {\n' + indent(case + body) + '\n}'

        return cases[0] + body

    def visit_other_match(self, subject_variable, subject_mys_type, node):
        cases = []

        for case in node.cases:
            if case.guard is not None:
                raise CompileError("guards are not supported", case.guard)

            if isinstance(case.pattern, ast.Name):
                if case.pattern.id != '_':
                    raise CompileError("cannot match variables", case.pattern)

                pattern = '_'
            else:
                pattern = self.visit_value_check_type(case.pattern, subject_mys_type)

                if subject_mys_type == 'string':
                    pattern = self.create_constant('String', pattern)

            body = indent('\n'.join([self.visit(item) for item in case.body]))

            if pattern == '_':
                cases.append('{\n' + body + '\n}')
            else:
                cases.append(f'if ({subject_variable} == {pattern}) {{\n'
                             + body
                             + '\n}')

        return ' else '.join(cases)

    def visit_Match(self, node):
        subject_variable = self.unique('subject')
        code = f'const auto& {subject_variable} = {self.visit(node.subject)};\n'
        subject_mys_type = self.context.mys_type

        if self.context.is_trait_defined(subject_mys_type):
            code += self.visit_trait_match(subject_variable, node)
        elif self.context.is_class_defined(subject_mys_type):
            raise CompileError("matching classes if not supported", node.subject)
        else:
            code += self.visit_other_match(subject_variable, subject_mys_type, node)

        return code

    def visit_IfExp(self, node):
        test = self.visit(node.test)
        raise_if_not_bool(self.context.mys_type, node.test, self.context)
        body = self.visit(node.body)
        body_type = self.context.mys_type
        orelse = self.visit(node.orelse)
        orelse_type = self.context.mys_type
        raise_if_wrong_types(orelse_type, body_type, node.orelse, self.context)

        return f'(({test}) ? ({body}) : ({orelse}))'

    def visit_ListComp(self, node):
        value_type = ValueTypeVisitor(self.source_lines, self.context).visit(node)
        value_type = reduce_type(value_type)

        return self.visit_value_check_type(node, value_type)

    def visit_DictComp(self, node):
        value_type = ValueTypeVisitor(self.source_lines, self.context).visit(node)
        value_type = reduce_type(value_type)

        return self.visit_value_check_type(node, value_type)

    def visit_SetComp(self, node):
        raise CompileError("set comprehension is not implemented", node)

    def visit_Slice(self, node):
        lower = None
        upper = None
        step = '1'

        if node.lower:
            lower = self.visit(node.lower)

        if node.upper:
            upper = self.visit(node.upper)

        if node.step:
            step = self.visit(node.step)

        return lower, upper, step

    def generic_visit(self, node):
        raise InternalError("unhandled node", node)
