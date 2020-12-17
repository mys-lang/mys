from .utils import CompileError
from .utils import Context
from .utils import BaseVisitor
from .utils import get_import_from_info
from .utils import params_string
from .utils import indent
from .utils import mys_to_cpp_type
from .utils import METHOD_OPERATORS
from .utils import is_primitive_type

class HeaderVisitor(BaseVisitor):

    def __init__(self,
                 namespace,
                 module_levels,
                 source_lines,
                 definitions,
                 module_definitions):
        super().__init__(source_lines, Context(), 'todo')
        self.namespace = namespace
        self.module_levels = module_levels
        self.includes = set()
        self.imported = set()
        self.prefix = namespace.replace('::', '_').upper()
        self.traits = []
        self.functions = []
        self.variables = []
        self.definitions = definitions
        self.module_definitions = module_definitions

        for name, trait_definitions in module_definitions.traits.items():
            self.context.define_trait(name, trait_definitions)
            self.traits.append(f'class {name};')

        self.classes = []

        for name, class_definitions in module_definitions.classes.items():
            self.context.define_class(name, class_definitions)
            self.classes.append(
                f'class {name};\n'
                f'#define {self.prefix}_{name}_IMPORT_AS(__name__) \\\n'
                f'    using __name__ = {self.namespace}::{name};')

        for enum in module_definitions.enums.values():
            self.context.define_enum(enum.name, enum.type)

        for functions in module_definitions.functions.values():
            for function in functions:
                self.functions += self.visit_function(function)

        for variable in module_definitions.variables.values():
            self.variables.append(self.visit_variable(variable))

    def visit_trait_declaration(self, name, definitions):
        methods = []

        for methods_definitions in definitions.methods.values():
            for method in methods_definitions:
                parameters = []

                for param_name, param_mys_type in method.args:
                    cpp_type = mys_to_cpp_type(param_mys_type, self.context)
                    parameters.append(f'{cpp_type} {param_name}')

                parameters = ', '.join(parameters)

                if method.returns is not None:
                    return_cpp_type = mys_to_cpp_type(method.returns, self.context)
                else:
                    return_cpp_type = 'void'

                methods.append(
                    f'virtual {return_cpp_type} {method.name}({parameters}) = 0;')

        self.classes.append('\n'.join([
            f'class {name} : public Object {{',
            'public:',
            indent('\n'.join(methods)),
            '};'
        ]))

    def validate_operator_signature(self,
                                    class_name,
                                    method_name,
                                    return_type,
                                    node):
        expected_return_type = {
            '__add__': class_name,
            '__sub__': class_name,
            '__iadd__': None,
            '__isub__': None,
            '__eq__': 'bool',
            '__ne__': 'bool',
            '__gt__': 'bool',
            '__ge__': 'bool',
            '__lt__': 'bool',
            '__le__': 'bool'
        }[method_name]

        if return_type != expected_return_type:
            raise CompileError(
                f'{method_name}() must return {expected_return_type}',
                node)

    def visit_class_declaration(self, name, definitions):
        bases = []

        for implements in definitions.implements:
            bases.append(f'public {implements}')

        bases = ', '.join(bases)

        if not bases:
            bases = 'public Object'

        members = []

        for member in definitions.members.values():
            cpp_type = mys_to_cpp_type(member.type, self.context)
            members.append(f'{cpp_type} {member.name};')

        methods = []

        for methods_definitions in definitions.methods.values():
            for method in methods_definitions:
                if method.name in METHOD_OPERATORS:
                    self.validate_operator_signature(name,
                                                     method.name,
                                                     method.returns,
                                                     method.node)
                    method_name = 'operator' + METHOD_OPERATORS[method.name]
                else:
                    method_name = method.name

                parameters = []

                for param_name, param_mys_type in method.args:
                    cpp_type = mys_to_cpp_type(param_mys_type, self.context)

                    if is_primitive_type(param_mys_type):
                        parameters.append(f'{cpp_type} {param_name}')
                    else:
                        parameters.append(f'const {cpp_type}& {param_name}')

                parameters = ', '.join(parameters)

                if method.returns is not None:
                    return_cpp_type = mys_to_cpp_type(method.returns, self.context)
                else:
                    return_cpp_type = 'void'

                methods.append(f'{return_cpp_type} {method_name}({parameters});')

        if '__init__' not in definitions.methods:
            parameters = []

            for member in definitions.members.values():
                if member.name.startswith('_'):
                    continue

                cpp_type = mys_to_cpp_type(member.type, self.context)
                parameters.append(f'{cpp_type} {member.name}')

            parameters = ', '.join(parameters)
            methods.append(f'{name}({parameters});')

        if '__del__' not in definitions.methods:
            methods.append(f'virtual ~{name}();')

        if '__str__' not in definitions.methods:
            methods.append('String __str__() const;')

        self.classes.append('\n'.join([
            f'class {name} : {bases} {{',
            'public:',
            indent('\n'.join(members + methods)),
            '};'
        ]))
        self.classes.append(
            f'std::ostream& operator<<(std::ostream& os, const {name}& obj);')

    def visit_variable(self, variable):
        cpp_type = self.visit_cpp_type(variable.node.annotation)

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
            code.append('\n'.join([
                f'{return_type} {function.name}({params});',
                f'#define {self.prefix}_{function.name}_IMPORT_AS(__name__) \\',
                f'    constexpr auto __name__ = [] (auto &&...args) {{ \\',
                f'        return {self.namespace}::{function.name}(std::forward<'
                f'decltype(args)>(args)...); \\',
                f'    }};'
            ]))

        return code

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

        for name, trait_definitions in self.module_definitions.traits.items():
            self.visit_trait_declaration(name, trait_definitions)

        for name, class_definitions in self.module_definitions.classes.items():
            self.visit_class_declaration(name, class_definitions)

        return '\n'.join([
            '// This file was generated by mys. DO NOT EDIT!!!',
            '',
            '#pragma once',
            '',
            '#include "mys.hpp"'
        ] + list(self.includes) + [
            '',
            f'namespace {self.namespace}',
            '{'
        ] + self.traits
          + list(self.imported)
          + self.classes
          + self.variables
          + self.functions + [
              '}',
              ''
          ])

    def visit_Import(self, node):
        raise CompileError('use from ... import ...', node)

    def visit_ImportFrom(self, node):
        module, name, asname = get_import_from_info(node, self.module_levels)
        module_hpp = module.replace('.', '/')
        self.includes.add(f'#include "{module_hpp}.mys.hpp"')
        prefix = 'MYS_' + module.replace('.', '_').upper()
        self.imported.add(f'{prefix}_{name.name}_IMPORT_AS({asname});')
        imported_module = self.definitions.get(module)

        if imported_module is None:
            raise CompileError(f"imported module '{module}' does not exist", node)

        if name.name in imported_module.classes:
            self.context.define_class(asname,
                                      imported_module.classes[name.name])

    def visit_ClassDef(self, node):
        pass

    def visit_AnnAssign(self, node):
        pass

    def visit_FunctionDef(self, node):
        pass
