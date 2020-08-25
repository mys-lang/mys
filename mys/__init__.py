import ast
import subprocess
import os
import sys
import argparse
from typing import Tuple
import ast
from pprintast import pprintast
import toml

from .version import __version__


u8 = int
u16 = int
u32 = int
u64 = int
s8 = int
s16 = int
s32 = int
s64 = int
f32 = float
f64 = float

Queue = Tuple

PRIMITIVE_TYPES = set([
    'int',
    'float',
    'u8', 'u16', 'u32', 'u64',
    's8', 's16', 's32', 's64',
    'f32', 'f64',
    'bool'
])

PACKAGE_FMT = '''\
[package]
name = "{name}"
version = "0.1.0"
authors = ["Your Name <your.name@example.com>"]
'''

MAIN_MYS = '''\
def main():
    print('Hello, world!')
'''

MYS_DIR = os.path.dirname(os.path.realpath(__file__))

MAKEFILE_FMT = '''\
CXX ?= g++
MYS ?= mys
CFLAGS += -I{mys_dir}
CFLAGS += -Wall
CFLAGS += -O3
CFLAGS += -std=c++17
CFLAGS += -fdata-sections
CFLAGS += -ffunction-sections
LDFLAGS += -std=c++17
LDFLAGS += -static
LDFLAGS += -Wl,--gc-sections
EXE = app

all: $(EXE)
\t./$(EXE)

$(EXE): transpiled/main.mys.o
\t$(CXX) $(LDFLAGS) -o $@ $^

transpiled/main.mys.cpp: ../src/main.mys
\t$(MYS) -d transpile -o $(dir $@) $^

transpiled/main.mys.o: transpiled/main.mys.cpp
\t$(CXX) $(CFLAGS) -c transpiled/main.mys.cpp -o transpiled/main.mys.o
'''


def _do_new(args):
    os.makedirs(args.path)
    path = os.getcwd()
    os.chdir(args.path)

    try:
        with open('Package.toml', 'w') as fout:
            fout.write(PACKAGE_FMT.format(name=os.path.basename(args.path)))

        os.mkdir('src')

        with open('src/main.mys', 'w') as fout:
            fout.write(MAIN_MYS)
    finally:
        os.chdir(path)


def load_package_configuration():
    with open('Package.toml') as fin:
        config = toml.loads(fin.read())


def setup_build():
    os.makedirs('build/transpiled')

    with open('build/Makefile', 'w') as fout:
        fout.write(MAKEFILE_FMT.format(mys_dir=MYS_DIR))


def _do_run(args):
    load_package_configuration()

    if not os.path.exists('build'):
        setup_build()

    subprocess.run(['make', '-C', 'build'], check=True)


def return_type_string(node):
    if isinstance(node, ast.Tuple):
        types = []

        for item in node.elts:
            if isinstance(item, ast.Name):
                types.append(item.id)
            elif isinstance(item, ast.Subscript):
                if item.slice.value.id == 'str':
                    types.append('shared_string')

        types = ', '.join(types)

        return f'shared_tuple<{types}>'
    elif isinstance(node, ast.List):
        type_string = 'todo'
        item = node.elts[0]

        if isinstance(item, ast.Name):
            type_string = item.id
        elif isinstance(item, ast.Subscript):
            if item.slice.value.id == 'str':
                type_string = 'shared_string'

        return f'shared_vector<{type_string}>'
    elif node is None:
        return 'void'
    elif isinstance(node, ast.Name):
        if node.id == 'str':
            return 'shared_string'
        else:
            return node.id
    elif isinstance(node, ast.Dict):
        key_type = node.keys[0].id
        value_type = return_type_string(node.values[0])
        return f'shared_map<{key_type}, {value_type}>'
    else:
        return type(node)


def params_string(function_name, args):
    params = []

    for arg in args:
        param_name = arg.arg
        annotation = arg.annotation

        if annotation is None:
            raise Exception(f'{function_name}({param_name}) is not typed.')
        elif isinstance(annotation, ast.Name):
            param_type = annotation.id

            if param_type == 'str':
                param_type = 'shared_string&'
            elif param_type not in PRIMITIVE_TYPES:
                param_type = f'std::shared_ptr<{param_type}>&'

            params.append(f'{param_type} {param_name}')
        elif isinstance(annotation, ast.Subscript):
            if isinstance(annotation.value, ast.Name):
                if annotation.value.id == 'Optional':
                    value = annotation.slice.value

                    if isinstance(value, ast.Name):
                        params.append(f'std::optional<{value.id}>& {param_name}')
            else:
                params.append(f'todo {param_name}')

    return ', '.join(params)


def indent(string):
    return '\n'.join(['    ' + line for line in string.splitlines() if line])


class ModuleVisitor(ast.NodeVisitor):

    def visit_Module(self, node):
        body = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                body.append(FunctionVisitor().visit(item))
            elif isinstance(item, ast.ClassDef):
                body.append(ClassVisitor().visit(item))
            elif isinstance(item, ast.Import):
                pass
            elif isinstance(item, ast.ImportFrom):
                pass
            elif isinstance(item, ast.AnnAssign):
                pass
            else:
                raise Exception(f"Unexpected node of type '{type(item).__name__}'.")

        return '\n\n'.join(['#include "mys.hpp"'] + body)


class ClassVisitor(ast.NodeVisitor):

    def visit_ClassDef(self, node):
        class_name = node.name
        body = []

        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                body.append(indent(MethodVisitor(class_name).visit(item)))

        return '\n\n'.join([
            f'class {class_name} {{',
            'public:',
        ] + body + [
            '};'
        ])


class MethodVisitor(ast.NodeVisitor):

    def __init__(self, class_name):
        super().__init__()
        self._class_name = class_name

    def visit_FunctionDef(self, node):
        method_name = node.name
        return_type = return_type_string(node.returns)

        if len(node.args.args) == 0 or node.args.args[0].arg != 'self':
            raise Exception(
                "Methods must always take 'self' as their first argument.")

        if node.decorator_list:
            raise Exception("Methods must not be decorated.")

        params = params_string(method_name, node.args.args[1:])

        if method_name == '__init__':
            return '\n'.join([
                f'{self._class_name}({params})',
                '{',
                '}'
            ])
        else:
            return '\n'.join([
                f'{return_type} {method_name}({params})',
                '{',
                '}'
            ])


BOOLOPS = {
    ast.And: '&&',
    ast.Or: '||'
}

OPERATORS = {
    ast.Add: '+',
    ast.Sub: '-',
    ast.Mult: '*',
    ast.Div: '/',
    ast.Mod: '%',
    ast.LShift: '<<',
    ast.RShift: '>>',
    ast.BitOr: '|',
    ast.BitXor: '^',
    ast.BitAnd: '&',
    ast.FloorDiv: '/',
    ast.Not: '!',
    ast.UAdd: '+',
    ast.USub: '-'
}

CMPOPS = {
    ast.Eq: '==',
    ast.NotEq: '!=',
    ast.Lt: '<',
    ast.LtE: '<=',
    ast.Gt: '>',
    ast.GtE: '>='
}


class ForVisitor(ast.NodeVisitor):

    def visit_For(self, node):
        var = node.target.id

        if node.iter.func.id == 'range':
            args = node.iter.args

            if len(args) == 1:
                begin = 0

                if isinstance(args[0], ast.Name):
                    end = args[0].id
                else:
                    raise Exception('Can only iterate to a variable.')

                step = 1
            else:
                raise Exception('Can only iterate from 0 to a maximum.')
        else:
            raise Exception('Can only iterate over a range.')

        body = []

        for item in node.body:
            if isinstance(item, ast.AugAssign):
                lval = item.target.id
                op = OPERATORS[item.op.__class__]

                if isinstance(item.value, ast.BinOp):
                    op1 = OPERATORS[item.value.op.__class__]
                    rval = f'{item.value.left.id} {op1} {item.value.right.id}'
                else:
                    rval = 'todo'

                body.append(f'{lval} {op}= ({rval});')

        body = indent('\n'.join(body))

        return '\n'.join([
            f'for (auto {var} = {begin}; {var} < {end}; {var} += {step}) {{',
            body,
            '}'
        ])


class ExpressionVisitor(ast.NodeVisitor):

    def visit_Expr(self, node):
        code = ''

        if isinstance(node.value, ast.Call):
            code = self.visit_Call(node.value)

        return code

    def visit_Call(self, node):
        code = ''

        if isinstance(node.func, ast.Name):
            function_name = node.func.id
            args = []

            if function_name == 'print':
                for arg in node.args:
                    if isinstance(arg, ast.Constant):
                        if isinstance(arg.value, str):
                            args.append(f'"{arg.value}"')
                        else:
                            args.append(f'{arg.value}')
                    elif isinstance(arg, ast.Name):
                        args.append(arg.id)
                    elif isinstance(arg, ast.Call):
                        args.append(self.visit_Call(arg))

                if len(args) == 0:
                    code = 'std::cout << std::endl'
                elif len(args) == 1:
                    code = f'std::cout << {args[0]} << std::endl'
                else:
                    first = args[0]
                    args = ' << " "'.join(args[1:])
                    code = f'std::cout << {first} << " " << {args} << std::endl'
            else:
                for arg in node.args:
                    if isinstance(arg, ast.Constant):
                        if arg.value is None:
                            args.append('{}')
                        elif isinstance(arg.value, str):
                            args.append(f'"{arg.value}"')
                        else:
                            args.append(f'{arg.value}')
                    elif isinstance(arg, ast.Name):
                        args.append(arg.id)
                    elif isinstance(arg, ast.Call):
                        args.append(self.visit_Call(arg))

                args = ', '.join(args)
                code = f'{function_name}({args})'

        return code


class FunctionVisitor(ast.NodeVisitor):

    def visit_FunctionDef(self, node):
        function_name = node.name
        return_type = return_type_string(node.returns)
        params = params_string(function_name, node.args.args)

        body = []

        for item in node.body:
            if isinstance(item, ast.For):
                body.append(indent(ForVisitor().visit(item)))
            elif isinstance(item, ast.Expr):
                body.append(indent(ExpressionVisitor().visit(item) + ';'))

        if function_name == 'main':
            if return_type == 'void':
                return_type = 'int'
            else:
                raise Exception("main() must return 'None'.")

            body.append('')
            body.append(indent('return (0);'))

        return '\n'.join([
            f'{return_type} {function_name}({params})',
            '{'
        ] + body + [
            '}'
        ])


def transpile(source):
    pprintast(source)

    return ModuleVisitor().visit(ast.parse(source))


def _do_transpile(args):
    mys_cpp = os.path.join(args.outdir, os.path.basename(args.mysfile) + '.cpp')

    with open(args.mysfile) as fin:
        source = transpile(fin.read())

    with open (mys_cpp, 'w') as fout:
        fout.write(source)


def main():
    parser = argparse.ArgumentParser(
        description='The Mys programming language command line tool.')

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')

    # Workaround to make the subparser required in Python 3.
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='subcommand')
    subparsers.required = True

    # The new subparser.
    subparser = subparsers.add_parser(
        'new',
        description='Create a new package.')
    subparser.add_argument('path')
    subparser.set_defaults(func=_do_new)

    # The run subparser.
    subparser = subparsers.add_parser(
        'run',
        description='Run the program.')
    subparser.add_argument('args', nargs='*')
    subparser.set_defaults(func=_do_run)

    # The transpile subparser.
    subparser = subparsers.add_parser(
        'transpile',
        description='Transpile given Mys file to C++.')
    subparser.add_argument('-o', '--outdir',
                           default='.',
                           help='Output directory.')
    subparser.add_argument('mysfile')
    subparser.set_defaults(func=_do_transpile)

    args = parser.parse_args()

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit('error: ' + str(e))
