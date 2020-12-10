import textwrap
from pathlib import Path
from ..parser import ast
from .utils import LanguageError
from .utils import TypeVisitor
from .utils import is_integer_literal
from .utils import is_float_literal
from .utils import make_integer_literal
from .utils import make_float_literal
from .utils import OPERATORS
from .utils import INTEGER_TYPES
from .utils import Context
from .utils import BaseVisitor
from .utils import get_import_from_info
from .utils import params_string
from .utils import return_type_string
from .utils import CppTypeVisitor
from .utils import indent
from .definitions import find_definitions
from .definitions import is_method

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

        for name, functions in module_definitions.functions.items():
            self.context.define_function(name, functions)

    def visit_value(self, node, mys_type):
        if is_integer_literal(node):
            return make_integer_literal(mys_type, node)
        elif is_float_literal(node):
            return make_float_literal(mys_type, node)
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
                self.context.mys_type = node.func.id

                return f'std::make_shared<{node.func.id}>({args})'

        if function_name in INTEGER_TYPES:
            self.context.mys_type = function_name

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

            self.context.define_global_variable(target, mys_type, node.target)

            return (f'std::shared_ptr<List<{cpp_type}>> {target} = '
                    f'std::make_shared<List<{cpp_type}>>('
                    f'std::initializer_list<{cpp_type}>{{{value}}});')

        cpp_type = CppTypeVisitor(self.source_lines,
                                  self.context,
                                  self.filename).visit(node.annotation)
        value = self.visit_value(node.value, cpp_type)
        self.context.define_global_variable(target, mys_type, node.target)

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
        imported_module = self.definitions.get(module)

        if imported_module is None:
            raise LanguageError(f"imported module '{module}' does not exist",
                                node.lineno,
                                node.col_offset)

        if name.name.startswith('_'):
            raise LanguageError(f"can't import private definition '{name.name}'",
                                node.lineno,
                                node.col_offset)

        if name.name in imported_module.variables:
            self.context.define_global_variable(
                asname,
                imported_module.variables[name.name].type,
                node)
        elif name.name in imported_module.functions:
            self.context.define_function(name.name,
                                         imported_module.functions[name.name])
        elif name.name in imported_module.classes:
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
            self.context.return_mys_type = None
        else:
            self.context.return_mys_type = TypeVisitor().visit(node.returns)

        function_name = node.name
        return_type = return_type_string(node.returns,
                                         self.source_lines,
                                         self.context,
                                         self.filename)
        params = params_string(function_name,
                               node.args.args,
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
            self.context.mys_type = 'string'

            return self.handle_string_source(node, node.value)
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

        if node.returns is None:
            self.context.return_mys_type = None
        else:
            self.context.return_mys_type = TypeVisitor().visit(node.returns)

        return_type = self.return_type_string(node.returns)

        if node.decorator_list:
            raise Exception("Methods must not be decorated.")

        self.context.define_variable('self', self._class_name, node.args.args[0])
        params = params_string(method_name,
                               node.args.args[1:],
                               self.source_lines,
                               self.context)
        self._method_names.append(method_name)

        if method_name in METHOD_OPERATORS:
            self.validate_operator_signature(method_name,
                                             params,
                                             return_type,
                                             node)
            method_name = 'operator' + METHOD_OPERATORS[method_name]

        body = []
        body_iter = iter(node.body)

        if has_docstring(node, self.source_lines):
            next(body_iter)

        for item in body_iter:
            body.append(indent(BodyVisitor(self.source_lines,
                                           self.context,
                                           self.filename).visit(item)))

        body = '\n'.join(body)

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
