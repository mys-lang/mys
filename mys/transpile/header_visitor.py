from .utils import CompileError
from .context import Context
from .base import BaseVisitor
from .base import get_import_from_info
from .base import indent_lines
from .base import mys_to_cpp_type
from .base import mys_to_cpp_type_param
from .base import METHOD_OPERATORS
from .base import make_name
from .base import format_parameters
from .base import format_return_type
from .base import format_method_name
from .base import dot2ns

class HeaderVisitor(BaseVisitor):

    def __init__(self,
                 namespace,
                 module_levels,
                 source_lines,
                 definitions,
                 module_definitions,
                 has_main):
        super().__init__(source_lines, Context(module_levels), 'todo')
        self.namespace = namespace
        self.module_levels = module_levels
        self.includes = set()
        self.imported = set()
        self.prefix = namespace.replace('::', '_').upper()
        self.traits = []
        self.variables = []
        self.definitions = definitions
        self.module_definitions = module_definitions
        self.has_main = has_main

        for name, trait_definitions in module_definitions.traits.items():
            self.context.define_trait(name,
                                      self.context.make_full_name_this_module(name),
                                      trait_definitions)
            self.traits.append(f'class {name};')

        self.classes = []

        for name, class_definitions in module_definitions.classes.items():
            self.context.define_class(name,
                                      self.context.make_full_name_this_module(name),
                                      class_definitions)
            self.classes.append(f'class {name};')

        for enum in module_definitions.enums.values():
            self.context.define_enum(enum.name,
                                     self.context.make_full_name_this_module(enum.name),
                                     enum.type)

        for variable in module_definitions.variables.values():
            self.variables += self.visit_variable(variable)

    def visit_trait_declaration(self, name, definitions):
        methods = []

        for methods_definitions in definitions.methods.values():
            for method in methods_definitions:
                if method.name == '__init__':
                    raise CompileError("traits cannot have an __init__ method",
                                       method.node)

                parameters = []

                for param, _ in method.args:
                    cpp_type = mys_to_cpp_type_param(param.type, self.context)
                    parameters.append(f'{cpp_type} {make_name(param.name)}')

                parameters = ', '.join(parameters)

                if method.returns is not None:
                    return_cpp_type = mys_to_cpp_type(method.returns, self.context)
                else:
                    return_cpp_type = 'void'

                methods.append(
                    f'    virtual {return_cpp_type} {method.name}({parameters}) = 0;')

        self.classes += [
            f'class {name} : public Object {{',
            'public:'
        ] + methods + [
            '};'
        ]

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

    def raise_if_trait_does_not_exist(self, trait_name, trait_node):
        if not self.context.is_trait_defined(trait_name):
            raise CompileError('trait does not exist', trait_node)

    def visit_class_declaration_bases(self, definitions):
        class_methods = definitions.methods
        bases = []

        for trait_name, trait_node in definitions.implements.items():
            self.raise_if_trait_does_not_exist(trait_name, trait_node)
            bases.append(f'public {dot2ns(trait_name)}')

        bases = ', '.join(bases)

        if not bases:
            bases = 'public Object'

        return bases

    def visit_class_declaration_members(self, definitions):
        members = []

        for member in definitions.members.values():
            cpp_type = mys_to_cpp_type(member.type, self.context)
            members.append(f'{cpp_type} {make_name(member.name)};')

        return members

    def visit_class_declaration_methods(self, class_name, definitions):
        defaults = []
        methods = []
        method_names = []

        for methods_definitions in definitions.methods.values():
            for method in methods_definitions:
                method_names.append(method.name)

                for param, default in method.args:
                    if default is None:
                        continue

                    if method.name == '__init__':
                        method_name = class_name
                    else:
                        method_name = method.name

                    cpp_type = mys_to_cpp_type(param.type, self.context)
                    defaults.append(
                        f'{cpp_type} {class_name}_{method_name}_{param.name}_default();')

                if method.name in METHOD_OPERATORS:
                    self.validate_operator_signature(class_name,
                                                     method.name,
                                                     method.returns,
                                                     method.node)

                method_name = format_method_name(method, class_name)
                parameters = format_parameters(method.args, self.context)

                if method_name == class_name:
                    methods.append(f'{method_name}({parameters});')
                else:
                    return_cpp_type = format_return_type(method.returns, self.context)
                    methods.append(f'{return_cpp_type} {method_name}({parameters});')

        if '__init__' not in definitions.methods:
            parameters = []

            for member in definitions.members.values():
                if member.name.startswith('_'):
                    continue

                cpp_type = mys_to_cpp_type_param(member.type, self.context)
                parameters.append(f'{cpp_type} {make_name(member.name)}')

            parameters = ', '.join(parameters)
            methods.append(f'{class_name}({parameters});')

        if '__del__' not in definitions.methods:
            methods.append(f'virtual ~{class_name}();')

        if '__str__' not in definitions.methods:
            methods.append('String __str__() const;')

        return methods, defaults

    def visit_class_declaration(self, name, definitions):
        bases = self.visit_class_declaration_bases(definitions)
        members = self.visit_class_declaration_members(definitions)
        methods, defaults = self.visit_class_declaration_methods(name, definitions)

        for function_name, functions in definitions.functions.items():
            for function in functions:
                raise CompileError("class functions are not yet implemented",
                                   function.node)

        self.classes += defaults + [
            f'class {name} : {bases}, public std::enable_shared_from_this<{name}> {{',
            'public:'
        ] + indent_lines(members + methods) + [
            f'    void __format__(std::ostream& os) const;',
            '};'
        ]

    def visit_variable(self, variable):
        cpp_type = self.visit_cpp_type(variable.node.annotation)

        return [f'extern {cpp_type} {variable.name};']

    def visit_function_declaration(self, function):
        parameters = format_parameters(function.args, self.context)
        return_type = format_return_type(function.returns, self.context)
        code = []

        for param, default in function.args:
            if default is None:
                continue

            cpp_type = mys_to_cpp_type(param.type, self.context)
            code.append(f'{cpp_type} {function.name}_{param.name}_default();')

        if function.name != 'main' and not function.is_test:
            code.append(f'{return_type} {function.name}({parameters});')

        return code

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

        for name, trait_definitions in self.module_definitions.traits.items():
            self.visit_trait_declaration(name, trait_definitions)

        for name, class_definitions in self.module_definitions.classes.items():
            self.visit_class_declaration(name, class_definitions)

        main_found = False
        functions = []

        for functions_definitions in self.module_definitions.functions.values():
            for function in functions_definitions:
                if function.name == 'main':
                    main_found = True

                functions += self.visit_function_declaration(function)

        if self.has_main and not main_found:
            raise Exception('main() not found in main.mys')
        elif main_found and not self.has_main:
            raise Exception('main() is only allowed in main.mys')

        return '\n'.join([
            '// This file was generated by mys. DO NOT EDIT!!!',
            '#pragma once',
        ] + list(self.includes) + [
            f'namespace {self.namespace}',
            '{'
        ] + self.traits
          + list(self.imported)
          + self.classes
          + self.variables
          + functions + [
            '}'
        ])

        return header

    def visit_Import(self, node):
        raise CompileError('use from ... import ...', node)

    def visit_ImportFrom(self, node):
        module, name, asname = get_import_from_info(node, self.module_levels)
        module_hpp = module.replace('.', '/')
        self.includes.add(f'#include "{module_hpp}.mys.hpp"')
        imported_module = self.definitions.get(module)

        if imported_module is None:
            raise CompileError(f"imported module '{module}' does not exist", node)

        if asname is None:
            asname = name

        full_name = f'{module}.{name}'

        if name in imported_module.classes:
            self.context.define_class(asname,
                                      full_name,
                                      imported_module.classes[name])
        elif name in imported_module.traits:
            self.context.define_trait(asname,
                                      full_name,
                                      imported_module.traits[name])

    def visit_ClassDef(self, node):
        pass

    def visit_AnnAssign(self, node):
        pass

    def visit_FunctionDef(self, node):
        pass
