import glob

from ....parser import ast
from ...utils import Spinner
from ...utils import read_package_configuration
from .comments_finder import CommentsFinder
from .comments_reader import CommentsReader
from .source_styler import SourceStyler
from .utils import get_function_or_class_node_start
from .utils import get_source


def style_files():
    source_styler = SourceStyler()

    for src_path in glob.glob('src/**/*.mys', recursive=True):
        with open(src_path, 'r') as fin:
            source = fin.read()

        tree = ast.parse(source, src_path)
        source_lines = source.split('\n')
        finder = CommentsFinder(source_lines)
        finder.visit(tree)
        # from pprint import pprint
        # pprint(finder.comments)
        styled_source = source_styler.style(source_lines, tree, finder.comments)

        if styled_source != source:
            with open(src_path, 'w') as fout:
                fout.write(styled_source)


def do_style(_parser, _args, _mys_config):
    read_package_configuration()

    with Spinner(text="Styling source code"):
        style_files()


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'style',
        description=(
            'Modify all source code files in the package follow the Mys style '
            'guidelines.'))
    subparser.set_defaults(func=do_style)
