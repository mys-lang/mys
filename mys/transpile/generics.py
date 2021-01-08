import copy
from ..parser import ast
from .definitions import Param
from .definitions import Function
from .utils import split_dict_mys_type


def replace_generic_types(generic_types, mys_type, chosen_types):
    if isinstance(mys_type, str):
        for generic_type, chosen_type in zip(generic_types, chosen_types):
            if mys_type == generic_type:
                return chosen_type


def replace_generic_type(mys_type, generic_type, chosen_type):
    if isinstance(mys_type, str):
        if mys_type == generic_type:
            mys_type = chosen_type
    elif isinstance(mys_type, dict):
        key_mys_type, value_mys_type = split_dict_mys_type(mys_type)
        key_mys_type = replace_generic_type(key_mys_type,
                                            generic_type,
                                            chosen_type)
        value_mys_type = replace_generic_type(value_mys_type,
                                              generic_type,
                                              chosen_type)
        mys_type = {key_mys_type: value_mys_type}
    elif isinstance(mys_type, list):
        mys_type = [replace_generic_type(mys_type[0], generic_type, chosen_type)]
    elif isinstance(mys_type, tuple):
        mys_type = tuple(
            replace_generic_type(item_mys_type, generic_type, chosen_type)
            for item_mys_type in mys_type)
    else:
        raise Exception('generic type not supported')

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
    returns = function.returns
    args = copy.deepcopy(function.args)

    for generic_type, chosen_type in zip(function.generic_types, chosen_types):
        returns = replace_generic_type(returns, generic_type, chosen_type)

        for param, node in args:
            param.type = replace_generic_type(param.type, generic_type, chosen_type)

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
