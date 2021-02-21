import glob

from ...parser import ast
from ..utils import ERROR
from ..utils import box_print
from ..utils import read_package_configuration


class CommentsFinder(ast.NodeVisitor):
    """Look for comments in source code not spanned by AST nodes.

    """

    def __init__(self, source):
        self.comments = {}
        self.source_lines = source.split('\n')
        self.lineno = 1
        self.col_offset = 0

    def visit_FunctionDef(self, node):
        print(node.lineno, node.col_offset)


def do_style(_parser, args, _mys_config):
    read_package_configuration()

    if not args.experimental:
        box_print(['This subcommand is not yet implemented.'], ERROR)

        raise Exception()

    for src in glob.glob('**/*.mys', recursive=True):
        with open(src, 'r') as fin:
            source = fin.read()

        print(source)
        tree = ast.parse(source)
        print(ast.dump(tree, indent=4))
        CommentsFinder(source).visit(tree)


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'style',
        description=(
            'Check that the package follows the Mys style guidelines. Automatically '
            'fixes trivial errors and prints the rest.'))
    subparser.add_argument('-e', '--experimental', action='store_true')
    subparser.set_defaults(func=do_style)
