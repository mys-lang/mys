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

    return mys_type


class SpecializeGenericType:

    def __init__(self, generic_type, chosen_type):
        self.generic_type = generic_type
        self.chosen_type = chosen_type

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
        self.generic_to_specialized_type = {
            generic_type: chosen_type
            for generic_type, chosen_type in zip(generic_types, chosen_types)
        }

    def visit_Name(self, node):
        node.id = self.generic_to_specialized_type.get(node.id, node.id)

        return node


def specialize_function(function, specialized_full_name, chosen_types):
    """Returns a copy of the function object with all generic types
    replaced with chosen types.

    """

    returns = function.returns
    args = copy.deepcopy(function.args)

    for generic_type, chosen_type in zip(function.generic_types, chosen_types):
        returns = SpecializeGenericType(generic_type, chosen_type).replace(returns)

        for param, node in args:
            param.type = SpecializeGenericType(generic_type,
                                               chosen_type).replace(param.type)

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
                    node)
