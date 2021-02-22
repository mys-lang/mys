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
        self.prev_end_lineno = 1
        self.prev_end_col_offset = 0

    def get_source(self, end_lineno, end_col_offset):
        source = []
        number_of_lines = end_lineno - self.prev_end_lineno + 1

        if number_of_lines == 1:
            line = self.source_lines[self.prev_end_lineno - 1]
            source.append(line[self.prev_end_col_offset:end_col_offset])
        else:
            for i in range(number_of_lines):
                line = self.source_lines[self.prev_end_lineno + i - 1]

                if i == 0:
                    line = line[self.prev_end_col_offset:]
                elif i == number_of_lines - 1:
                    line = line[:end_col_offset]

                source.append(line)

        return source

    def add_comments(self, lineno, col_offset):
        self.comments[self.prev_end_lineno] = self.get_source(lineno, col_offset)

    def visit_FunctionDef(self, node):
        self.add_comments(node.lineno, node.col_offset)
        self.prev_end_lineno = node.end_lineno
        self.prev_end_col_offset = node.end_col_offset

    def visit_ClassDef(self, node):
        self.add_comments(node.lineno, node.col_offset)
        self.prev_end_lineno = node.end_lineno
        self.prev_end_col_offset = node.end_col_offset

    def visit_AnnAssign(self, node):
        self.add_comments(node.lineno, node.col_offset)
        self.prev_end_lineno = node.end_lineno
        self.prev_end_col_offset = node.end_col_offset


def style_file(_tree, _comments):
    """Returns the styled source code from given AST and comments.

    """

    return 'ToDo: the styled code'


def do_style(_parser, args, _mys_config):
    read_package_configuration()

    if not args.experimental:
        box_print(['This subcommand is not yet implemented.'], ERROR)

        raise Exception()

    for src in glob.glob('**/*.mys', recursive=True):
        with open(src, 'r') as fin:
            source = fin.read()

        tree = ast.parse(source)
        comments_finder = CommentsFinder(source)
        comments_finder.visit(tree)
        from pprint import pprint
        print('Comments:')
        pprint(comments_finder.comments)
        print(style_file(tree, comments_finder.comments))


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'style',
        description=(
            'Check that the package follows the Mys style guidelines. Automatically '
            'fixes trivial errors and prints the rest.'))
    subparser.add_argument('-e', '--experimental', action='store_true')
    subparser.set_defaults(func=do_style)
