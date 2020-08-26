import ast
import subprocess
import os
import sys
import argparse
from typing import Tuple
import ast
from pprintast import pprintast
import toml
import shutil

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


def build_app(verbose):
    load_package_configuration()

    if not os.path.exists('build'):
        setup_build()

    command = ['make', '-C', 'build']

    if not verbose:
        command += ['-s']

    subprocess.run(command, check=True)


def run_app():
    proc = subprocess.Popen(['build/app'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)

    while True:
        stdout, _ = proc.communicate(timeout=0.1)
        sys.stdout.buffer.write(stdout)
        sys.stdout.flush()

        if proc.returncode is not None:
            if proc.returncode != 0:
                raise Exception(f'The application exited with {proc.returncode}')

            break


def _do_build(args):
    build_app(args.verbose)


def _do_run(args):
    build_app(args.verbose)
    run_app()


def _do_clean(args):
    shutil.rmtree('build')


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
    ast.USub: '-',
    ast.Is: '==',
    ast.Eq: '==',
    ast.NotEq: '!=',
    ast.Lt: '<',
    ast.LtE: '<=',
    ast.Gt: '>',
    ast.GtE: '>='
}


class ModuleVisitor(ast.NodeVisitor):

    def visit_Module(self, node):
        return '\n\n'.join(['#include "mys.hpp"'] + [
            self.visit(item)
            for item in node.body
        ]) + '\n'

    def visit_Import(self, node):
        return '#include "todo"'

    def visit_ImportFrom(self, node):
        return '#include "todo"'

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

    def visit_FunctionDef(self, node):
        function_name = node.name
        return_type = return_type_string(node.returns)
        params = params_string(function_name, node.args.args)

        body = []

        for item in node.body:
            body.append(indent(BodyVisitor().visit(item)))

        if function_name == 'main':
            if return_type == 'void':
                return_type = 'int'
            else:
                raise Exception("main() must return 'None'.")

            body.append('')
            body.append(indent('return 0;'))

        return '\n'.join([
            f'{return_type} {function_name}({params})',
            '{'
        ] + body + [
            '}'
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


class BodyVisitor(ast.NodeVisitor):

    def visit_Name(self, node):
        return node.id

    def visit_Call(self, node):
        function_name = self.visit(node.func)
        args = [
            self.visit(arg)
            for arg in node.args
        ]

        if function_name == 'print':
            if len(args) == 0:
                code = 'std::cout << std::endl'
            elif len(args) == 1:
                code = f'std::cout << {args[0]} << std::endl'
            else:
                first = args[0]
                args = ' << " " << '.join(args[1:])
                code = f'std::cout << {first} << " " << {args} << std::endl'
        else:
            args = ', '.join(args)
            code = f'{function_name}({args})'

        return code

    def visit_Constant(self, node):
        if isinstance(node.value, str):
            return f'"{node.value}"'
        elif isinstance(node.value, bool):
            return 'true' if node.value else 'false'
        else:
            return str(node.value)

    def visit_Expr(self, node):
        return self.visit(node.value) + ';'

    def visit_BinOp(self, node):
        op = OPERATORS[node.op.__class__]
        left = self.visit(node.left)
        right = self.visit(node.right)

        return f'({left} {op} {right})'

    def visit_UnaryOp(self, node):
        op = OPERATORS[node.op.__class__]
        operand = self.visit(node.operand)

        return f'{op}{operand}'

    def visit_AugAssign(self, node):
        lval = node.target.id
        op = OPERATORS[node.op.__class__]
        rval = self.visit(node.value)

        return f'{lval} {op}= {rval}'

    def visit_Tuple(self, node):
        return 'make_shared_tuple<todo>({' + ', '.join([
            self.visit(item)
            for item in node.elts
        ]) + '})'

    def visit_List(self, node):
        return 'make_shared_vector<todo>({' + ', '.join([
            self.visit(item)
            for item in node.elts
        ]) + '})'

    def visit_Dict(self, node):
        return 'make_shared_map<todo>({})'

    def visit_For(self, node):
        var = self.visit(node.target)
        func = self.visit(node.iter)
        body = indent('\n'.join([
            self.visit(item) + ';'
            for item in node.body
        ]))

        return '\n'.join([
            f'for (auto {var}: {func}) {{',
            body,
            '}'
        ])

    def visit_Attribute(self, node):
        value = self.visit(node.value)

        return f'{value}.{node.attr}'

    def visit_Compare(self, node):
        op = OPERATORS[node.ops[0].__class__]
        left = self.visit(node.left)
        right = self.visit(node.comparators[0])

        return f'{left} {op} {right}'

    def visit_If(self, node):
        cond = self.visit(node.test)
        body = indent('\n'.join([
            self.visit(item)
            for item in node.body
        ]))
        orelse = indent('\n'.join([
            self.visit(item)
            for item in node.orelse
        ]))

        code = [f'if ({cond}) {{', body]

        if orelse:
            code += [
                '} else {',
                orelse,
                '}'
            ]

        return '\n'.join(code)

    def visit_Return(self, node):
        value = self.visit(node.value)

        return f'return {value};'

    def visit_Try(self, node):
        return '\n'.join([
            'try {',
            '} catch (...) {',
            '}'
        ])

    def visit_Assign(self, node):
        targets = ' todo '.join([self.visit(target) for target in node.targets])
        value = self.visit(node.value)

        return f'{targets} = {value};'

    def visit_Subscript(self, node):
        value = self.visit(node.value)

        return f'{value}'

    def visit_AnnAssign(self, node):
        type = self.visit(node.annotation)
        target = self.visit(node.target)
        value = self.visit(node.value)

        return f'{type} {target} = {value};'

    def visit_While(self, node):
        condition = self.visit(node.test)
        body = indent('\n'.join([self.visit(item) for item in node.body]))

        return '\n'.join([
            f'while ({condition}) {{',
            body,
            '}'
        ])

    def visit_Pass(self, node):
        return '// pass'

    def visit_Break(self, node):
        return 'break;'

    def visit_Continue(self, node):
        return 'continue;'

    def visit_Assert(self, node):
        cond = self.visit(node.test)

        return f'assert({cond});'

    def generic_visit(self, node):
        raise Exception(node)


def transpile(source):
    # pprintast(source)

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

    # The build subparser.
    subparser = subparsers.add_parser(
        'build',
        description='Build the appliaction.')
    subparser.add_argument('--verbose',
                           action='store_true',
                           help='Verbose output.')
    subparser.set_defaults(func=_do_build)

    # The run subparser.
    subparser = subparsers.add_parser(
        'run',
        description='Build and run the application.')
    subparser.add_argument('--verbose',
                           action='store_true',
                           help='Verbose output.')
    subparser.add_argument('args', nargs='*')
    subparser.set_defaults(func=_do_run)

    # The clean subparser.
    subparser = subparsers.add_parser(
        'clean',
        description='Remove build output.')
    subparser.set_defaults(func=_do_clean)

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
