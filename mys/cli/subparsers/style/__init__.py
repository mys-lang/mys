import glob

from ....parser import ast
from ...utils import Spinner
from ...utils import read_package_configuration
from .comments_finder import CommentsFinder
from .comments_reader import CommentsReader
from .utils import get_function_or_class_node_start
from .utils import get_source


class SourceStyler:

    def __init__(self):
        self.source_lines = None
        self.tree = None
        self.comments_reader = None
        self.local_imports = None
        self.other_imports = None
        self.code = None

    def style(self, source_lines, tree, comments):
        """Returns the styled source code from given source code, AST and
        extracted comments and blank lines.

        """

        self.source_lines = source_lines
        self.tree = tree
        self.comments_reader = CommentsReader(comments)
        self.local_imports = []
        self.other_imports = []
        self.code = []

        for node in self.tree.body:
            if isinstance(node, ast.ImportFrom):
                self._style_import_from(node)
            elif isinstance(node, ast.FunctionDef):
                self._style_function(node)
            elif isinstance(node, ast.ClassDef):
                self._style_class(node)
            else:
                self._style_other(node)

        imports = []

        if self.other_imports:
            imports += sorted(self.other_imports)

        if self.local_imports:
            imports += sorted(self.local_imports)

        if imports:
            imports.append('')

        self.code = imports + self.code
        self.code += self.comments_reader.get_remaining(self.get_prev_line())

        if len(self.code) == 0 or self.code[-1] != '':
            self.code.append('')

        return '\n'.join(self.code)

    def get_prev_line(self):
        if len(self.code) == 0:
            return ''
        else:
            return self.code[-1]

    def get_comments_before(self, lineno):
        prev_line = self.get_prev_line()
        comments = self.comments_reader.get_before(lineno, prev_line)

        return comments

    def get_inline_comment(self, lineno):
        comment = self.comments_reader.get_at(lineno)

        if comment:
            comment = '  ' + comment.strip()

        return comment

    def ensure_blank_line(self):
        if len(self.code) > 0:
            if self.get_prev_line() != '':
                self.code.append('')

    def _style_import_from(self, node):
        if node.module is None:
            module = ''
        else:
            module = node.module

        module = '.' * node.level + module
        names = []

        for item in node.names:
            if item.asname is None:
                name = item.name
            else:
                name = f'{item.name} as {item.asname}'

            names.append(name)

        comment = self.get_inline_comment(node.end_lineno)
        names = ', '.join(names)
        styled_code = f'from {module} import {names}{comment}'

        if module[0] == '.':
            self.local_imports.append(styled_code)
        else:
            self.other_imports.append(styled_code)

    def _style_function(self, node):
        # Just get everything the node spans for now.
        lineno, col_offset = get_function_or_class_node_start(node)
        comments = self.get_comments_before(lineno)

        if not comments:
            self.ensure_blank_line()

        self.code += comments
        self.code += get_source(self.source_lines,
                                lineno,
                                col_offset,
                                node.end_lineno,
                                node.end_col_offset)[1]
        self.code[-1] += self.get_inline_comment(node.end_lineno)

    def _style_class(self, node):
        # Just get everything the node spans for now.
        lineno, col_offset = get_function_or_class_node_start(node)
        comments = self.get_comments_before(lineno)

        if not comments:
            self.ensure_blank_line()

        self.code += comments
        self.code += get_source(self.source_lines,
                                lineno,
                                col_offset,
                                node.end_lineno,
                                node.end_col_offset)[1]

    def _style_other(self, node):
        # Just get everything the node spans for now.
        self.code += self.get_comments_before(node.lineno)
        self.code += get_source(self.source_lines,
                                node.lineno,
                                node.col_offset,
                                node.end_lineno,
                                node.end_col_offset)[1]


def style_files():
    source_styler = SourceStyler()

    for src_path in glob.glob('src/**/*.mys', recursive=True):
        with open(src_path, 'r') as fin:
            source = fin.read()

        tree = ast.parse(source, src_path)
        source_lines = source.split('\n')
        finder = CommentsFinder(source_lines)
        finder.visit(tree)
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
