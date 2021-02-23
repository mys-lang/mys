from ....parser import ast
from ....transpiler.definitions import TypeVisitor
from ....transpiler.utils import format_mys_type
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
        lineno = get_function_or_class_node_start(node)[0]
        comments = self.get_comments_before(lineno)

        if not comments:
            self.ensure_blank_line()

        self.code += comments

        for item in node.decorator_list:
            if isinstance(item, ast.Name):
                self.code.append(f'@{item.id}')

        members = []
        methods = []

        for item in node.body:
            comments = self.get_comments_before(item.lineno)

            if isinstance(item, ast.FunctionDef):
                methods.append('')
                methods += comments
                methods += get_source(self.source_lines,
                                      item.lineno,
                                      item.col_offset - 4,
                                      item.end_lineno,
                                      item.end_col_offset)[1]
                methods[-1] += self.get_inline_comment(item.end_lineno)
            elif isinstance(item, ast.AnnAssign):
                mys_type = format_mys_type(TypeVisitor().visit(item.annotation))
                members += comments
                members.append(f'    {item.target.id}: {mys_type}')
            elif isinstance(item, ast.Constant):
                members += comments
                members += get_source(self.source_lines,
                                      item.lineno - 4,
                                      item.col_offset,
                                      item.end_lineno,
                                      item.end_col_offset)[1]
                members[-1] += self.get_inline_comment(item.end_lineno)
            elif isinstance(item, ast.Pass):
                members += comments
                members.append('    pass')

        bases = ', '.join([base.id for base in node.bases])

        if bases:
            bases = f'({bases})'

        self.code.append(f'class {node.name}{bases}:')
        self.code += members
        self.code += methods

    def _style_other(self, node):
        # Just get everything the node spans for now.
        self.code += self.get_comments_before(node.lineno)
        self.code += get_source(self.source_lines,
                                node.lineno,
                                node.col_offset,
                                node.end_lineno,
                                node.end_col_offset)[1]
