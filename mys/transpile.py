import sys
import traceback
import textwrap
import ast
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
    'bool'
])

class LanguageError(Exception):

    def __init__(self, message, lineno, offset):
        self.message = message
        self.lineno = lineno
        self.offset = offset

def is_relative_import(node):
    return node.level > 0

def return_type_string(node):
    if isinstance(node, ast.Tuple):
        types = []

        for item in node.elts:
            if isinstance(item, ast.Name):
                if item.id == 'string':
                    types.append('String')
                else:
                    types.append(item.id)
            elif isinstance(item, ast.Subscript):
                if item.slice.value.id == 'string':
                    types.append('String')

        types = ', '.join(types)

        return f'Tuple<{types}>'
    elif isinstance(node, ast.List):
        type_string = 'todo'
        item = node.elts[0]

        if isinstance(item, ast.Name):
            if item.id == 'string':
                type_string = 'String'
            else:
                type_string = item.id
        elif isinstance(item, ast.Subscript):
            if item.slice.value.id == 'string':
                type_string = 'String'

        return f'List<{type_string}>'
    elif node is None:
        return 'void'
    elif isinstance(node, ast.Name):
        if node.id == 'string':
            return 'String'
        else:
            return node.id
    elif isinstance(node, ast.Dict):
        key_type = node.keys[0].id
        value_type = return_type_string(node.values[0])
        return f'Dict<{key_type}, {value_type}>'
    else:
        return type(node)

def params_string(function_name, args, source_lines, defaults=None):
    if defaults is None:
        defaults = []

    params = [
        ParamVisitor(function_name, source_lines).visit(arg)
        for arg in args
    ]

    defaults = [
        BaseVisitor(source_lines).visit(default)
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

BOOLOPS = {
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

class BaseVisitor(ast.NodeVisitor):

    def __init__(self, source_lines):
        self.source_lines = source_lines

    def is_string(self, node):
        line = self.source_lines[node.lineno - 1]

        if line[node.col_offset] != "'":
            return True

        return False

    def handle_string_node(self, node, value):
        if self.is_string(node):
            return handle_string(value)
        else:
            raise LanguageError('character literals are not yet supported',
                                node.lineno,
                                node.col_offset)

    def is_docstring(self, node):
        if sys.version_info >= (3, 8):
            if not isinstance(node, ast.Constant):
                return False

            if not isinstance(node.value, str):
                return False

            if not self.is_string(node):
                return False

            value = node.value
        else:
            if not isinstance(node, ast.Str):
                return False

            if not self.is_string(node):
                return False

            value = node.s

        return not value.startswith('mys-embedded-c++')

    def has_docstring(self, node):
        if len(node.body) == 0:
            return False

        first = node.body[0]

        if isinstance(first, ast.Expr):
            return self.is_docstring(first.value)

        return False

    def visit_Name(self, node):
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
        code = 'std::cout';

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

        return code

    def visit_Call(self, node):
        function_name = self.visit(node.func)
        args = [
            self.visit(arg)
            for arg in node.args
        ]

        if function_name == 'print':
            code = self.handle_print(node, args)
        else:
            if function_name in ['i8', 'i16', 'i32', 'i64']:
                function_name = 'to_int'

            args = ', '.join(args)
            code = f'{function_name}({args})'

        return code

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return self.handle_string_node(node, node.value)
        elif isinstance(node.value, bool):
            return 'true' if node.value else 'false'
        elif isinstance(node.value, float):
            return f'{node.value}f'
        else:
            return str(node.value)

    def visit_Num(self, node):
        value = node.n

        if isinstance(value, float):
            return f'{value}f'
        else:
            return str(value)

    def visit_Str(self, node):
        return self.handle_string_node(node, node.s)

    def visit_Bytes(self, node):
        raise LanguageError('bytes() is not yet supported',
                            node.lineno,
                            node.col_offset)

    def visit_NameConstant(self, node):
        return self.visit_Constant(node)

    def visit_Ellipsis(self, node):
        raise LanguageError("'...' is not yet supported",
                            node.lineno,
                            node.col_offset)

    def visit_Expr(self, node):
        return self.visit(node.value) + ';'

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
        op = OPERATORS[type(node.op)]
        operand = self.visit(node.operand)

        return f'{op}({operand})'

    def visit_AugAssign(self, node):
        lval = self.visit(node.target)
        op = OPERATORS[type(node.op)]
        rval = self.visit(node.value)

        return f'{lval} {op}= {rval};'

    def visit_Tuple(self, node):
        return 'Tuple<todo>({' + ', '.join([
            self.visit(item)
            for item in node.elts
        ]) + '})'

    def visit_List(self, node):
        return 'List<todo>({' + ', '.join([
            self.visit(item)
            for item in node.elts
        ]) + '})'

    def visit_Dict(self, node):
        return 'MakeDict<todo>({})'

    def visit_For(self, node):
        if isinstance(node.target, ast.Tuple):
            items = ', '.join([item.id for item in node.target.elts])
            var = f'[{items}]'
        else:
            var = self.visit(node.target)

        func = self.visit(node.iter)
        body = indent('\n'.join([
            self.visit(item)
            for item in node.body
        ]))

        return '\n'.join([
            f'for (auto {var}: {func}) {{',
            body,
            '}'
        ])

    def visit_Attribute(self, node):
        value = self.visit(node.value)

        if value == 'self':
            return f'this->{node.attr}'
        else:
            return f'{value}.{node.attr}'

    def visit_Compare(self, node):
        op_class = type(node.ops[0])
        left = self.visit(node.left)
        right = self.visit(node.comparators[0])

        if op_class == ast.In:
            return f'contains({left}, {right})'
        elif op_class == ast.NotIn:
            return f'!contains({left}, {right})'
        else:
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

        return f'return {value};'

    def visit_Try(self, node):
        body = indent('\n'.join([self.visit(item) for item in node.body]))
        finalbody = indent(
            '\n'.join([self.visit(item) for item in node.finalbody]))
        handlers = []

        for handler in node.handlers:
            if handler.type is None:
                exception = 'std::exception'
            else:
                exception = self.visit(handler.type)

            handlers.append('\n'.join([
                f'}} catch ({exception}& e) {{',
                indent('\n'.join([self.visit(item) for item in handler.body]))
            ]))

        if handlers:
            code = '\n'.join([
                'try {',
                body,
                '\n'.join(handlers),
                '}'
            ])
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

    def visit_Assign(self, node):
        value = self.visit(node.value)

        if len(node.targets) == 1:
            target = node.targets[0]

            if isinstance(target, ast.Tuple):
                return '\n'.join([f'auto value = {value};'] + [
                    f'auto {self.visit(item)} = std::get<{i}>(*value.m_tuple);'
                    for i, item in enumerate(target.elts)
                ])
            else:
                target = self.visit(target)

                return f'{target} = {value};'
        else:
            raise LanguageError(
                "assignments with more than one target is not yet supported",
                node.lineno,
                node.col_offset)

    def visit_Subscript(self, node):
        value = self.visit(node.value)
        index = self.visit(node.slice.value)

        return f'{value}[{index}]'

    def visit_AnnAssign(self, node):
        if node.value is None:
            raise LanguageError(
                "variables must be initialized when declared",
                node.lineno,
                node.col_offset)

        target = self.visit(node.target)

        if isinstance(node.annotation, ast.List):
            types = params_string('', node.annotation.elts, self.source_lines)

            if isinstance(node.value, ast.Name):
                value = self.visit(node.value)
            else:
                value = ', '.join([self.visit(item)
                                   for item in node.value.elts])

            return f'auto {target} = List<{types}>({{{value}}});'

        type_name = self.visit(node.annotation)
        value = self.visit(node.value)

        if target.startswith('this->'):
            return f'{target} = {value};'
        elif type_name in PRIMITIVE_TYPES:
            return f'{type_name} {target} = {value};'
        elif type_name == 'string':
            return f'String {target}({value});'
        else:
            return f'auto {target} = {type_name}({value});'

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
        cond = self.visit(node.test)

        return f'ASSERT({cond});'

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

    def visit_arguments(self, node):
        return ', '.join([self.visit(arg) for arg in node.args])

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
        return f'str({self.visit(node.value)})'

    def visit_BoolOp(self, node):
        values = [self.visit(value) for value in node.values]
        op = BOOLOPS[type(node.op)]

        return '((' + f') {op} ('.join(values) + '))'

    def generic_visit(self, node):
        raise LanguageError('unsupported language construct',
                            node.lineno,
                            node.col_offset)

class HeaderVisitor(BaseVisitor):

    def __init__(self, namespace, module_levels, source_lines):
        super().__init__(source_lines)
        self.namespace = namespace
        self.module_levels = module_levels
        self.imports = []
        self.other = []
        self.prefix = namespace.replace('::', '_').upper()

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
        ] + self.other + [
            '',
            '}',
            ''
        ])

    def visit_Import(self, node):
        raise LanguageError('use from ... import ...',
                            node.lineno,
                            node.col_offset)

    def make_relative_import_absolute(self, module, node):
        prefix = '.'.join(self.module_levels[0:-node.level])

        if not prefix:
            raise LanguageError('relative import is outside package',
                                node.lineno,
                                node.col_offset)

        if module is None:
            module = prefix
        else:
            module = f'{prefix}.{module}'

        return module

    def visit_ImportFrom(self, node):
        module = node.module

        if is_relative_import(node):
            module = self.make_relative_import_absolute(module, node)

        if '.' not in module:
            module += '.lib'

        module_hpp = module.replace('.', '/')
        self.imports.append(f'#include "{module_hpp}.mys.hpp"')
        prefix = 'MYS_' + module.replace('.', '_').upper()

        if len(node.names) != 1:
            raise LanguageError(f'only one import is allowed, found {len(node.names)}',
                                node.lineno,
                                node.col_offset)

        name = node.names[0]

        if name.asname:
            asname = name.asname
        else:
            asname = name.name

        self.other.append(f'{prefix}_{name.name}_IMPORT_AS({asname});')

    def visit_ClassDef(self, node):
        # MYS_TIMER_LIB_Timer_IMPORT_AS(__name__) \
        #     typedef mys::timer::lib::Timer __name__;
        pass

    def visit_FunctionDef(self, node):
        function_name = node.name
        return_type = return_type_string(node.returns)
        params = params_string(function_name,
                               node.args.args,
                               self.source_lines,
                               node.args.defaults)

        if function_name == 'main':
            return

        decorators = [self.visit(decorator) for decorator in node.decorator_list]

        if 'test' not in decorators:
            self.other.append(f'{return_type} {function_name}({params});')
            self.other.append('\n'.join([
                f'#define {self.prefix}_{function_name}_IMPORT_AS(__name__) \\',
                f'    constexpr auto __name__ = [] (auto &&...args) {{ \\',
                f'        return {self.namespace}::{function_name}(std::forward<'
                f'decltype(args)>(args)...); \\',
                f'    }};'
            ]))

        return ''

    def visit_AnnAssign(self, node):
        target = self.visit(node.target)
        type_name = self.visit(node.annotation)
        self.other.append(
            '\n'.join([
                f'extern {type_name} {target};',
                f'#define {self.prefix}_{target}_IMPORT_AS(__name__) \\',
                f'    static auto& __name__ = {self.namespace}::{target};'
            ]))

    def generic_visit(self, node):
        raise Exception(node)

def create_class_init(class_name, member_names, member_types, member_values):
    params = []
    body = []

    for member_name, member_type, member_value in zip(member_names,
                                                      member_types,
                                                      member_values):
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
        'virtual String __str__() const',
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

class SourceVisitor(BaseVisitor):

    def __init__(self, module_hpp, skip_tests, namespace, source_lines):
        super().__init__(source_lines)
        self.module_hpp = module_hpp
        self.skip_tests = skip_tests
        self.namespace = namespace
        self.forward_declarations = []
        self.add_package_main = False
        self.before_namespace = []

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

    def visit_Import(self, node):
        return ''

    def visit_ImportFrom(self, node):
        return ''

    def visit_ClassDef(self, node):
        class_name = node.name
        members = []
        member_types = []
        member_names = []
        member_values = []
        method_names = []
        body = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                body.append(indent(MethodVisitor(class_name,
                                                 method_names,
                                                 self.source_lines).visit(item)))
            elif isinstance(item, ast.AnnAssign):
                member_name = self.visit(item.target)
                member_type = self.visit(item.annotation)

                if item.value is not None:
                    member_value = self.visit(item.value)
                elif member_type in ['i8', 'i16', 'i32', 'i64']:
                    member_value = "0"
                elif member_type in ['u8', 'u16', 'u32', 'u64']:
                    member_value = "0"
                elif member_type in ['f32', 'f64']:
                    member_value = "0.0"
                elif member_type == 'string':
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
            f'class {class_name} : public Object {{',
            'public:',
            indent('\n'.join(members))
        ] + body + [
            '};'
        ])

    def visit_FunctionDef(self, node):
        function_name = node.name
        return_type = return_type_string(node.returns)
        params = params_string(function_name, node.args.args, self.source_lines)
        body = []
        body_iter = iter(node.body)

        if self.has_docstring(node):
            next(body_iter)

        for item in body_iter:
            body.append(indent(BodyVisitor(self.source_lines).visit(item)))

        if function_name == 'main':
            self.add_package_main = True

            if return_type == 'void':
                return_type = 'int'
            else:
                raise Exception("main() must return 'None'.")

            if params not in ['List<String>& argv', 'void']:
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
        decorators = [self.visit(decorator) for decorator in node.decorator_list]

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

        return code

    def handle_string_source(self, node, value):
        if value.startswith('mys-embedded-c++-before-namespace'):
            self.before_namespace.append('\n'.join([
                '/* mys-embedded-c++-before-namespace start */\n',
                textwrap.dedent(value[33:]).strip(),
                '\n/* mys-embedded-c++-before-namespace stop */']))

            return ''
        else:
            return self.handle_string_node(node, value)

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return self.handle_string_source(node, node.value)
        else:
            return super().visit_Constant(node)

    def visit_Str(self, node):
        if self.is_string(node):
            return self.handle_string_source(node, node.s)
        else:
            raise LanguageError('character literals are not yet supported',
                                node.lineno,
                                node.col_offset)

    def generic_visit(self, node):
        raise Exception(node)

class MethodVisitor(BaseVisitor):

    def __init__(self, class_name, method_names, source_lines):
        super().__init__(source_lines)
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
        return_type = return_type_string(node.returns)

        if node.decorator_list:
            raise Exception("Methods must not be decorated.")

        if len(node.args.args) == 0 or node.args.args[0].arg != 'self':
            raise LanguageError(
                'Methods must take self as their first argument.',
                node.lineno,
                node.col_offset)

        params = params_string(method_name, node.args.args[1:], self.source_lines)
        body = []
        body_iter = iter(node.body)

        if self.has_docstring(node):
            next(body_iter)

        for item in body_iter:
            body.append(indent(BodyVisitor(self.source_lines).visit(item)))

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

class BodyVisitor(BaseVisitor):
    pass

class ParamVisitor(BaseVisitor):

    def __init__(self, function_name, source_lines):
        super().__init__(source_lines)
        self.function_name = function_name

    def visit_arg(self, node):
        param_name = node.arg
        annotation = node.annotation

        if annotation is None:
            raise Exception(f'{self.function_name}({param_name}) is not typed.')
        elif isinstance(annotation, ast.Name):
            param_type = annotation.id

            if param_type == 'string':
                param_type = 'String&'
            elif param_type not in PRIMITIVE_TYPES:
                param_type = f'std::shared_ptr<{param_type}>&'

            return f'{param_type} {param_name}'
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                if annotation.value.id == 'Optional':
                    value = annotation.slice.value

                    if isinstance(value, ast.Name):
                        return f'std::optional<{value.id}>& {param_name}'
            else:
                return f'todo {param_name}'
        elif isinstance(annotation, ast.List):
            if len(annotation.elts) != 1:
                raise Exception('Lists must be [T].')
            else:
                param_type = annotation.elts[0].id

                if param_type == 'string':
                    param_type = 'String'
                elif param_type not in PRIMITIVE_TYPES:
                    param_type = f'std::shared_ptr<{param_type}>'

                return f'List<{param_type}>& {param_name}'
        elif isinstance(annotation, ast.Tuple):
            types = []

            for item in annotation.elts:
                param_type = item.id

                if param_type == 'string':
                    param_type = 'String'
                elif param_type not in PRIMITIVE_TYPES:
                    param_type = f'std::shared_ptr<{param_type}>'

                types.append(param_type)

            types = ', '.join(types)

            return f'Tuple<{types}>& {param_name}'

        raise Exception(ast.dump(node))

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

def transpile(source, filename, module_hpp, skip_tests=False):
    namespace = 'mys::' + module_hpp[:-8].replace('/', '::')
    module_levels = module_hpp[:-8].split('/')
    source_lines = source.split('\n')

    try:
        header = HeaderVisitor(namespace,
                               module_levels,
                               source_lines).visit(ast.parse(source, filename))
        source = SourceVisitor(module_hpp,
                               skip_tests,
                               namespace,
                               source_lines).visit(ast.parse(source,
                                                             filename))

        return header, source
    except SyntaxError:
        raise Exception(
            style_traceback('\n'.join(traceback.format_exc(0).splitlines()[1:])))
    except LanguageError as e:
        line = source.splitlines()[e.lineno - 1]
        marker_line = ' ' * e.offset + '^'

        raise Exception(
            style_traceback(f'  File "{filename}", line {e.lineno}\n'
                            f'    {line}\n'
                            f'    {marker_line}\n'
                            f'LanguageError: {e.message}'))
