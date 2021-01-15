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
        if len(node.generators) != 1:
            raise CompileError("only one for-loop allowed", node)

        context = visitor.context
        self.local_variables = list(context.local_variables.items())
        self.local_variables.sort()
        self.result_cpp_type = mys_to_cpp_type(mys_type, context)
        self.result_variable = context.unique('result')
        context.push()
        context.define_local_variable(self.result_variable, mys_type, node)
        self.generator = node.generators[0]
        self.context = context
        self.visitor = visitor
        self.mys_type = mys_type
        self.node = node

        if len(self.generator.ifs) > 1:
            raise CompileError("at most one if allowed", node)

    def value(self):
        raise NotImplementedError()

    def body(self):
        raise NotImplementedError()

    def generate(self):
        body = self.body()

        if self.generator.ifs:
            body = ast.If(test=self.generator.ifs[0],
                          body=[body],
                          orelse=[])

        code = '\n'.join([
            f'{self.result_cpp_type} {self.result_variable} = {self.value()};',
            self.visitor.visit_For(
                ast.fix_missing_locations(
                    ast.For(target=self.generator.target,
                            iter=self.generator.iter,
                            body=[body]))),
            f'\nreturn {self.result_variable};'
        ])
        function_name = self.visitor.unique('list_comprehension')
        parameters = ', '.join([
            f'{mys_to_cpp_type_param(mys_type, self.context)} {name}'
            for name, mys_type in self.local_variables
        ])
        function_code = '\n'.join([
            f'static {self.result_cpp_type} {function_name}({parameters})',
            '{',
            indent(code),
            '}'
        ])
        self.context.comprehensions.append(function_code)
        self.context.pop()
        self.context.mys_type = self.mys_type
        parameters = ', '.join([name for name, _ in self.local_variables])

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
