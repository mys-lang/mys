import copy
from ..parser import ast
from .definitions import Param
from .definitions import Function


def replace_generic_types(generic_types, mys_type, chosen_types):
    if isinstance(mys_type, str):
        for generic_type, chosen_type in zip(generic_types, chosen_types):
            if mys_type == generic_type:
                return chosen_type


def replace_generic_type(mys_type, generic_type, chosen_type):
    if isinstance(mys_type, str):
        if mys_type == generic_type:
            mys_type = chosen_type

    return mys_type


class SpecializeTypeTransformer(ast.NodeTransformer):

    def __init__(self, generic_types, chosen_types):
        self.generic_to_specialized_type = {
            generic_type: chosen_type
            for generic_type, chosen_type in zip(generic_types, chosen_types)
        }

    def visit_Name(self, node):
        node.id = self.generic_to_specialized_type.get(node.id, node.id)

        return node


def specialize_function(function, chosen_types):
    """Returns a copy of the function object with all generic types
    replaced with chosen types.

    """

    function_name = '_'.join([function.name] + chosen_types)
    returns = None
    args = []

    for generic_type, chosen_type in zip(function.generic_types, chosen_types):
        returns = replace_generic_type(function.returns, generic_type, chosen_type)

        for param, node in function.args:
            args.append((Param(param.name,
                               replace_generic_type(param.type,
                                                    generic_type,
                                                    chosen_type)),
                         node))

    node = copy.deepcopy(function.node)
    node.name = function_name
    node = SpecializeTypeTransformer(function.generic_types,
                                     chosen_types).visit(node)

    return Function(function_name,
                    [],
                    function.raises,
                    function.is_test,
                    args,
                    returns,
                    node)
