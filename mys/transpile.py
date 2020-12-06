import traceback
import textwrap
from pathlib import Path
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexer import RegexLexer
from pygments.lexer import bygroups
from pygments.lexer import using
from pygments.lexers import PythonLexer
from pygments.style import Style
from pygments.token import Text
from pygments.token import Name
from pygments.token import Number
from pygments.token import Generic
from .parser import ast
from .utils import LanguageError
from .utils import is_snake_case
from .utils import TypeVisitor
from .utils import is_integer_literal
from .utils import is_float_literal
from .utils import make_integer_literal
from .utils import make_float_literal
from .utils import BOOL_OPS
from .utils import OPERATORS
from .utils import PRIMITIVE_TYPES
from .utils import INTEGER_TYPES
from .definitions import find_definitions
from .definitions import is_method

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

class Context:

    def __init__(self):
        self._stack = [[]]
        self._variables = {}
        self._classes = {}
        self._traits = {}
        self._functions = {}
        self._enums = {}
        # The return C++ type of the current function.
        self.return_cpp_type = None
        # The C++ type of the current object.
        self.cpp_type = None

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

    def define_function(self, name, return_type):
        self._functions[name] = return_type

    def is_function_defined(self, name):
        return name in self._functions

    def get_function_return_type(self, name):
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

def is_docstring(node, source_lines):
    if not isinstance(node, ast.Constant):
        return False

    if not isinstance(node.value, str):
        return False

    if not is_string(node, source_lines):
        return False

    return not node.value.startswith('mys-embedded-c++')

def has_docstring(node, source_lines):
    first = node.body[0]

    if isinstance(first, ast.Expr):
        return is_docstring(first.value, source_lines)

    return False

def handle_string_node(node, value, source_lines):
    if is_string(node, source_lines):
        return handle_string(value)
    else:
        raise LanguageError('character literals are not yet supported',
                            node.lineno,
                            node.col_offset)

class BaseVisitor(ast.NodeVisitor):

    def __init__(self, source_lines, context, filename):
        self.source_lines = source_lines
        self.context = context
        self.filename = filename

    def return_type_string(self, node):
        return return_type_string(node,
                                  self.source_lines,
                                  self.context,
                                  self.filename)

    def visit_Name(self, node):
        if self.context.is_variable_defined(node.id):
            self.context.cpp_type = self.context.get_variable_type(node.id)

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

        self.context.cpp_type = None

        return code

    def is_class_or_trait_defined(self, type_string):
        if self.context.is_class_defined(type_string):
            return True

        if self.context.is_trait_defined(type_string):
            return True

        return False

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if self.context.is_function_defined(node.func.id):
                # print('Func:', node.func.id)
                pass
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
            #       self.context.cpp_type,
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
                self.context.cpp_type = node.func.id

                return f'std::make_shared<{node.func.id}>({args})'

        if function_name == 'print':
            code = self.handle_print(node, args)
        else:
            if function_name in INTEGER_TYPES:
                self.context.cpp_type = function_name

            args = ', '.join(args)
            code = f'{function_name}({args})'

        return code

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            self.context.cpp_type = 'String'

            return handle_string_node(node, node.value, self.source_lines)
        elif isinstance(node.value, bool):
            self.context.cpp_type = 'bool'

            return 'true' if node.value else 'false'
        elif isinstance(node.value, float):
            self.context.cpp_type = 'f64'

            return f'{node.value}'
        elif isinstance(node.value, int):
            self.context.cpp_type = 'i64'

            return str(node.value)
        else:
            raise LanguageError("internal error",
                                node.lineno,
                                node.col_offset)

    def visit_Expr(self, node):
        return self.visit(node.value) + ';'

    def visit_BinOp(self, node):
        is_left_literal = is_integer_literal(node.left)
        is_right_literal = is_integer_literal(node.right)
        op_class = type(node.op)

        if is_left_literal and not is_right_literal:
            right = self.visit(node.right)
            right_type = self.context.cpp_type

            if isinstance(node.right, ast.Name):
                if not self.context.is_variable_defined(node.right.id):
                    raise LanguageError(
                        f"undefined variable '{node.right.id}'",
                        node.right.lineno,
                        node.right.col_offset)

            if self.context.cpp_type in INTEGER_TYPES:
                left_type = self.context.cpp_type
                left = make_integer_literal(left_type, node.left)
            else:
                left = self.visit(node.left)
                left_type = self.context.cpp_type
        elif not is_left_literal and is_right_literal:
            left = self.visit(node.left)
            left_type = self.context.cpp_type

            if isinstance(node.left, ast.Name):
                if not self.context.is_variable_defined(node.left.id):
                    raise LanguageError(
                        f"undefined variable '{node.left.id}'",
                        node.left.lineno,
                        node.left.col_offset)

            if self.context.cpp_type in INTEGER_TYPES:
                right_type = self.context.cpp_type
                right = make_integer_literal(right_type, node.right)
            else:
                right = self.visit(node.right)
                right_type = self.context.cpp_type
        else:
            left = self.visit(node.left)
            left_type = self.context.cpp_type
            right = self.visit(node.right)
            right_type = self.context.cpp_type

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

        # ToDo
        # if left_type != right_type:
        #     raise LanguageError(
        #         f"can't compare '{left_type}' and '{right_type}'\n",
        #         node.lineno,
        #         node.col_offset)

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
        types = []

        for item in node.elts:
            items.append(self.visit(item))
            types.append(self.context.cpp_type)

        self.context.cpp_type = tuple(types)

        return f'Tuple<{", ".join(types)}>({{{", ".join(items)}}})'

    def visit_List(self, node):
        items = []
        type_ = None

        for item in node.elts:
            items.append(self.visit(item))

            if type_ is None:
                type_ = self.context.cpp_type

        if type_ is None:
            self.context.cpp_type = None
        else:
            self.context.cpp_type = [type_]

        return f'List<todo>({{{", ".join(items)}}})'

    def visit_Dict(self, node):
        key = self.visit(node.keys[0])
        key_type = self.context.cpp_type
        value_type = None

        for value in node.values:
            value = self.visit(value)

            if value_type is None:
                value_type = self.context.cpp_type

        self.context.cpp_type = {key_type: value_type}

        return 'std::make_shared<Dict<todo>>({})'

    def visit_For(self, node):
        self.context.push()
        func = self.visit(node.iter)

        if isinstance(node.target, ast.Tuple):
            items = []

            for i, item in enumerate(node.target.elts):
                name = item.id

                if name.startswith('_'):
                    name = f'_{id(item)}'
                else:
                    self.context.define_variable(name,
                                                 self.context.cpp_type[i],
                                                 item)

                items.append(name)

            items = ', '.join(items)
            target = f'[{items}]'
        else:
            target = node.target.id

            if target.startswith('_'):
                target = f'_{id(node.target)}'
            else:
                type_ = self.context.cpp_type

                if isinstance(type_, list):
                    type_ = type_[0]

                self.context.define_variable(target, type_, node.target)

        body = indent('\n'.join([
            self.visit(item)
            for item in node.body
        ]))
        self.context.pop()

        return '\n'.join([
            f'for (auto {target}: {func}) {{',
            body,
            '}'
        ])

    def visit_Attribute(self, node):
        value = self.visit(node.value)

        if self.context.is_enum_defined(value):
            enum_type = self.context.get_enum_type(value)
            self.context.cpp_type = enum_type

            return f'({enum_type}){value}::{node.attr}'
        else:
            if value == 'self':
                value = 'this'

            return f'{value}->{node.attr}'

    def visit_compare(self, node):
        value_nodes = [node.left] + node.comparators
        items = []
        cpp_type = None

        for value_node in value_nodes:
            if is_integer_literal(value_node):
                items.append(('integer', value_node))
            elif is_float_literal(value_node):
                items.append(('float', value_node))
            else:
                value = self.visit(value_node)

                if cpp_type is None:
                    cpp_type = self.context.cpp_type

                if self.context.cpp_type != cpp_type:
                    raise LanguageError(
                        f"can't compare '{self.context.cpp_type}' and '{cpp_type}'\n",
                        value_node.lineno,
                        value_node.col_offset)

                items.append((cpp_type, value))

        values = []

        for value_cpp_type, value in items:
            if value_cpp_type == 'integer':
                values.append(make_integer_literal(cpp_type, value))
            elif value_cpp_type == 'float':
                values.append(make_float_literal(cpp_type, value))
            else:
                values.append(value)

        return cpp_type, values, [type(op) for op in node.ops]

    def visit_Compare(self, node):
        cpp_type, values, ops = self.visit_compare(node)

        if len(values) != 2:
            raise LanguageError("can only compare two values",
                                node.lineno,
                                node.col_offset)

        left = values[0]
        left_type = cpp_type
        right = values[1]
        right_type = cpp_type
        op_class = ops[0]

        if op_class == ast.In:
            return f'contains({left}, {right})'
        elif op_class == ast.NotIn:
            return f'!contains({left}, {right})'
        else:
            if left_type != right_type:
                raise LanguageError(
                    f"can't compare '{left_type}' and '{right_type}'\n",
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

    def visit_Return(self, node):
        value = self.visit(node.value)
        actual = self.context.cpp_type
        expected = self.context.return_cpp_type

        if actual != expected:
            if False:
                raise LanguageError(
                    f"returning '{actual}' from a function with return "
                    f"type '{expected}'\n",
                    node.value.lineno,
                    node.value.col_offset)

        if isinstance(node.value, ast.Name):
            if not self.context.is_variable_defined(value):
                raise LanguageError(
                    f"undefined variable '{value}'",
                    node.value.lineno,
                    node.value.col_offset)

        return f'return {value};'

    def visit_Try(self, node):
        body = indent('\n'.join([self.visit(item) for item in node.body]))
        success_variable = f'success_{id(node)}'
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
            self.context.cpp_type = 'i64'
            cpp_type = 'i64'
            value = make_integer_literal('i64', node.value)
        elif isinstance(node.value, ast.Constant):
            value = self.visit(node.value)
            cpp_type = self.context.cpp_type

            if cpp_type == 'String':
                value = f'String({value})'
        elif isinstance(node.value, ast.UnaryOp):
            value = self.visit(node.value)
            cpp_type = self.context.cpp_type
        else:
            value = self.visit(node.value)
            cpp_type = 'auto'

        self.context.define_variable(target, self.context.cpp_type, node)

        return f'{cpp_type} {target} = {value};'

    def visit_Assign(self, node):
        target = node.targets[0]

        if isinstance(target, ast.Tuple):
            value = self.visit(node.value)
            temp = f'tuple_{id(node)}'
            lines = [f'auto {temp} = {value};']

            for i, item in enumerate(target.elts):
                name = self.visit(item)
                self.context.define_variable(name, None, item)
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
        index = self.visit(node.slice)

        return f'{value}->get({index})'

    def visit_value(self, node, cpp_type):
        if is_integer_literal(node):
            return make_integer_literal(cpp_type, node)
        elif is_float_literal(node):
            return make_float_literal(cpp_type, node)
        else:
            return self.visit(node)

    def visit_AnnAssign(self, node):
        if node.value is None:
            raise LanguageError(
                "variables must be initialized when declared",
                node.lineno,
                node.col_offset)

        target = node.target.id

        if isinstance(node.annotation, ast.List):
            cpp_type = CppTypeVisitor(self.source_lines,
                                      self.context,
                                      self.filename).visit(node.annotation.elts[0])

            if isinstance(node.value, ast.Name):
                value = self.visit(node.value)
            else:
                value = ', '.join([self.visit(item)
                                   for item in node.value.elts])
            self.context.define_variable(target, None, node.target)

            return (f'auto {target} = std::make_shared<List<{cpp_type}>>('
                    f'std::initializer_list<{cpp_type}>{{{value}}});')

        cpp_type = CppTypeVisitor(self.source_lines,
                                  self.context,
                                  self.filename).visit(node.annotation)
        value = self.visit_value(node.value, cpp_type)
        self.context.define_variable(target, cpp_type, node.target)

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
            cpp_type, values, ops = self.visit_compare(node.test)
            variables = []

            for i, value in enumerate(values):
                variable = f'var_{id(node) + i}'
                prepare.append(f'{cpp_type} {variable} = {value};')
                variables.append(variable)

            conds = []
            messages = []

            for i, op_class in enumerate(ops):
                op = OPERATORS[op_class]
                conds.append(f'({variables[i]} {op} {variables[i + 1]})')
                messages.append(f'{variables[i]} << " {op} " << {variables[i + 1]}')

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
        return type_name[0].isupper() and type_name != 'String'

    def is_class(self, type_name):
        return False

    def visit_trait_match(self, subject, code, node):
        cases = []

        for case in node.cases:
            casted = f'casted_{id(case)}'

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
            subject = f'subject_{id(node)}'
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

class HeaderVisitor(BaseVisitor):

    def __init__(self, namespace, module_levels, source_lines, definitions):
        super().__init__(source_lines, Context(), 'todo')
        self.namespace = namespace
        self.module_levels = module_levels
        self.imports = []
        self.other = []
        self.prefix = namespace.replace('::', '_').upper()
        self.traits = []
        self.functions = []
        self.variables = []

        for name in definitions.traits:
            self.context.define_trait(name)
            self.traits.append(f'class {name};')

        self.classes = []

        for name in definitions.classes:
            self.context.define_class(name)
            self.classes.append(f'class {name};')

        for enum in definitions.enums.values():
            self.context.define_enum(enum.name, enum.type)

        for functions in definitions.functions.values():
            for function in functions:
                self.functions += self.visit_function(function)

        for variable in definitions.variables.values():
            self.variables.append(self.visit_variable(variable))

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

        return '\n'.join([
            '// This file was generated by mys. DO NOT EDIT!!!',
            '',
            '#pragma once',
            '',
            '#include "mys.hpp"'
        ] + self.imports + [
            '',
            f'namespace {self.namespace}',
            '{' ,
            ''
        ] + self.traits
          + self.classes
          + self.variables
          + self.other
          + self.functions + [
              '',
              '}',
              ''
          ])

    def visit_Import(self, node):
        raise LanguageError('use from ... import ...',
                            node.lineno,
                            node.col_offset)

    def visit_ImportFrom(self, node):
        module, name, asname = get_import_from_info(node, self.module_levels)
        module_hpp = module.replace('.', '/')
        self.imports.append(f'#include "{module_hpp}.mys.hpp"')
        prefix = 'MYS_' + module.replace('.', '_').upper()
        self.other.append(f'{prefix}_{name.name}_IMPORT_AS({asname});')

    def visit_ClassDef(self, node):
        pass

    def visit_AnnAssign(self, node):
        pass

    def visit_FunctionDef(self, node):
        return

    def visit_variable(self, variable):
        cpp_type = CppTypeVisitor(self.source_lines,
                                  self.context,
                                  self.filename).visit(variable.node.annotation)

        return '\n'.join([
            f'extern {cpp_type} {variable.name};',
            f'#define {self.prefix}_{variable.name}_IMPORT_AS(__name__) \\',
            f'    static auto& __name__ = {self.namespace}::{variable.name};'
        ])

    def visit_function(self, function):
        self.context.push()
        return_type = self.return_type_string(function.node.returns)
        params = params_string(function.name,
                               function.node.args.args,
                               self.source_lines,
                               self.context,
                               function.node.args.defaults,
                               self.filename)
        self.context.pop()
        code = []

        if function.name != 'main' and not function.is_test:
            code.append(f'{return_type} {function.name}({params});')
            code.append('\n'.join([
                f'#define {self.prefix}_{function.name}_IMPORT_AS(__name__) \\',
                f'    constexpr auto __name__ = [] (auto &&...args) {{ \\',
                f'        return {self.namespace}::{function.name}(std::forward<'
                f'decltype(args)>(args)...); \\',
                f'    }};'
            ]))

        return code

def create_class_init(class_name, member_names, member_types, member_values):
    params = []
    body = []

    for member_name, member_type in zip(member_names, member_types):
        params.append(f'{member_type} {member_name}')
        body.append(f'this->{member_name} = {member_name};')

    params = ', '.join(params)
    body = '\n'.join(body)

    return '\n'.join([
        f'{class_name}({params})',
        '{',
        indent(body),
        '}'
    ])

def create_class_str(class_name, member_names):
    members = [f'ss << "{name}=" << this->{name}' for name in member_names]
    members = indent(' << ", ";\n'.join(members))

    if members:
        members += ';'

    return '\n'.join([
        'String __str__() const',
        '{',
        '    std::stringstream ss;',
        '',
        f'    ss << "{class_name}(";',
        members,
        '    ss << ")";',
        '',
        '    return String(ss.str().c_str());',
        '}'
    ])

class SourceVisitor(ast.NodeVisitor):

    def __init__(self,
                 module_levels,
                 module_hpp,
                 filename,
                 skip_tests,
                 namespace,
                 source_lines,
                 definitions,
                 module_definitions):
        self.module_levels = module_levels
        self.source_lines = source_lines
        self.module_hpp = module_hpp
        self.filename = filename
        self.skip_tests = skip_tests
        self.namespace = namespace
        self.forward_declarations = []
        self.add_package_main = False
        self.before_namespace = []
        self.context = Context()
        self.definitions = definitions
        self.module_definitions = module_definitions

    def visit_value(self, node, cpp_type):
        if is_integer_literal(node):
            return make_integer_literal(cpp_type, node)
        elif is_float_literal(node):
            return make_float_literal(cpp_type, node)
        else:
            return self.visit(node)

    def visit_Call(self, node):
        function_name = self.visit(node.func)
        args = []

        for arg in node.args:
            if isinstance(arg, ast.Name):
                if not self.context.is_variable_defined(arg.id):
                    raise LanguageError(
                        f"undefined variable '{arg.id}'",
                        arg.lineno,
                        arg.col_offset)

            args.append(self.visit_value(arg, 'i64'))

        if isinstance(node.func, ast.Name):
            if self.context.is_class_defined(node.func.id):
                args = ', '.join(args)
                self.context.cpp_type = node.func.id

                return f'std::make_shared<{node.func.id}>({args})'

        if function_name in INTEGER_TYPES:
            self.context.cpp_type = function_name

        args = ', '.join(args)
        code = f'{function_name}({args})'

        return code

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        op_class = type(node.op)

        if isinstance(node.left, ast.Name):
            self.context.define_global_variable(node.left.id, None, node.left)

        if isinstance(node.right, ast.Name):
            self.context.define_global_variable(node.right.id, None, node.right)

        if op_class == ast.Pow:
            return f'ipow({left}, {right})'
        else:
            op = OPERATORS[op_class]

            return f'({left} {op} {right})'

    def visit_Assign(self, node):
        pass

    def visit_AnnAssign(self, node):
        if node.value is None:
            raise LanguageError(
                "variables must be initialized when declared",
                node.lineno,
                node.col_offset)

        target = node.target.id
        cpp_type = CppTypeVisitor(self.source_lines,
                                  self.context,
                                  self.filename).visit(node.annotation)

        if isinstance(node.annotation, ast.List):
            if isinstance(node.value, ast.Name):
                value = self.visit(node.value)
            else:
                value = ', '.join([self.visit(item)
                                   for item in node.value.elts])
            self.context.define_global_variable(target, None, node.target)

            return f'auto {target} = {cpp_type}({{{value}}});'

        value = self.visit_value(node.value, cpp_type)
        self.context.define_global_variable(target, cpp_type, node.target)

        return f'{cpp_type} {target} = {value};'

    def visit_UnaryOp(self, node):
        op = OPERATORS[type(node.op)]
        operand = self.visit(node.operand)

        return f'{op}({operand})'

    def visit_Module(self, node):
        body = [
            self.visit(item)
            for item in node.body
        ]

        return '\n\n'.join([
            '// This file was generated by mys. DO NOT EDIT!!!',
            f'#include "{self.module_hpp}"'
        ] + self.before_namespace + [
            f'namespace {self.namespace}',
            '{'
        ] + self.forward_declarations + body + [
            '}',
            '',
            self.main()
        ])

    def main(self):
        if self.add_package_main:
            return '\n'.join([
                'int package_main(int argc, const char *argv[])',
                '{',
                f'    return {self.namespace}::main(argc, argv);',
                '}',
                ''
            ])
        else:
            return ''

    def visit_ImportFrom(self, node):
        module, name, asname = get_import_from_info(node, self.module_levels)
        definitions = self.definitions.get(module)

        if definitions is None:
            raise LanguageError(f"imported module '{module}' does not exist",
                                node.lineno,
                                node.col_offset)

        if name.name.startswith('_'):
            raise LanguageError(f"can't import private definition '{name.name}'",
                                node.lineno,
                                node.col_offset)

        if name.name in definitions.variables:
            self.context.define_global_variable(
                asname,
                definitions.variables[name.name].type,
                node)
        elif name.name in definitions.functions:
            pass
        elif name.name in definitions.classes:
            pass
        else:
            raise LanguageError(
                f"imported module '{module}' does not contain '{name.name}'",
                node.lineno,
                node.col_offset)

        return ''

    def get_decorator_names(self, decorator_list):
        names = []

        for decorator in decorator_list:
            if isinstance(decorator, ast.Call):
                names.append(self.visit(decorator.func))
            elif isinstance(decorator, ast.Name):
                names.append(decorator.id)
            else:
                raise LanguageError("decorator",
                                    decorator.lineno,
                                    decorator.col_offset)

        return names

    def visit_enum(self, name, node):
        decorator = node.decorator_list[0]

        if isinstance(decorator, ast.Call):
            if len(decorator.args) == 1:
                type_ = self.visit(decorator.args[0])
            else:
                raise LanguageError("enum value type",
                                    node.lineno,
                                    node.col_offset)
        else:
            type_ = 'i64'

        members = []

        for item in node.body:
            if not isinstance(item, ast.Assign):
                raise LanguageError("enum",
                                    item.lineno,
                                    item.col_offset)

            if len(item.targets) != 1:
                raise LanguageError("enum",
                                    item.lineno,
                                    item.col_offset)

            if not isinstance(item.targets[0], ast.Name):
                raise LanguageError("enum",
                                    item.lineno,
                                    item.col_offset)

            member_name = item.targets[0].id

            if not is_integer_literal(item.value):
                raise LanguageError("enum",
                                    item.lineno,
                                    item.col_offset)

            member_value = make_integer_literal(type_, item.value)

            members.append(f"    {member_name} = {member_value},")

        self.context.define_enum(name, type_)

        return '\n'.join([
            f'enum class {name} : {type_} {{'
        ] + members + [
            '};'
        ])

    def is_single_pass(self, body):
        if len(body) != 1:
            return False

        return isinstance(body[0], ast.Pass)

    def visit_trait(self, name, node):
        body = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if not self.is_single_pass(item.body):
                    raise LanguageError("trait method body must be 'pass'",
                                        item.lineno,
                                        item.col_offset)

                body.append(TraitMethodVisitor(name,
                                               self.source_lines,
                                               self.context,
                                               self.filename).visit(item))
            elif isinstance(item, ast.AnnAssign):
                raise LanguageError('traits can not have members',
                                    node.lineno,
                                    node.col_offset)

        self.context.define_trait(name)

        return '\n\n'.join([
            f'class {name} : public Object {{',
            'public:'
        ] + body + [
            '};'
        ])

    def visit_ClassDef(self, node):
        class_name = node.name
        members = []
        member_types = []
        member_names = []
        member_values = []
        method_names = []
        body = []

        decorator_names = self.get_decorator_names(node.decorator_list)

        if decorator_names == ['enum']:
            return self.visit_enum(class_name, node)
        elif decorator_names == ['trait']:
            return self.visit_trait(class_name, node)
        elif decorator_names:
            raise LanguageError('invalid class decorator(s)',
                                node.lineno,
                                node.col_offset)

        self.context.define_class(class_name)

        bases = []

        for base in node.bases:
            if not self.context.is_trait_defined(base.id):
                raise LanguageError('trait does not exist',
                                    base.lineno,
                                    base.col_offset)

            bases.append(f'public {base.id}')

        bases = ', '.join(bases)

        if not bases:
            bases = 'public Object'

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self.context.push()

                if is_method(item.args):
                    body.append(indent(MethodVisitor(class_name,
                                                     method_names,
                                                     self.source_lines,
                                                     self.context,
                                                     self.filename).visit(item)))
                else:
                    raise LanguageError("class functions are not yet implemented",
                                        item.lineno,
                                        item.col_offset)

                self.context.pop()
            elif isinstance(item, ast.AnnAssign):
                member_name = self.visit(item.target)
                member_type = self.visit(item.annotation)

                if item.value is not None:
                    member_value = self.visit_value(item.value, member_type)
                elif member_type in ['i8', 'i16', 'i32', 'i64']:
                    member_value = "0"
                elif member_type in ['u8', 'u16', 'u32', 'u64']:
                    member_value = "0"
                elif member_type in ['f32', 'f64']:
                    member_value = "0.0"
                elif member_type == 'String':
                    member_value = 'String()'
                elif member_type == 'bytes':
                    member_value = "Bytes()"
                elif member_type == 'bool':
                    member_value = "false"
                else:
                    member_value = 'std::nullptr'

                members.append(f'{member_type} {member_name};')
                member_types.append(member_type)
                member_names.append(member_name)
                member_values.append(member_value)

        if '__init__' not in method_names:
            body.append(indent(create_class_init(class_name,
                                                 member_names,
                                                 member_types,
                                                 member_values)))

        if '__str__' not in method_names:
            body.append(indent(create_class_str(class_name, member_names)))

        return '\n\n'.join([
            f'class {class_name} : {bases} {{',
            'public:',
            indent('\n'.join(members))
        ] + body + [
            '};'
        ])

    def visit_FunctionDef(self, node):
        self.context.push()

        if node.returns is None:
            self.context.return_cpp_type = None
        else:
            self.context.return_cpp_type = TypeVisitor().visit(node.returns)

        function_name = node.name
        return_type = return_type_string(node.returns,
                                         self.source_lines,
                                         self.context,
                                         self.filename)
        params = params_string(function_name,
                               node.args.args,
                               self.source_lines,
                               self.context)
        self.context.define_function(function_name, return_type)
        body = []
        body_iter = iter(node.body)

        if has_docstring(node, self.source_lines):
            next(body_iter)

        for item in body_iter:
            body.append(indent(BodyVisitor(self.source_lines,
                                           self.context,
                                           self.filename).visit(item)))

        if function_name == 'main':
            self.add_package_main = True

            if return_type == 'void':
                return_type = 'int'
            else:
                raise Exception("main() must return 'None'.")

            if params not in ['std::shared_ptr<List<String>>& argv', 'void']:
                raise Exception("main() takes 'argv: [string]' or no arguments.")

            if params == 'void':
                body = [indent('\n'.join([
                    '(void)__argc;',
                    '(void)__argv;'
                ]))] + body
            else:
                body = [indent('auto argv = create_args(__argc, __argv);')] + body

            params = 'int __argc, const char *__argv[]'
            body += ['', indent('return 0;')]

        prototype = f'{return_type} {function_name}({params})'
        decorators = self.get_decorator_names(node.decorator_list)

        if 'test' in decorators:
            if self.skip_tests:
                code = ''
            else:
                parts = Path(self.module_hpp).parts
                full_test_name = list(parts[1:-1])
                full_test_name += [parts[-1].split('.')[0]]
                full_test_name += [function_name]
                full_test_name = '::'.join([part for part in full_test_name])
                code = '\n'.join([
                    '#if defined(MYS_TEST)',
                    '',
                    f'static {prototype}',
                    '{'
                ] + body + [
                    '}',
                    '',
                    f'static Test mys_test_{function_name}("{full_test_name}", '
                    f'{function_name});',
                    '',
                    '#endif'
                ])
        else:
            self.forward_declarations.append(prototype + ';')
            code = '\n'.join([
                prototype,
                '{'
            ] + body + [
                '}'
            ])

        self.context.pop()

        return code

    def visit_Expr(self, node):
        return self.visit(node.value) + ';'

    def visit_Name(self, node):
        return node.id

    def handle_string_source(self, node, value):
        if value.startswith('mys-embedded-c++-before-namespace'):
            self.before_namespace.append('\n'.join([
                '/* mys-embedded-c++-before-namespace start */\n',
                textwrap.dedent(value[33:]).strip(),
                '\n/* mys-embedded-c++-before-namespace stop */']))

            return ''
        else:
            return handle_string_node(node, value, self.source_lines)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            type_ = 'String'
            value = self.handle_string_source(node, node.value)
        elif isinstance(node.value, bool):
            type_ = 'bool'
            value = 'true' if node.value else 'false'
        else:
            raise LanguageError("internal error",
                                node.lineno,
                                node.col_offset)

        self.context.cpp_type = type_

        return value

    def generic_visit(self, node):
        raise Exception(node)

class MethodVisitor(BaseVisitor):

    def __init__(self, class_name, method_names, source_lines, context, filename):
        super().__init__(source_lines, context, filename)
        self._class_name = class_name
        self._method_names = method_names

    def validate_operator_signature(self,
                                    method_name,
                                    params,
                                    return_type,
                                    node):
        expected_return_type = {
            '__add__': self._class_name,
            '__sub__': self._class_name,
            '__iadd__': 'void',
            '__isub__': 'void',
            '__eq__': 'bool',
            '__ne__': 'bool',
            '__gt__': 'bool',
            '__ge__': 'bool',
            '__lt__': 'bool',
            '__le__': 'bool'
        }[method_name]

        if return_type != expected_return_type:
            raise LanguageError(
                f'{method_name}() must return {expected_return_type}',
                node.lineno,
                node.col_offset)

    def visit_FunctionDef(self, node):
        method_name = node.name
        return_type = self.return_type_string(node.returns)

        if node.decorator_list:
            raise Exception("Methods must not be decorated.")

        self.context.define_variable('self', self._class_name, node.args.args[0])
        params = params_string(method_name,
                               node.args.args[1:],
                               self.source_lines,
                               self.context)
        body = []
        body_iter = iter(node.body)

        if has_docstring(node, self.source_lines):
            next(body_iter)

        for item in body_iter:
            body.append(indent(BodyVisitor(self.source_lines,
                                           self.context,
                                           self.filename).visit(item)))

        body = '\n'.join(body)
        self._method_names.append(method_name)

        if method_name == '__init__':
            return '\n'.join([
                f'{self._class_name}({params})',
                '{',
                body,
                '}'
            ])
        elif method_name == '__del__':
            raise LanguageError('__del__ is not yet supported',
                                node.lineno,
                                node.col_offset)
        elif method_name in METHOD_OPERATORS:
            self.validate_operator_signature(method_name,
                                             params,
                                             return_type,
                                             node)
            method_name = 'operator' + METHOD_OPERATORS[method_name]

        return '\n'.join([
            f'{return_type} {method_name}({params})',
            '{',
            body,
            '}'
        ])

    def generic_visit(self, node):
        raise Exception(node)

class TraitMethodVisitor(BaseVisitor):

    def __init__(self, class_name, source_lines, context, filename):
        super().__init__(source_lines, context, filename)
        self._class_name = class_name

    def validate_operator_signature(self,
                                    method_name,
                                    params,
                                    return_type,
                                    node):
        expected_return_type = {
            '__add__': self._class_name,
            '__sub__': self._class_name,
            '__iadd__': 'void',
            '__isub__': 'void',
            '__eq__': 'bool',
            '__ne__': 'bool',
            '__gt__': 'bool',
            '__ge__': 'bool',
            '__lt__': 'bool',
            '__le__': 'bool'
        }[method_name]

        if return_type != expected_return_type:
            raise LanguageError(
                f'{method_name}() must return {expected_return_type}',
                node.lineno,
                node.col_offset)

    def visit_FunctionDef(self, node):
        self.context.push()
        method_name = node.name
        return_type = self.return_type_string(node.returns)

        if node.decorator_list:
            raise Exception("Methods must not be decorated.")

        if len(node.args.args) == 0 or node.args.args[0].arg != 'self':
            raise LanguageError(
                'Methods must take self as their first argument.',
                node.lineno,
                node.col_offset)

        params = params_string(method_name,
                               node.args.args[1:],
                               self.source_lines,
                               self.context)

        if method_name == '__init__':
            raise LanguageError('__init__ is not allowed in a trait',
                                node.lineno,
                                node.col_offset)
        elif method_name == '__del__':
            raise LanguageError('__del__ is not allowed in a trait',
                                node.lineno,
                                node.col_offset)
        elif method_name in METHOD_OPERATORS:
            self.validate_operator_signature(method_name,
                                             params,
                                             return_type,
                                             node)
            method_name = 'operator' + METHOD_OPERATORS[method_name]

        self.context.pop()

        return indent(f'virtual {return_type} {method_name}({params}) = 0;')

    def generic_visit(self, node):
        raise Exception(node)

class BodyVisitor(BaseVisitor):
    pass

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

class TracebackLexer(RegexLexer):

    tokens = {
        'root': [
            (r'^(  File )("[^"]+")(, line )(\d+)(\n)',
             bygroups(Generic.Error, Name.Builtin, Generic.Error, Number, Text)),
            (r'^(\s+?)(\^)(\n)',
             bygroups(Text, Generic.Error, Text)),
            (r'^(    )(.+)(\n)',
             bygroups(Text, using(PythonLexer), Text)),
            (r'^([^:]+)(: )(.+)(\n)',
             bygroups(Generic.Escape, Text, Name, Text), '#pop')
        ]
    }

def style_traceback(traceback):
    return highlight(traceback,
                     TracebackLexer(),
                     Terminal256Formatter(style='monokai'))

def transpile_file(tree,
                   source,
                   filename,
                   module_hpp,
                   module,
                   definitions,
                   skip_tests=False):
    namespace = 'mys::' + module_hpp[:-8].replace('/', '::')
    module_levels = module_hpp[:-8].split('/')
    source_lines = source.split('\n')
    header = HeaderVisitor(namespace,
                           module_levels,
                           source_lines,
                           definitions[module]).visit(tree)
    source = SourceVisitor(module_levels,
                           module_hpp,
                           filename,
                           skip_tests,
                           namespace,
                           source_lines,
                           definitions,
                           definitions[module]).visit(tree)

    return header, source

class Source:

    def __init__(self,
                 contents,
                 filename='',
                 module='',
                 mys_path='',
                 module_hpp='',
                 skip_tests='',
                 hpp_path='',
                 cpp_path=''):
        self.contents = contents
        self.filename = filename
        self.module = module
        self.mys_path = mys_path
        self.module_hpp = module_hpp
        self.skip_tests = skip_tests
        self.hpp_path = hpp_path
        self.cpp_path = cpp_path

def transpile(sources):
    generated = []
    trees = []
    definitions = {}

    try:
        for source in sources:
            trees.append(ast.parse(source.contents, source.filename))
    except SyntaxError:
        raise Exception(
            style_traceback('\n'.join(traceback.format_exc(0).splitlines()[1:])))

    try:
        for source, tree in zip(sources, trees):
            definitions[source.module] = find_definitions(tree)

        for source, tree in zip(sources, trees):
            generated.append(transpile_file(tree,
                                            source.contents,
                                            source.mys_path,
                                            source.module_hpp,
                                            source.module,
                                            definitions,
                                            source.skip_tests))

        return generated
    except LanguageError as e:
        line = source.contents.splitlines()[e.lineno - 1]
        marker_line = ' ' * e.offset + '^'

        raise Exception(
            style_traceback(f'  File "{source.filename}", line {e.lineno}\n'
                            f'    {line}\n'
                            f'    {marker_line}\n'
                            f'LanguageError: {e.message}'))
