from .base import BaseVisitor
from .context import Context
from .generics import TypeVisitor
from .generics import add_generic_class
from .generics import format_parameters
from .utils import METHOD_OPERATORS
from .utils import CompileError
from .utils import GenericType
from .utils import dot2ns
from .utils import format_default
from .utils import format_method_name
from .utils import format_return_type
from .utils import get_import_from_info
from .utils import indent_lines
from .utils import make_name


class HeaderVisitor(BaseVisitor):
    """The header visitor generates C++ code from given AST.

    """

    def __init__(self,
                 namespace,
                 module_levels,
                 module_hpp,
                 source_lines,
                 definitions,
                 module_definitions,
                 has_main,
                 specialized_classes):
        super().__init__(Context(module_levels,
                                 {},
                                 specialized_classes,
                                 source_lines),
                         '')
        self.namespace = namespace
        self.module_levels = module_levels
        self.module_hpp = module_hpp
        self.early_includes = set()
        self.includes = set()
        self.imported = set()
        self.traits = []
        self.variables = []
        self.definitions = definitions
        self.module_definitions = module_definitions
        self.has_main = has_main
        self.forward = []
        self.classes = []
        self.functions = []
        self.enums = []

        for name, trait_definitions in module_definitions.traits.items():
            full_name = self.context.make_full_name_this_module(name)
            self.context.define_trait(name, full_name, trait_definitions)

            if full_name == 'fiber.lib.Fiber':
                continue

            self.forward.append(f'class {name};')

        for name, class_definitions in module_definitions.classes.items():
            self.context.define_class(name,
                                      self.context.make_full_name_this_module(name),
                                      class_definitions)
            self.forward.append(f'class {name};')

        for enum in module_definitions.enums.values():
            self.context.define_enum(
                enum.name,
                self.context.make_full_name_this_module(enum.name),
                enum.type)

        for name, variable_definitions in module_definitions.variables.items():
            TypeVisitor(self.context).visit(variable_definitions.node.annotation)

    def visit_trait_declaration(self, name, definitions):
        methods = []

        for methods_definitions in definitions.methods.values():
            for method in methods_definitions:
                if method.name == '__init__':
                    raise CompileError("traits cannot have an __init__ method",
                                       method.node)

                parameters = format_parameters(method.args, self.context)
                return_type = format_return_type(method.returns, self.context)

                methods.append(
                    f'    virtual {return_type} {method.name}({parameters}) = 0;')

        self.traits += [
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

    def visit_class_declaration_bases(self, definitions):
        bases = []

        for trait_name, _trait_node in definitions.implements.items():
            bases.append(f'public {dot2ns(trait_name)}')

        bases = ', '.join(bases)

        if not bases:
            bases = 'public Object'

        return bases

    def visit_class_declaration_members(self, definitions):
        members = []

        for member in definitions.members.values():
            if isinstance(member.type, GenericType):
                member_type = add_generic_class(member.type.node, self.context)[1]
            else:
                member_type = member.type

            cpp_type = self.mys_to_cpp_type(member_type)
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

                    if isinstance(param.type, GenericType):
                        param_type = add_generic_class(param.type.node,
                                                       self.context)[1]
                    else:
                        param_type = param.type

                    cpp_type = self.mys_to_cpp_type(param_type)
                    defaults.append(format_default(f'{class_name}_{method_name}',
                                                   param.name,
                                                   cpp_type) + ';')

                if method.name in METHOD_OPERATORS:
                    self.validate_operator_signature(class_name,
                                                     method.name,
                                                     method.returns,
                                                     method.node)

                method_name = format_method_name(method, class_name)
                parameters = format_parameters(method.args, self.context)

                if method_name  == class_name:
                    methods.append(f'{method_name}({parameters});')
                elif method_name  == f'~{class_name}':
                    methods.append(f'virtual {method_name}({parameters});')
                else:
                    return_cpp_type = format_return_type(method.returns, self.context)
                    methods.append(f'{return_cpp_type} {method_name}({parameters});')

        return methods, defaults

    def visit_class_declaration(self, name, definitions):
        bases = self.visit_class_declaration_bases(definitions)
        members = self.visit_class_declaration_members(definitions)
        methods, defaults = self.visit_class_declaration_methods(name, definitions)

        if 'Error' in definitions.implements:
            methods.append('[[ noreturn ]] void __throw();')

        for functions in definitions.functions.values():
            for function in functions:
                raise CompileError("class functions are not yet implemented",
                                   function.node)

        self.classes += defaults + [
            f'class {name} : {bases}, public std::enable_shared_from_this<{name}> {{',
            'public:'
        ] + indent_lines(members + methods) + [
            '};'
        ]

        if 'Error' in definitions.implements:
            self.classes += [
                f'class __{name} final : public __Error {{',
                'public:',
                f'    __{name}(const std::shared_ptr<{name}>& error) : '
                '__Error(error)',
                '    {',
                '    }',
                '};'
            ]

    def visit_enum_declaration(self, definitions):
        name = definitions.name
        cpp_type = definitions.type
        members = [
            f"    {name} = {value},"
            for name, value in definitions.members
        ]

        self.enums += [
            f'enum class {name} : {cpp_type} {{'
        ] + members + [
            '};',
            f'{cpp_type} {name}_from_value({cpp_type} value);'
        ]

    def visit_variable(self, variable):
        mys_type = TypeVisitor(self.context).visit(variable.node.annotation)
        cpp_type = self.mys_to_cpp_type(mys_type)

        return [f'extern {cpp_type} {variable.name};']

    def visit_function_declaration(self, function):
        parameters = format_parameters(function.args, self.context)
        return_type = format_return_type(function.returns, self.context)
        code = []
        function_name = function.make_name()

        for param, default in function.args:
            if default is None:
                continue

            cpp_type = self.mys_to_cpp_type(param.type)
            code.append(format_default(function_name, param.name, cpp_type) + ';')

        if function_name != 'main' and not function.is_test:
            code.append(f'{return_type} {function_name}({parameters});')

        return code

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

        for name, trait_definitions in self.module_definitions.traits.items():
            full_name = self.context.make_full_name_this_module(name)

            if full_name == 'fiber.lib.Fiber':
                continue

            self.visit_trait_declaration(name, trait_definitions)

        for name, class_definitions in self.module_definitions.classes.items():
            if class_definitions.is_generic():
                continue

            self.visit_class_declaration(name, class_definitions)

        for name, enum_definitions in self.module_definitions.enums.items():
            self.visit_enum_declaration(enum_definitions)

        main_found = False

        for functions_definitions in self.module_definitions.functions.values():
            for function in functions_definitions:
                if function.name == 'main':
                    main_found = True

                if function.is_generic():
                    continue

                self.functions += self.visit_function_declaration(function)

        if self.has_main and not main_found:
            raise Exception('main() not found in main.mys')
        elif main_found and not self.has_main:
            raise Exception('main() is only allowed in main.mys')

        for variable in self.module_definitions.variables.values():
            self.variables += self.visit_variable(variable)

    def visit_specialized_function(self, function):
        self.functions += self.visit_function_declaration(function)

    def visit_specialized_class(self, definitions):
        self.forward.append(f'class {definitions.name};')
        self.visit_class_declaration(definitions.name, definitions)

    def format_early_hpp(self):
        return '\n'.join([
            '// This file was generated by mys. DO NOT EDIT!!!',
            '#pragma once',
        ] + list(self.early_includes) + [
            f'namespace {self.namespace}',
            '{'
        ] + self.forward
          + self.enums
          + self.traits
          + list(self.imported)
          + self.variables
          + self.functions + [
            '}'
        ])

    def format_hpp(self):
        return '\n'.join([
            '// This file was generated by mys. DO NOT EDIT!!!',
            '#pragma once',
            f'#include "{self.module_hpp[:-4]}.early.hpp"'
        ] + list(self.includes) + [
            f'namespace {self.namespace}',
            '{'
        ] + self.classes + [
            '}'
        ])

    def visit_ImportFrom(self, node):
        module, name, asname = get_import_from_info(node, self.module_levels)
        module_hpp = module.replace('.', '/')
        self.early_includes.add(f'#include "{module_hpp}.mys.early.hpp"')
        self.includes.add(f'#include "{module_hpp}.mys.hpp"')
        imported_module = self.definitions.get(module)

        if imported_module is None:
            raise CompileError(f"imported module '{module}' does not exist", node)

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
