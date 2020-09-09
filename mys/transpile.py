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
    'int',
    'float',
    'bool'
])

class LanguageError(Exception):

    def __init__(self, message, lineno, offset):
        self.message = message
        self.lineno = lineno
        self.offset = offset

def return_type_string(node):
    if isinstance(node, ast.Tuple):
        types = []

        for item in node.elts:
            if isinstance(item, ast.Name):
                if item.id == 'str':
                    types.append('String')
                else:
                    types.append(item.id)
            elif isinstance(item, ast.Subscript):
                if item.slice.value.id == 'str':
                    types.append('String')

        types = ', '.join(types)

        return f'Tuple<{types}>'
    elif isinstance(node, ast.List):
        type_string = 'todo'
        item = node.elts[0]

        if isinstance(item, ast.Name):
            if item.id == 'str':
                type_string = 'String'
            else:
                type_string = item.id
        elif isinstance(item, ast.Subscript):
            if item.slice.value.id == 'str':
                type_string = 'String'

        return f'List<{type_string}>'
    elif node is None:
        return 'void'
    elif isinstance(node, ast.Name):
        if node.id == 'str':
            return 'String'
        else:
            return node.id
    elif isinstance(node, ast.Dict):
        key_type = node.keys[0].id
        value_type = return_type_string(node.values[0])
        return f'Dict<{key_type}, {value_type}>'
    else:
        return type(node)

def params_string(function_name, args):
    if not args:
        return 'void'
    else:
        return ', '.join([
            ParamVisitor(function_name).visit(arg)
            for arg in args
        ])

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

    def visit_Name(self, node):
        return node.id

    def visit_Call(self, node):
        function_name = self.visit(node.func)
        args = [
            self.visit(arg)
            for arg in node.args
        ]

        if function_name == 'print':
            if len(args) == 0:
                code = 'std::cout << std::endl'
            elif len(args) == 1:
                code = f'std::cout << {args[0]} << std::endl'
            else:
                first = args[0]
                args = ' << " " << '.join(args[1:])
                code = f'std::cout << {first} << " " << {args} << std::endl'
        else:
            if function_name == 'int':
                function_name = 'to_int'

            args = ', '.join(args)
            code = f'{function_name}({args})'

        return code

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return handle_string(node.value)
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
        return handle_string(node.s)

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
        op_class = node.op.__class__

        if op_class == ast.Pow:
            return f'ipow({left}, {right})'
        else:
            op = OPERATORS[op_class]

            return f'({left} {op} {right})'

    def visit_UnaryOp(self, node):
        op = OPERATORS[node.op.__class__]
        operand = self.visit(node.operand)

        return f'{op}{operand}'

    def visit_AugAssign(self, node):
        lval = self.visit(node.target)
        op = OPERATORS[node.op.__class__]
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
        op_class = node.ops[0].__class__
        left = self.visit(node.left)
        right = self.visit(node.comparators[0])

        if op_class == ast.In:
            return f'contains({left}, {right})'
        elif op_class == ast.NotIn:
            return f'!contains({left}, {right})'
        else:
            return f'{left} {OPERATORS[op_class]} {right}'

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
            types = params_string('', node.annotation.elts)
            value = ', '.join([self.visit(item) for item in node.value.elts])

            return f'auto {target} = List<{types}>({{{value}}});'

        type_name = self.visit(node.annotation)
        value = self.visit(node.value)

        if target.startswith('this->'):
            return f'{target} = {value};'
        elif type_name in PRIMITIVE_TYPES:
            return f'{type_name} {target} = {value};'
        elif type_name == 'str':
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

    def generic_visit(self, node):
        raise LanguageError('unsupported language construct',
                            node.lineno,
                            node.col_offset)

class HeaderVisitor(BaseVisitor):

    def __init__(self, namespace):
        super().__init__()
        self.namespace = namespace
        self.imports = []
        self.other = []

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
        if len(node.names) != 1:
            raise LanguageError('import has more than one name')

        name = node.names[0].name

        if '.' not in name:
            name += '.lib'

        module_hpp = name.replace('.', '/')
        self.imports.append(f'#include "{module_hpp}.mys.hpp"')

        return ''

    def visit_ImportFrom(self, node):
        print(ast.dump(node))
        module = node.module

        if '.' not in module:
            module += '.lib'

        module_hpp = module.replace('.', '/')
        self.imports.append(f'#include "{module_hpp}.mys.hpp"')
        namespace = module.replace('.', '::')

        for name in node.names:
            # ToDo: Must figure out if a function or class is
            #       imported. Should probably prefix all function
            #       calls and classes with a namespace where used
            #       instead of this.
            self.imports.append('\n'.join([
                f'constexpr auto {name.name} = [] (auto &&...args) {{',
                f'    return {namespace}::{name.name}(std::forward<'
                f'decltype(args)>(args)...);',
                '};'
            ]))

        return ''

    def visit_ClassDef(self, node):
        return ''

    def visit_FunctionDef(self, node):
        function_name = node.name
        return_type = return_type_string(node.returns)
        params = params_string(function_name, node.args.args)

        if function_name == 'main':
            return ''

        decorators = [self.visit(decorator) for decorator in node.decorator_list]

        if 'test' not in decorators:
            self.other.append(f'{return_type} {function_name}({params});')

        return ''

    def visit_AnnAssign(self, node):
        return ''

    def generic_visit(self, node):
        raise Exception(node)

def create_class_str(class_name, member_names):
    return '\n'.join([
        'virtual String __str__() const',
        '{',
        '    std::stringstream ss;',
        '',
        f'    ss << "{class_name}(";',
        indent(' << ", ";\n'.join([f'ss << "{name}=" << this->{name}'
                                   for name in member_names]) + ';'),
        '    ss << ")";'
        '',
        '    return String(ss.str().c_str());'
        '}'
    ])

class SourceVisitor(BaseVisitor):

    def __init__(self, module_hpp, skip_tests, namespace):
        super().__init__()
        self.module_hpp = module_hpp
        self.skip_tests = skip_tests
        self.namespace = namespace
        self.forward_declarations = []
        self.main_kind = None

    def visit_Module(self, node):
        body = [
            self.visit(item)
            for item in node.body
        ]

        return '\n\n'.join([
            '// This file was generated by mys. DO NOT EDIT!!!',
            f'#include "{self.module_hpp}"',
            f'namespace {self.namespace}',
            '{'
        ] + self.forward_declarations + body + [
            '}',
            '',
            self.main()
        ])

    def main(self):
        if self.main_kind == 'args':
            code = [
                'int main(int argc, const char *argv[])',
                '{',
                f'    return {self.namespace}::main(argc, argv);',
                '}'
            ]
        elif self.main_kind == 'void':
            code = [
                'int main(void)',
                '{',
                f'    return {self.namespace}::main();',
                '}'
            ]
        else:
            code = []

        return '\n'.join([
            '#if !defined(MYS_TEST)'
        ] + code + [
            '#endif'
        ])

    def visit_Import(self, node):
        return ''

    def visit_ImportFrom(self, node):
        return ''

    def visit_ClassDef(self, node):
        class_name = node.name
        members = []
        member_names = []
        method_names = []
        body = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                body.append(indent(MethodVisitor(class_name,
                                                 members,
                                                 member_names,
                                                 method_names).visit(item)))

        if '__str__' not in method_names:
            body.append(indent(create_class_str(class_name, member_names)))

        return '\n\n'.join([
            f'class {class_name} {{',
            'public:',
            indent('\n'.join(members))
        ] + body + [
            '};'
        ])

    def visit_FunctionDef(self, node):
        function_name = node.name
        return_type = return_type_string(node.returns)
        params = params_string(function_name, node.args.args)
        body = []

        for item in node.body:
            body.append(indent(BodyVisitor().visit(item)))

        if function_name == 'main':
            if return_type == 'void':
                return_type = 'int'
            else:
                raise Exception("main() must return 'None'.")

            if params != 'void':
                if params != 'List<String>& args':
                    raise Exception("main() takes 'args: [str]' or no arguments.")

                params = 'int __argc, const char *__argv[]'
                body = [indent('auto args = create_args(__argc, __argv);')] + body
                self.main_kind = 'args'
            else:
                self.main_kind = 'void'

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

    def generic_visit(self, node):
        raise Exception(node)

class MethodVisitor(ast.NodeVisitor):

    def __init__(self, class_name, members, member_names, method_names):
        super().__init__()
        self._class_name = class_name
        self._members = members
        self._member_names = member_names
        self._method_names = method_names

    def visit_FunctionDef(self, node):
        method_name = node.name
        return_type = return_type_string(node.returns)

        if len(node.args.args) == 0 or node.args.args[0].arg != 'self':
            raise Exception(
                "Methods must always take 'self' as their first argument.")

        if node.decorator_list:
            raise Exception("Methods must not be decorated.")

        params = params_string(method_name, node.args.args[1:])
        body = []

        for item in node.body:
            body.append(indent(BodyVisitor().visit(item)))

        body = '\n'.join(body)
        self._method_names.append(method_name)

        if method_name == '__init__':
            for item in node.body:
                InitMemberVisitor(self._members, self._member_names).visit(item)

            return '\n'.join([
                f'{self._class_name}({params})',
                '{',
                body,
                '}'
            ])
        elif method_name == '__del__':
            raise LanguageError('__del__ is not yet supported')
        else:
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

class InitMemberVisitor(BaseVisitor):

    def __init__(self, members, member_names):
        super().__init__()
        self._members = members
        self._member_names = member_names

    def visit_AnnAssign(self, node):
        if not isinstance(node.target, ast.Attribute):
            return

        if node.target.value.id != 'self':
            return

        member_type = self.visit(node.annotation)
        member_name = node.target.attr
        self._members.append(f'{member_type} {member_name};')
        self._member_names.append(member_name)

class ParamVisitor(BaseVisitor):

    def __init__(self, function_name):
        super().__init__()
        self.function_name = function_name

    def visit_arg(self, node):
        param_name = node.arg
        annotation = node.annotation

        if annotation is None:
            raise Exception(f'{self.function_name}({param_name}) is not typed.')
        elif isinstance(annotation, ast.Name):
            param_type = annotation.id

            if param_type == 'str':
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

                if param_type == 'str':
                    param_type = 'String'
                elif param_type not in PRIMITIVE_TYPES:
                    param_type = f'std::shared_ptr<{param_type}>'

                return f'List<{param_type}>& {param_name}'
        elif isinstance(annotation, ast.Tuple):
            types = []

            for item in annotation.elts:
                param_type = item.id

                if param_type == 'str':
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
    namespace = module_hpp[:-8].replace('/', '::')

    try:
        header = HeaderVisitor(namespace).visit(ast.parse(source, filename))
        source = SourceVisitor(module_hpp,
                               skip_tests,
                               namespace).visit(ast.parse(source,
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
