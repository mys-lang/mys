import copy

from ..parser import ast
from .definitions import Class
from .definitions import Function
from .utils import CompileError
from .utils import InternalError
from .utils import split_dict_mys_type


def replace_generic_types(generic_types, mys_type, chosen_types):
    if isinstance(mys_type, str):
        for generic_type, chosen_type in zip(generic_types, chosen_types):
            if mys_type == generic_type:
                return chosen_type

    return mys_type


class SpecializeGenericType:

    def __init__(self, generic_type, chosen_type, node=None):
        self.generic_type = generic_type
        self.chosen_type = chosen_type
        self.node = node

    def replace(self, mys_type):
        """Replaces all occurrences of generic types with chosen types.

        """

        if isinstance(mys_type, str):
            if mys_type == self.generic_type:
                mys_type = self.chosen_type
        elif isinstance(mys_type, dict):
            key_mys_type, value_mys_type = split_dict_mys_type(mys_type)
            mys_type = {self.replace(key_mys_type): self.replace(value_mys_type)}
        elif isinstance(mys_type, list):
            mys_type = [self.replace(mys_type[0])]
        elif isinstance(mys_type, tuple):
            mys_type = tuple(self.replace(item_mys_type)
                             for item_mys_type in mys_type)
        else:
            raise Exception('generic type not supported')

        return mys_type


class SpecializeTypeTransformer(ast.NodeTransformer):
    """Traverses given generic node and replaces given generic types with
    given chosen types.

    """

    def __init__(self, generic_types, chosen_types):
        self.generic_to_specialized_type = dict(zip(generic_types, chosen_types))

    def visit_Name(self, node):
        node.id = self.generic_to_specialized_type.get(node.id, node.id)

        return node


def specialize_function(function, specialized_full_name, chosen_types, node):
    """Returns a copy of the function object with all generic types
    replaced with chosen types.

    """

    returns = function.returns
    args = copy.deepcopy(function.args)
    actual_ntypes = len(chosen_types)
    expected_ntypes = len(function.generic_types)

    if actual_ntypes != expected_ntypes:
        raise CompileError(
            f'expected {expected_ntypes} type, got {actual_ntypes}',
            node.func.slice)

    for generic_type, chosen_type in zip(function.generic_types, chosen_types):
        if returns is not None:
            returns = SpecializeGenericType(generic_type,
                                            chosen_type,
                                            function.node).replace(returns)

        for param, _ in args:
            param.type = SpecializeGenericType(generic_type,
                                               chosen_type,
                                               function.node).replace(param.type)

    node = copy.deepcopy(function.node)
    node.name = specialized_full_name
    node = SpecializeTypeTransformer(function.generic_types,
                                     chosen_types).visit(node)

    return Function(specialized_full_name,
                    [],
                    function.raises,
                    function.is_test,
                    args,
                    returns,
                    node,
                    function.module_name)


def specialize_class(definitions, specialized_name, chosen_types, node):
    """Returns a copy of the class object with all generic types replaced
    with chosen types.

    """

    members = copy.deepcopy(definitions.members)
    methods = copy.deepcopy(definitions.methods)
    actual_ntypes = len(chosen_types)
    expected_ntypes = len(definitions.generic_types)

    if actual_ntypes != expected_ntypes:
        raise CompileError(
            f'expected {expected_ntypes} type, got {actual_ntypes}',
            node.func.slice)

    for generic_type, chosen_type in zip(definitions.generic_types, chosen_types):
        for member in members.values():
            member.type = SpecializeGenericType(generic_type,
                                                chosen_type).replace(member.type)

        for class_methods in methods.values():
            for method in class_methods:
                if method.returns is not None:
                    method.returns = SpecializeGenericType(
                        generic_type,
                        chosen_type).replace(method.returns)

                for param, _node in method.args:
                    param.type = SpecializeGenericType(
                        generic_type,
                        chosen_type).replace(param.type)

                method.node = SpecializeTypeTransformer(
                    definitions.generic_types,
                    chosen_types).visit(method.node)

    return Class(specialized_name,
                 [],
                 members,
                 methods,
                 definitions.functions,
                 definitions.implements,
                 definitions.node,
                 definitions.module_name)


def generic_class_setup(node, context):
    name = node.func.value.id
    full_name = context.make_full_name(name)
    types_slice = node.func.slice
    chosen_types = []

    if isinstance(types_slice, ast.Name):
        type_name = types_slice.id

        if context.is_class_defined(type_name):
            type_name = context.make_full_name(type_name)

        chosen_types.append(type_name)
    elif isinstance(types_slice, ast.Tuple):
        for item in types_slice.elts:
            if not isinstance(item, ast.Name):
                raise CompileError('unsupported generic type', node)

            type_name = item.id

            if context.is_class_defined(type_name):
                type_name = context.make_full_name(type_name)

            chosen_types.append(type_name)
    else:
        raise InternalError('invalid specialization of generic class', node)

    joined_chosen_types = '_'.join([
        chosen_type.replace('.', '_')
        for chosen_type in chosen_types
    ])
    definitions = context.get_class_definitions(full_name)
    specialized_name = f'{name}_{joined_chosen_types}'
    specialized_full_name = f'{full_name}_{joined_chosen_types}'

    if context.is_specialized_class_defined(specialized_full_name):
        specialized_class = context.get_specialized_class(
            specialized_full_name)
    else:
        specialized_class = specialize_class(definitions,
                                             specialized_name,
                                             chosen_types,
                                             node)
        context.define_specialized_class(specialized_full_name,
                                         specialized_class,
                                         node)
        context.define_class(specialized_name,
                             specialized_full_name,
                             specialized_class)

    return specialized_class, specialized_full_name
