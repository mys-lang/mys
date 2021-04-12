from ..parser import ast
from .comprehension import DictComprehension
from .comprehension import ListComprehension
from .comprehension import SetComprehension
from .constant_visitor import is_constant
from .generics import add_generic_class
from .utils import CompileError
from .utils import GenericType
from .utils import dot2ns
from .utils import format_mys_type
from .utils import is_float_literal
from .utils import is_integer_literal
from .utils import is_primitive_type
from .utils import make_float_literal
from .utils import make_integer_literal
from .utils import make_shared
from .utils import make_shared_dict
from .utils import make_shared_list
from .utils import make_shared_set
from .utils import mys_to_cpp_type
from .utils import raise_if_wrong_types
from .utils import raise_if_wrong_visited_type
from .utils import split_dict_mys_type


def is_allowed_dict_key_type(mys_type):
    if is_primitive_type(mys_type):
        return True
    elif mys_type == 'string':
        return True

    return False


class ValueCheckTypeVisitor:

    def __init__(self, visitor):
        self.visitor = visitor
        self.context = self.visitor.context

    def mys_to_cpp_type(self, mys_type):
        return mys_to_cpp_type(mys_type, self.context)

    def visit_tuple(self, node, mys_type):
        if not isinstance(mys_type, tuple):
            mys_type = format_mys_type(mys_type)

            raise CompileError(f"cannot convert tuple to '{mys_type}'", node)

        values = []
        types = []

        for i, item in enumerate(node.elts):
            values.append(self.visit(item, mys_type[i]))
            types.append(self.context.mys_type)

        raise_if_wrong_types(tuple(types), mys_type, node, self.context)
        self.context.mys_type = mys_type
        cpp_type = self.mys_to_cpp_type(mys_type)
        values = ", ".join(values)

        return make_shared(cpp_type[6:], values)

    def visit_list(self, node, mys_type):
        if not isinstance(mys_type, list):
            mys_type = format_mys_type(mys_type)

            raise CompileError(f"cannot convert list to '{mys_type}'", node)

        values = []
        item_mys_type = mys_type[0]

        for item in node.elts:
            values.append(self.visit(item, item_mys_type))

        self.context.mys_type = mys_type
        value = ", ".join(values)
        item_cpp_type = self.mys_to_cpp_type(item_mys_type)

        return make_shared_list(item_cpp_type, value)

    def visit_dict(self, node, mys_type):
        if isinstance(mys_type, set) and len(node.keys) == 0:
            item_mys_type = list(mys_type)[0]
            item_cpp_type = self.mys_to_cpp_type(item_mys_type)
            return make_shared_set(item_cpp_type, '')

        if not isinstance(mys_type, dict):
            mys_type = format_mys_type(mys_type)

            raise CompileError(f"cannot convert dict to '{mys_type}'", node)

        key_mys_type, value_mys_type = split_dict_mys_type(mys_type)

        if not is_allowed_dict_key_type(key_mys_type):
            raise CompileError("invalid key type", node)

        keys = []
        values = []

        for key, value in zip(node.keys, node.values):
            keys.append(self.visit(key, key_mys_type))
            values.append(self.visit(value, value_mys_type))

        self.context.mys_type = mys_type
        items = ", ".join([f'{{{key}, {value}}}' for key, value in zip(keys, values)])
        key_cpp_type = self.mys_to_cpp_type(key_mys_type)
        value_cpp_type = self.mys_to_cpp_type(value_mys_type)

        return make_shared_dict(key_cpp_type, value_cpp_type, items)

    def visit_set(self, node, mys_type):
        if not isinstance(mys_type, set):
            mys_type = format_mys_type(mys_type)

            raise CompileError(f"cannot convert set to '{mys_type}'", node)

        values = []
        item_mys_type = list(mys_type)[0]

        for item in node.elts:
            values.append(self.visit(item, item_mys_type))

        self.context.mys_type = mys_type
        value = ", ".join(values)
        item_cpp_type = self.mys_to_cpp_type(item_mys_type)

        return make_shared_set(item_cpp_type, value)

    def visit_list_comp(self, node, mys_type):
        return ListComprehension(node, mys_type, self.visitor).generate()

    def visit_dict_comp(self, node, mys_type):
        return DictComprehension(node, mys_type, self.visitor).generate()

    def visit_set_comp(self, node, mys_type):
        return SetComprehension(node, mys_type, self.visitor).generate()

    def visit_other(self, node, mys_type):
        value = self.visitor.visit(node)

        if self.context.is_trait_defined(mys_type):
            if self.context.is_class_defined(self.context.mys_type):
                definitions = self.context.get_class_definitions(
                    self.context.mys_type)

                if mys_type not in definitions.implements:
                    trait_type = format_mys_type(mys_type)
                    class_type = self.context.mys_type

                    raise CompileError(
                        f"'{class_type}' does not implement trait '{trait_type}'",
                        node)

                self.context.mys_type = mys_type
        elif self.context.is_trait_defined(self.context.mys_type):
            if self.context.is_class_defined(mys_type):
                value = f'static_cast<mys::shared_ptr<{dot2ns(mys_type)}>>({value})'
                definitions = self.context.get_class_definitions(mys_type)

                if self.context.mys_type not in definitions.implements:
                    trait_type = format_mys_type(self.context.mys_type)
                    class_type = mys_type

                    raise CompileError(
                        f"'{class_type}' does not implement trait '{trait_type}'",
                        node)
        else:
            if isinstance(mys_type, GenericType):
                mys_type = add_generic_class(mys_type.node, self.context)[1]

            raise_if_wrong_visited_type(self.context, mys_type, node)

        return value

    def visit(self, node, mys_type):
        if is_integer_literal(node):
            value = make_integer_literal(mys_type, node)
            self.context.mys_type = mys_type
        elif is_float_literal(node):
            value = make_float_literal(mys_type, node)
            self.context.mys_type = mys_type
        elif isinstance(node, ast.Tuple):
            value = self.visit_tuple(node, mys_type)
        elif isinstance(node, ast.List):
            value = self.visit_list(node, mys_type)
        elif isinstance(node, ast.Dict):
            value = self.visit_dict(node, mys_type)
        elif isinstance(node, ast.Set):
            value = self.visit_set(node, mys_type)
        elif isinstance(node, ast.ListComp):
            value = self.visit_list_comp(node, mys_type)
        elif isinstance(node, ast.DictComp):
            value = self.visit_dict_comp(node, mys_type)
        elif isinstance(node, ast.SetComp):
            value = self.visit_set_comp(node, mys_type)
        elif is_constant(node):
            value = self.visitor.visit(node)

            if self.context.mys_type is None:
                if not is_primitive_type(mys_type):
                    self.context.mys_type = mys_type

            raise_if_wrong_visited_type(self.context, mys_type, node)
        else:
            value = self.visit_other(node, mys_type)

        return value
