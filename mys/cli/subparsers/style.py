import glob

from ...parser import ast
from ..utils import read_package_configuration


def get_source(source_lines, lineno, col_offset, end_lineno, end_col_offset):
    source = []
    number_of_lines = end_lineno - lineno + 1

    if number_of_lines == 1:
        line = source_lines[lineno - 1]
        source.append(line[col_offset:end_col_offset])
    else:
        for i in range(number_of_lines):
            line = source_lines[lineno + i - 1]

            if i == 0:
                line = line[col_offset:]
            elif i == number_of_lines - 1:
                line = line[:end_col_offset]

            source.append(line)

    return source


class CommentsFinder(ast.NodeVisitor):
    """Look for comments in source code not spanned by AST nodes.

    """

    def __init__(self, source_lines):
        self.comments = {}
        self.source_lines = source_lines
        self.prev_end_lineno = 1
        self.prev_end_col_offset = 0

    def get_source(self, end_lineno, end_col_offset):
        return get_source(self.source_lines,
                          self.prev_end_lineno,
                          self.prev_end_col_offset,
                          end_lineno,
                          end_col_offset)

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

    def visit_ImportFrom(self, node):
        self.add_comments(node.lineno, node.col_offset)
        self.prev_end_lineno = node.end_lineno
        self.prev_end_col_offset = node.end_col_offset


class SourceStyler:

    def __init__(self):
        self.source_lines = None
        self.tree = None
        self.comments = None
        self.local_imports = None
        self.other_imports = None
        self.code = None

    def style(self, source_lines, tree, comments):
        """Returns the styled source code from given source code, AST and
        extracted comments and blank lines.

        """

        self.source_lines = source_lines
        self.tree = tree
        self.comments = comments
        self.local_imports = []
        self.other_imports = []
        self.code = []

        # from pprint import pprint
        # print('Comments:')
        # pprint(comments)

        for node in self.tree.body:
            if isinstance(node, ast.ImportFrom):
                self._style_import_from(node)
            else:
                self._style_other(node)

        imports = []

        if self.other_imports:
            imports += sorted(self.other_imports)

        if self.local_imports:
            imports += sorted(self.local_imports)

        if imports:
            imports.append('')

        return '\n'.join(imports + self.code)

    def _style_import_from(self, node):
        module = '.' * node.level + node.module
        names = []

        for item in node.names:
            if item.asname is None:
                name = item.name
            else:
                name = f'{item.name} as {item.asname}'

            names.append(name)

        names = ', '.join(names)
        styled_code = f'from {module} import {names}'

        if module[0] == '.':
            self.local_imports.append(styled_code)
        else:
            self.other_imports.append(styled_code)

    def _style_other(self, node):
        # print(ast.dump(node, indent=4))

        # Just get everything the node spans for now.
        self.code += get_source(self.source_lines,
                                node.lineno,
                                node.col_offset,
                                node.end_lineno,
                                node.end_col_offset)
        self.code.append('')


def do_style(_parser, _args, _mys_config):
    read_package_configuration()
    source_styler = SourceStyler()

    for src in glob.glob('src/**/*.mys', recursive=True):
        with open(src, 'r') as fin:
            source = fin.read()

        tree = ast.parse(source)
        source_lines = source.split('\n')
        comments_finder = CommentsFinder(source_lines)
        comments_finder.visit(tree)
        styled_source = source_styler.style(source_lines,
                                            tree,
                                            comments_finder.comments)

        if styled_source != source:
            with open(src, 'w') as fout:
                fout.write(styled_source)


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'style',
        description=(
            'Check that the package follows the Mys style guidelines. Automatically '
            'fixes trivial errors and prints the rest.'))
    subparser.set_defaults(func=do_style)
