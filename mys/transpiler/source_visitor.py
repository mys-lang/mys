import textwrap

from ..parser import ast
from .base import BaseVisitor
from .body_check_visitor import BodyCheckVisitor
from .context import Context
from .generics import TypeVisitor
from .generics import add_generic_class
from .generics import format_parameters
from .return_checker_visitor import check_returns
from .utils import BUILTIN_ERRORS
from .utils import CompileError
from .utils import Dict
from .utils import GenericType
from .utils import InternalError
from .utils import Optional
from .utils import Set
from .utils import Tuple
from .utils import Weak
from .utils import format_default
from .utils import format_method_name
from .utils import format_mys_type
from .utils import format_return_type
from .utils import get_import_from_info
from .utils import has_docstring
from .utils import indent
from .utils import is_builtin_type
from .utils import is_c_string
from .utils import is_private
from .utils import make_name
from .utils import mys_to_cpp_type
from .utils import mys_to_cpp_type_param
from .utils import split_full_name
from .value_check_type_visitor import ValueCheckTypeVisitor


def make_test_name(name):
    return f'mys_test_{name}'

def create_coverage_exit(module_path, coverage_variables):
    code = [
        '#if defined(MYS_COVERAGE)',
        f'    mys::mys_coverage_file << "File: {module_path}" << "\\n";'
    ]

    for lineno, variable in coverage_variables:
        code.append(
            f'    mys::mys_coverage_file << {lineno} << " " << {variable} << "\\n";')

    code.append('#endif')

    return code


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
        '        mys::make_shared<ValueError>('
        f'mys::String("enum {enum.name} does not contain ") + '
        'mys::String(value))->__throw();',
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
                 version,
                 source_lines,
                 definitions,
                 module_definitions,
                 skip_tests,
                 specialized_functions,
                 specialized_classes,
                 coverage_variables):
        self.module_levels = module_levels
        self.module_hpp = module_hpp
        self.filename = filename
        self.version = version
        self.skip_tests = skip_tests
        self.namespace = namespace
        self.add_package_main = False
        self.before_namespace = []
        self.in_namespace = []
        self.context = Context(module_levels,
                               specialized_functions,
                               specialized_classes,
                               source_lines)
        self.definitions = definitions
        self.module_definitions = module_definitions
        self.enums = []
        self.body = []
        self.variables = []
        self.init_globals = []
        self.method_comprehensions = self.context.method_comprehensions
        self.macros = self.context.macros
        self.coverage_exit = create_coverage_exit(filename, coverage_variables)

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
                enum)
            self.enums += create_enum_from_integer(enum)

    def define_parameters(self, args):
        for param, node in args:
            if isinstance(param.type, GenericType):
                param_type = add_generic_class(param.type.node, self.context)[1]
            else:
                param_type = param.type

            self.raise_if_type_not_defined(param_type, param.node.annotation)
            self.context.define_local_variable(param.name, param_type, node)

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

    def add_application_exit(self, ordered_modules):
        body = []

        for module in ordered_modules:
            self.before_namespace += [
                f'namespace mys::{module.replace(".", "::")} {{',
                'extern void __module_exit();',
                '}'
            ]
            body.append(f'    mys::{module.replace(".", "::")}::__module_exit();')

        body += [
            '#if defined(MYS_COVERAGE)',
            '    mys::mys_coverage_file.close();',
            '#endif'
        ]

        self.before_namespace += [
            'void __application_exit(void)',
            '{'
        ] + body + [
            '}'
        ]

    def raise_if_type_not_defined(self, mys_type, node):
        if not self.context.is_type_defined(mys_type):
            raise CompileError(f"undefined type '{mys_type}'", node)

    def visit_AnnAssign(self, node):
        return GlobalVariableVisitor(self.context, '', '').visit(node)

    def visit_variable(self, variable):
        mys_type = TypeVisitor(self.context).visit(variable.node.annotation)
        cpp_type = mys_to_cpp_type(mys_type, self.context)

        return [f'{cpp_type} {variable.name};']

    def visit_global_variable(self, node, body, next_index):
        docstring = None

        if len(body) > next_index:
            docstring_node = body[next_index]

            if isinstance(docstring_node, ast.Expr):
                if isinstance(docstring_node.value, ast.Constant):
                    if isinstance(docstring_node.value.value, str):
                        docstring = docstring_node.value.value

        self.init_globals += GlobalVariableVisitor(self.context, '', '').visit(node)

        return docstring is not None

    def visit_Module(self, node):
        body_iter = iter(node.body)
        item_index = 0

        for item in body_iter:
            if isinstance(item, ast.AnnAssign):
                if self.visit_global_variable(item, node.body, item_index + 1):
                    next(body_iter)
                    item_index += 1
            else:
                self.init_globals += self.visit(item)

            item_index += 1

        for name, definitions in self.module_definitions.classes.items():
            if definitions.is_generic():
                continue

            self.body += self.visit_class_definition(name, definitions)

        for functions in self.module_definitions.functions.values():
            for function in functions:
                if function.is_generic():
                    continue

                self.body += self.visit_function_defaults(function)

                if function.is_macro:
                    self.macros.append(self.visit_macro_definition(function))
                elif function.is_iterator:
                    self.visit_iterator_definition(function)
                else:
                    self.body += self.visit_function_definition(function)

        for variable in self.module_definitions.variables.values():
            self.variables += self.visit_variable(variable)

        if not self.skip_tests:
            for test in self.module_definitions.tests.values():
                self.body += self.visit_test_definition(test)

    def visit_specialized_function(self, function):
        self.body += self.visit_function_defaults(function)
        self.body += self.visit_function_definition(function)

    def visit_specialized_class(self, name, definitions):
        self.context.define_class(name,
                                  self.context.make_full_name_this_module(name),
                                  definitions)
        self.body += self.visit_class_definition(name, definitions)

    def format_cpp(self):
        traceback_entries = ',\n'.join([
            f'    {{ "{name}", {lineno}, "{code}" }}'
            for name, lineno, code in self.context.traceback.entries
        ])
        return '\n'.join([
            '// This file was generated by mys. DO NOT EDIT!!!',
            '#include "mys.hpp"',
            f'#include "{self.module_hpp}"'
        ] + self.before_namespace + [
            f'namespace {self.namespace}',
            '{',
            'static mys::TracebackEntryInfo __traceback_entries_info[] = {',
            traceback_entries,
            '};',
            'static mys::TracebackModuleInfo __traceback_module_info = {',
            f'   .path_p = "{self.filename}",',
            '   .entries_info_p = &__traceback_entries_info[0]',
            '};'
        ] + self.in_namespace
          + self.enums
          + [constant[1] for constant in self.context.constants.values()]
          + self.context.comprehensions
          + self.variables
          + self.body + [
              'void __module_init()',
              '{'
          ] + self.init_globals + [
              '}',
              'void __module_exit()',
              '{'
          ] + self.coverage_exit + [
              '}',
              '}'
          ] + self.main())

    def main(self):
        if self.add_package_main:
            return [
                'void package_main(int argc, char * const argv[])',
                '{',
                f'    {self.namespace}::main(argc, argv);',
                '}'
            ]
        else:
            return []

    def define_implicitly_imported_types(self, mys_type):
        if isinstance(mys_type, Tuple):
            for item_mys_type in mys_type:
                self.define_implicitly_imported_types(item_mys_type)
        elif isinstance(mys_type, list):
            self.define_implicitly_imported_types(mys_type[0])
        elif isinstance(mys_type, Set):
            self.define_implicitly_imported_types(mys_type.value_type)
        elif isinstance(mys_type, Dict):
            self.define_implicitly_imported_types(mys_type.key_type)
            self.define_implicitly_imported_types(mys_type.value_type)
        elif isinstance(mys_type, GenericType):
            # ToDo, but what should be done?
            pass
        elif isinstance(mys_type, Optional):
            self.define_implicitly_imported_types(mys_type.mys_type)
        elif isinstance(mys_type, Weak):
            self.define_implicitly_imported_types(mys_type.mys_type)
        elif '.' in mys_type:
            module, name = split_full_name(mys_type)
            imported = self.definitions.get(module)

            if imported is None:
                raise Exception(f"imported module '{module}' not found")
            elif name in imported.classes:
                self.define_imported_class(mys_type,
                                           mys_type,
                                           imported.classes[name])
            elif name in imported.traits:
                self.context.define_trait(mys_type, mys_type, imported.traits[name])

    def define_imported_function_parameters_and_return_type(self, function):
        if function.returns is not None:
            self.define_implicitly_imported_types(function.returns)

        for param, _ in function.args:
            self.define_implicitly_imported_types(param.type)

    def define_imported_class_member(self, member):
        self.define_implicitly_imported_types(member.type)

    def visit_ImportFrom(self, node):
        module, name, asname = get_import_from_info(node, self.module_levels)
        imported_module = self.definitions.get(module)

        if imported_module is None:
            raise CompileError(f"imported module '{module}' does not exist", node)

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
                self.define_imported_function_parameters_and_return_type(function)

            self.context.define_function(asname,
                                         full_name,
                                         imported_module.functions[name])
        elif name in imported_module.classes:
            self.define_imported_class(asname,
                                       full_name,
                                       imported_module.classes[name])
        elif name in imported_module.traits:
            self.context.define_trait(asname,
                                      full_name,
                                      imported_module.traits[name])
        elif name in imported_module.enums:
            self.context.define_enum(asname,
                                     full_name,
                                     imported_module.enums[name])
        else:
            raise CompileError(
                f"imported module '{module}' does not contain '{name}'",
                node)

        return []

    def define_imported_class(self, asname, full_name, class_definitions):
        if self.context.is_class_defined(asname):
            return

        self.context.define_class(asname, full_name, class_definitions)

        for methods in class_definitions.methods.values():
            for method in methods:
                self.define_imported_function_parameters_and_return_type(method)

        for member in class_definitions.members.values():
            self.define_imported_class_member(member)

    def visit_ClassDef(self, _node):
        return []

    def visit_defaults(self, name, args):
        code = []

        for param, default in args:
            if default is None:
                continue

            cpp_type = mys_to_cpp_type(param.type, self.context)
            body = ValueCheckTypeVisitor(
                BaseVisitor(self.context,
                            self.filename,
                            self.version)).visit(default, param.type)

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

    def visit_class_methods_definition(self, class_name, methods_definitions):
        body = []
        self.context.class_name = class_name

        for method in methods_definitions:
            if method.is_macro:
                self.visit_class_macro_definition(class_name, method)
            elif method.is_iterator:
                self.visit_class_iterator_definition(class_name, method)
            else:
                self.visit_class_method_definition(class_name, method, body)

        self.context.class_name = None

        return body

    def visit_class_method_definition(self, class_name, method, body):
        self.context.is_macro = False
        body += self.visit_method_defaults(method, class_name)
        self.context.push()
        self.context.define_local_variable(
            'self',
            self.context.make_full_name_this_module(class_name),
            method.node.args.args[0])
        self.define_parameters(method.args)
        self.raise_if_type_not_defined(method.returns, method.node.returns)
        check_returns(method)
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

        if method.name != '__del__':
            body.append(self.context.traceback.enter(method.name))

        body_iter = iter(method.node.body)

        if has_docstring(method.node):
            next(body_iter)

        for item in body_iter:
            BodyCheckVisitor().visit(item)

            if method.name != '__del__':
                body.append(self.context.traceback.set(item.lineno))

            body.append(indent(BodyVisitor(self.context,
                                           self.filename,
                                           self.version).visit(item)))

        if method.name != '__del__':
            body.append(self.context.traceback.exit())

        body.append('}')
        self.context.pop()

    def visit_class_macro_definition(self, class_name, method):
        self.context.push()
        self.context.is_macro = True
        self.context.define_local_variable(
            'self',
            self.context.make_full_name_this_module(class_name),
            method.node.args.args[0])
        self.define_parameters(method.args)
        self.raise_if_type_not_defined(method.returns, method.node.returns)
        check_returns(method)
        namespace = '__'.join(self.module_levels)
        name = format_method_name(method, class_name)
        macro_name = f'mys__{namespace}__{class_name}__{name}'
        format_parameters(method.args, self.context)
        parameters = ['__self__'] + [make_name(arg.name) for arg, _ in method.args]
        self.context.return_mys_type = method.returns
        body = [
            f'#define {macro_name}({", ".join(parameters)})',
            '{'
        ]
        body_iter = iter(method.node.body)

        if has_docstring(method.node):
            next(body_iter)

        for item in body_iter:
            BodyCheckVisitor().visit(item)
            body += indent(BodyVisitor(self.context,
                                       self.filename,
                                       self.version).visit(item)).splitlines()

        body.append('}')
        self.context.pop()
        self.macros.append(' \\\n'.join(body))

    def visit_class_iterator_definition(self, _class_name, method):
        raise CompileError("iterators are not yet implemented", method.node)

    def visit_class_definition(self, class_name, definitions):
        member_cpp_types = []
        member_names = []
        body = []

        for member in definitions.members.values():
            if isinstance(member.type, GenericType):
                member_type = add_generic_class(member.type.node, self.context)[1]
            else:
                member_type = member.type

            if isinstance(member_type, Weak):
                if is_builtin_type(member_type.mys_type):
                    raise CompileError(
                        f"builtin type '{format_mys_type(member_type.mys_type)}' "
                        f"cannot be weak",
                        member.node.annotation)
                elif self.context.is_enum_defined(member_type.mys_type):
                    raise CompileError(
                        f"enum '{format_mys_type(member_type.mys_type)}' cannot "
                        f"be weak",
                        member.node.annotation)

            if not self.context.is_type_defined(member_type):
                raise CompileError(f"undefined type '{member_type}'",
                                   member.node.annotation)

            member_cpp_types.append(mys_to_cpp_type_param(member_type, self.context))
            member_names.append(member.name)

        for methods in definitions.methods.values():
            body += self.visit_class_methods_definition(class_name, methods)

        if 'Error' in (implement.name() for implement in definitions.implements):
            body += [
                f'void {class_name}::__throw()',
                '{',
                f'    throw __{class_name}(mys::shared_ptr<{class_name}>(this));',
                '}'
            ]

        return body

    def visit_FunctionDef(self, _node):
        return []

    def visit_function_defaults(self, function):
        return self.visit_defaults(function.make_name(), function.args)

    def visit_function_definition_main(self, function, parameters, body):
        self.add_package_main = True

        if parameters not in ['mys::shared_ptr<mys::List<mys::String>> argv', 'void']:
            raise CompileError("main() takes 'argv: [string]' or no arguments",
                               function.node)

        if function.returns is not None:
            raise CompileError("main() must not return any value", function.node)

        if parameters == 'void':
            body = [
                '    (void)__argc;',
                '    (void)__argv;'
            ] + body
        else:
            body = ['    auto argv = create_args(__argc, __argv);'] + body

        parameters = 'int __argc, char * const __argv[]'

        return body, parameters

    def visit_function_definition(self, function):
        self.context.push()
        self.context.is_macro = False
        self.define_parameters(function.args)
        self.raise_if_type_not_defined(function.returns, function.node.returns)
        check_returns(function)
        function_name = function.make_name()
        parameters = format_parameters(function.args, self.context)
        return_cpp_type = format_return_type(function.returns, self.context)
        self.context.return_mys_type = function.returns
        body = [self.context.traceback.enter(function.name)]
        body_iter = iter(function.node.body)

        if has_docstring(function.node):
            next(body_iter)

        for item in body_iter:
            BodyCheckVisitor().visit(item)
            body.append(self.context.traceback.set(item.lineno))
            body.append(indent(BodyVisitor(self.context,
                                           self.filename,
                                           self.version).visit(item)))

        body.append(self.context.traceback.exit())

        if function_name == 'main':
            body, parameters = self.visit_function_definition_main(function,
                                                                   parameters,
                                                                   body)

        code = [
            f'{return_cpp_type} {function_name}({parameters})',
            '{'
        ] + body + [
            '}'
        ]

        self.context.pop()

        return code

    def visit_macro_definition(self, function):
        self.context.push()
        self.context.is_macro = True
        self.define_parameters(function.args)
        self.raise_if_type_not_defined(function.returns, function.node.returns)
        check_returns(function)
        namespace = '__'.join(self.module_levels)
        macro_name = f'mys__{namespace}__{function.make_name()}'
        format_parameters(function.args, self.context)
        parameters = [make_name(arg.name) for arg, _ in function.args]
        self.context.return_mys_type = function.returns
        body_iter = iter(function.node.body)

        if has_docstring(function.node):
            next(body_iter)

        body = []

        for item in body_iter:
            BodyCheckVisitor().visit(item)
            body += indent(BodyVisitor(self.context,
                                       self.filename,
                                       self.version).visit(item)).splitlines()

        code = [
            f'#define {macro_name}({", ".join(parameters)})',
            '{'
        ] + body + [
            '}'
        ]

        self.context.pop()

        return ' \\\n'.join(code)

    def visit_iterator_definition(self, function):
        raise CompileError("iterators are not yet implemented", function.node)

    def visit_test_definition(self, function):
        self.context.push()

        self.context.return_mys_type = None
        body = [self.context.traceback.enter(function.name)]
        body_iter = iter(function.node.body)

        if has_docstring(function.node):
            next(body_iter)

        for item in body_iter:
            BodyCheckVisitor().visit(item)
            body.append(self.context.traceback.set(item.lineno))
            body.append(indent(BodyVisitor(self.context,
                                           self.filename,
                                           self.version).visit(item)))

        body.append(self.context.traceback.exit())
        namespace = '::'.join(self.module_levels[1:])
        test_name = make_test_name(function.name)
        code = [
            '#if defined(MYS_TEST)',
            f'static void {test_name}(void)',
            '{'
        ] + body + [
            '}',
            f'static Test __{test_name}("{namespace}::{function.name}", '
            f'{test_name});',
            '#endif'
        ]

        self.context.pop()

        return code

    def visit_Expr(self, node):
        return self.visit(node.value) + [';']

    def visit_Constant(self, node):
        if is_c_string(node.value):
            value = node.value[0]

            if value.startswith('source-before-namespace'):
                self.before_namespace += [
                    '/* c-string-source-before-namespace start */',
                    textwrap.dedent(value[23:]).strip(),
                    '/* c-string-source-before-namespace stop */'
                ]
            elif value.startswith('header-before-namespace'):
                pass
            else:
                self.in_namespace += [
                    '/* c-string start */',
                    textwrap.dedent(value).strip(),
                    '/* c-string stop */']

            return []

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
