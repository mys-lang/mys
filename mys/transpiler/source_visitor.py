import textwrap
from pathlib import Path

from ..parser import ast
from .base import BaseVisitor
from .body_check_visitor import BodyCheckVisitor
from .context import Context
from .utils import BUILTIN_ERRORS
from .utils import CompileError
from .utils import InternalError
from .utils import format_default
from .utils import format_method_name
from .utils import format_parameters
from .utils import format_return_type
from .utils import get_import_from_info
from .utils import has_docstring
from .utils import indent
from .utils import is_private
from .utils import mys_to_cpp_type
from .utils import mys_to_cpp_type_param


def create_enum_from_integer(enum):
    code = [
        f'{enum.type} {enum.name}_from_value({enum.type} value)',
        '{',
        '    switch (value) {'
    ]

    for name, value in enum.members:
        code += [
            f'    case {value}:',
            f'        return ({enum.type}){enum.name}::{name};'
        ]

    code += [
        '    default:',
        '        std::make_shared<ValueError>("bad enum value")->__throw();',
        '    }',
        '}'
    ]

    return code


class SourceVisitor(ast.NodeVisitor):
    """The source visitor generates C++ code from given AST.

    """


    def __init__(self,
                 namespace,
                 module_levels,
                 module_hpp,
                 filename,
                 source_lines,
                 definitions,
                 module_definitions,
                 skip_tests,
                 specialized_functions,
                 specialized_classes):
        self.module_levels = module_levels
        self.source_lines = source_lines
        self.module_hpp = module_hpp
        self.filename = filename
        self.skip_tests = skip_tests
        self.namespace = namespace
        self.forward_declarations = []
        self.add_package_main = False
        self.before_namespace = []
        self.context = Context(module_levels,
                               specialized_functions,
                               specialized_classes)
        self.definitions = definitions
        self.module_definitions = module_definitions
        self.enums = []
        self.body = []
        self.variables = []
        self.init_globals = []

        for name, functions in module_definitions.functions.items():
            self.context.define_function(
                name,
                self.context.make_full_name_this_module(name),
                functions)

        for name, trait_definitions in module_definitions.traits.items():
            self.context.define_trait(name,
                                      self.context.make_full_name_this_module(name),
                                      trait_definitions)

        self.context.define_trait('Error', 'Error', None)

        for name, class_definitions in module_definitions.classes.items():
            self.context.define_class(name,
                                      self.context.make_full_name_this_module(name),
                                      class_definitions)

        for name in BUILTIN_ERRORS:
            self.context.define_class(name, name, None)

        for enum in module_definitions.enums.values():
            self.context.define_enum(
                enum.name,
                self.context.make_full_name_this_module(enum.name),
                enum.type)
            self.enums += create_enum_from_integer(enum)

    def define_parameters(self, args):
        for param, node in args:
            self.raise_if_type_not_defined(param.type, param.node.annotation)
            self.context.define_local_variable(param.name, param.type, node)

    def add_application_init(self, ordered_modules):
        body = []

        for module in ordered_modules:
            self.before_namespace += [
                f'namespace mys::{module.replace(".", "::")} {{',
                'extern void __module_init();',
                '}'
            ]
            body.append(f'    mys::{module.replace(".", "::")}::__module_init();')

        self.before_namespace += [
            'void __application_init(void)',
            '{'
        ] + body + [
            '}'
        ]

    def raise_if_type_not_defined(self, mys_type, node):
        if not self.context.is_type_defined(mys_type):
            raise CompileError(f"undefined type '{mys_type}'", node)

    def visit_AnnAssign(self, node):
        return GlobalVariableVisitor(self.source_lines,
                                     self.context,
                                     self.source_lines).visit(node)

    def visit_variable(self, variable):
        cpp_type = mys_to_cpp_type(variable.type, self.context)

        return [f'{cpp_type} {variable.name};']

    def visit_Module(self, node):
        for item in node.body:
            self.init_globals += self.visit(item)

        for name, definitions in self.module_definitions.classes.items():
            if definitions.generic_types:
                continue

            self.body += self.visit_class_definition(name, definitions)

        for functions in self.module_definitions.functions.values():
            for function in functions:
                if function.generic_types:
                    continue

                self.body += self.visit_function_defaults(function)
                self.body += self.visit_function_definition(function)

        for variable in self.module_definitions.variables.values():
            self.variables += self.visit_variable(variable)

    def visit_specialized_function(self, function):
        self.body += self.visit_function_defaults(function)
        self.body += self.visit_function_definition(function)

    def visit_specialized_class(self, name, definitions):
        self.body += self.visit_class_definition(name, definitions)

    def format_cpp(self):
        return '\n'.join([
            '// This file was generated by mys. DO NOT EDIT!!!',
            '#include "mys.hpp"',
            f'#include "{self.module_hpp}"'
        ] + self.before_namespace + [
            f'namespace {self.namespace}',
            '{'
        ] + self.forward_declarations
          + self.enums
          + [constant[1] for constant in self.context.constants.values()]
          + self.context.comprehensions
          + self.variables
          + self.body + [
              'void __module_init()',
              '{'
          ] + self.init_globals + [
              '}',
              '}'
          ]+ self.main())

    def main(self):
        if self.add_package_main:
            return [
                'void package_main(int argc, const char *argv[])',
                '{',
                '    core_fiber::init();',
                f'    {self.namespace}::main(argc, argv);',
                '}'
            ]
        else:
            return []

    def visit_import_from_define_function_return_type(self, function):
        if function.returns is None:
            return

        if '.' in function.returns:
            module = '.'.join(function.returns.split('.')[:-1])
            class_name = function.returns.split('.')[-1]
            imported = self.definitions.get(module)

            if class_name in imported.classes:
                self.context.define_class(function.returns,
                                          function.returns,
                                          imported.classes[class_name])

    def visit_ImportFrom(self, node):
        module, name, asname = get_import_from_info(node, self.module_levels)
        imported_module = self.definitions.get(module)

        if is_private(name):
            raise CompileError(f"cannot import private definition '{name}'", node)

        full_name = f'{module}.{name}'

        if name in imported_module.variables:
            self.context.define_global_variable(
                asname,
                full_name,
                imported_module.variables[name].type,
                node)
        elif name in imported_module.functions:
            for function in imported_module.functions[name]:
                self.visit_import_from_define_function_return_type(function)

            self.context.define_function(asname,
                                         full_name,
                                         imported_module.functions[name])
        elif name in imported_module.classes:
            for methods in imported_module.classes[name].methods.values():
                for method in methods:
                    self.visit_import_from_define_function_return_type(method)

            self.context.define_class(asname,
                                      full_name,
                                      imported_module.classes[name])
        elif name in imported_module.traits:
            self.context.define_trait(asname,
                                      full_name,
                                      imported_module.traits[name])
        elif name in imported_module.enums:
            self.context.define_enum(asname,
                                     full_name,
                                     imported_module.enums[name].type)
        else:
            raise CompileError(
                f"imported module '{module}' does not contain '{name}'",
                node)

        return []

    def visit_ClassDef(self, _node):
        return []

    def visit_defaults(self, name, args):
        code = []

        for param, default in args:
            if default is None:
                continue

            cpp_type = mys_to_cpp_type(param.type, self.context)
            body = BaseVisitor(self.source_lines,
                               self.context,
                               self.filename).visit_value_check_type(default,
                                                                     param.type)

            code += [
                format_default(name, param.name, cpp_type),
                '{',
                f'    return {body};',
                '}'
            ]

        return code

    def visit_method_defaults(self, method, class_name):
        if method.name == '__init__':
            method_name = class_name
        elif method.name == '__del__':
            method_name = f'~{class_name}'
        else:
            method_name = method.name

        return self.visit_defaults(f'{class_name}_{method_name}', method.args)

    def visit_class_methods_definition(self,
                                       class_name,
                                       method_names,
                                       methods_definitions):
        body = []

        for method in methods_definitions:
            body += self.visit_method_defaults(method, class_name)
            self.context.push()
            self.context.define_local_variable(
                'self',
                self.context.make_full_name_this_module(class_name),
                method.node.args.args[0])
            self.define_parameters(method.args)
            self.raise_if_type_not_defined(method.returns, method.node.returns)
            method_names.append(method.name)
            method_name = format_method_name(method, class_name)
            parameters = format_parameters(method.args, self.context)
            self.context.return_mys_type = method.returns

            if method_name in [class_name, f'~{class_name}']:
                body.append(f'{class_name}::{method_name}({parameters})')
            else:
                return_cpp_type = format_return_type(method.returns, self.context)
                body.append(
                    f'{return_cpp_type} {class_name}::{method_name}({parameters})')

            body.append('{')
            body_iter = iter(method.node.body)

            if has_docstring(method.node):
                next(body_iter)

            for item in body_iter:
                BodyCheckVisitor().visit(item)
                body.append(indent(BodyVisitor(self.source_lines,
                                               self.context,
                                               self.filename).visit(item)))

            body.append('}')
            self.context.pop()

        return body

    def visit_class_definition(self, class_name, definitions):
        member_cpp_types = []
        member_names = []
        method_names = []
        body = []

        for member in definitions.members.values():
            if not self.context.is_type_defined(member.type):
                raise CompileError(f"undefined type '{member.type}'",
                                   member.node.annotation)

            member_cpp_types.append(mys_to_cpp_type_param(member.type, self.context))
            member_names.append(member.name)

        for methods in definitions.methods.values():
            body += self.visit_class_methods_definition(class_name,
                                                        method_names,
                                                        methods)

        if 'Error' in definitions.implements:
            body += [
                f'void {class_name}::__throw()',
                '{',
                f'    throw __{class_name}(shared_from_this());',
                '}'
            ]

        return body

    def visit_FunctionDef(self, _node):
        return []

    def visit_function_defaults(self, function):
        return self.visit_defaults(function.name, function.args)

    def visit_function_definition_main(self,
                                       function,
                                       parameters,
                                       return_cpp_type,
                                       body):
        self.add_package_main = True

        if return_cpp_type != 'void':
            raise CompileError("main() must not return any value", function.node)

        if parameters not in ['const SharedList<String>& argv', 'void']:
            raise CompileError("main() takes 'argv: [string]' or no arguments",
                               function.node)

        if parameters == 'void':
            body = [
                '    (void)__argc;',
                '    (void)__argv;'
            ] + body
        else:
            body = ['    auto argv = create_args(__argc, __argv);'] + body

        parameters = 'int __argc, const char *__argv[]'

        return body, parameters

    def visit_function_definition_test(self, function_name, prototype, body):
        if self.skip_tests:
            code = []
        else:
            parts = Path(self.module_hpp).parts
            full_test_name = list(parts[1:-1])
            full_test_name += [parts[-1].split('.')[0]]
            full_test_name += [function_name]
            full_test_name = '::'.join(full_test_name)
            code = [
                '#if defined(MYS_TEST)',
                f'static {prototype}',
                '{'
            ] + body + [
                '}',
                f'static Test mys_test_{function_name}("{full_test_name}", '
                f'{function_name});',
                '#endif'
            ]

        return code

    def visit_function_definition(self, function):
        self.context.push()
        self.define_parameters(function.args)
        self.raise_if_type_not_defined(function.returns, function.node.returns)
        function_name = function.node.name
        parameters = format_parameters(function.args, self.context)
        return_cpp_type = format_return_type(function.returns, self.context)
        self.context.return_mys_type = function.returns
        body = []
        body_iter = iter(function.node.body)

        if has_docstring(function.node):
            next(body_iter)

        for item in body_iter:
            BodyCheckVisitor().visit(item)
            body.append(indent(BodyVisitor(self.source_lines,
                                           self.context,
                                           self.filename).visit(item)))

        if function_name == 'main':
            body, parameters = self.visit_function_definition_main(function,
                                                                   parameters,
                                                                   return_cpp_type,
                                                                   body)

        prototype = f'{return_cpp_type} {function_name}({parameters})'

        if function.is_test:
            code = self.visit_function_definition_test(function_name,
                                                       prototype,
                                                       body)
        else:
            self.forward_declarations.append(prototype + ';')
            code = [
                prototype,
                '{'
            ] + body + [
                '}'
            ]

        self.context.pop()

        return code

    def visit_Expr(self, node):
        return self.visit(node.value) + [';']

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            if node.value.startswith('mys-embedded-c++-before-namespace'):
                self.before_namespace += [
                    '/* mys-embedded-c++-before-namespace start */',
                    textwrap.dedent(node.value[33:]).strip(),
                    '/* mys-embedded-c++-before-namespace stop */'
                ]
                return []
            elif node.value.startswith('mys-embedded-c++'):
                return [
                    '/* mys-embedded-c++ start */',
                    textwrap.dedent(node.value[17:]).strip(),
                    '/* mys-embedded-c++ stop */']

        raise CompileError("syntax error", node)

    def generic_visit(self, node):
        raise InternalError("unhandled node", node)


class BodyVisitor(BaseVisitor):
    pass


class GlobalVariableVisitor(BaseVisitor):

    def visit_AnnAssign(self, node):
        target, mys_type, _, cpp_target, code = self.visit_ann_assign(node)
        self.context.define_global_variable(
            target,
            self.context.make_full_name_this_module(target),
            mys_type,
            node.target)

        return [f'    {cpp_target} = {code};']
