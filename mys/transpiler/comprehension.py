from ..parser import ast
from .utils import CompileError
from .utils import indent
from .utils import make_shared_dict
from .utils import make_shared_list
from .utils import mys_to_cpp_type
from .utils import mys_to_cpp_type_param
from .utils import split_dict_mys_type


class Comprehension:

    def __init__(self, node, mys_type, visitor):
        self.node = node
        self.mys_type = mys_type
        self.visitor = visitor
        self.result_variable = None

    def value(self):
        raise NotImplementedError()

    def body(self):
        raise NotImplementedError()

    def generate(self):
        if len(self.node.generators) != 1:
            raise CompileError("only one for-loop allowed", self.node)

        context = self.visitor.context
        local_variables = list(context.local_variables.items())
        local_variables.sort()
        result_cpp_type = mys_to_cpp_type(self.mys_type, context)
        self.result_variable = context.unique('result')
        context.push()
        context.define_local_variable(self.result_variable,
                                      self.mys_type,
                                      self.node)
        generator = self.node.generators[0]

        if len(generator.ifs) > 1:
            raise CompileError("at most one if allowed", self.node)

        body = self.body()

        if generator.ifs:
            body = ast.If(test=generator.ifs[0],
                          body=[body],
                          orelse=[])

        code = '\n'.join([
            f'{result_cpp_type} {self.result_variable} = {self.value()};',
            self.visitor.visit_For(
                ast.fix_missing_locations(
                    ast.For(target=generator.target,
                            iter=generator.iter,
                            body=[body],
                            orelse=[]))),
            f'\nreturn {self.result_variable};'
        ])
        function_name = self.visitor.unique('list_comprehension')
        parameters = ', '.join([
            f'{mys_to_cpp_type_param(mys_type, context)} {name}'
            for name, mys_type in local_variables
        ])
        function_code = '\n'.join([
            f'static {result_cpp_type} {function_name}({parameters})',
            '{',
            indent(code),
            '}'
        ])
        context.comprehensions.append(function_code)
        context.pop()
        context.mys_type = self.mys_type
        parameters = ', '.join([name for name, _ in local_variables])

        return f'{function_name}({parameters})'


class ListComprehension(Comprehension):

    def value(self):
        result_item_cpp_type = self.visitor.mys_to_cpp_type(self.mys_type[0])

        return make_shared_list(result_item_cpp_type, '')

    def body(self):
        return ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=self.result_variable),
                    attr='append'),
                args=[self.node.elt]))

class DictComprehension(Comprehension):

    def value(self):
        key_mys_type, value_mys_type = split_dict_mys_type(self.mys_type)
        key_cpp_type = self.visitor.mys_to_cpp_type(key_mys_type)
        value_cpp_type = self.visitor.mys_to_cpp_type(value_mys_type)

        return make_shared_dict(key_cpp_type, value_cpp_type, '')

    def body(self):
        return ast.Assign(
            targets=[
                ast.Subscript(
                    slice=self.node.key,
                    value=ast.Name(id=self.result_variable))
            ],
            value=self.node.value)
