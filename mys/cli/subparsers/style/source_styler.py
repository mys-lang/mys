from ....parser import ast
from ....transpiler.definitions import TypeVisitor
from ....transpiler.utils import format_mys_type
from .comments_reader import CommentsReader
from .utils import get_function_or_class_node_start
from .utils import get_source


class SourceStyler(ast.NodeVisitor):

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
            elif isinstance(node, ast.AnnAssign):
                self._style_ann_assign(node)
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
        lineno = get_function_or_class_node_start(node)[0]
        comments = self.get_comments_before(lineno)

        if comments:
            self.code += comments
        else:
            self.ensure_blank_line()

        self.code += self.visit_decorator_list(node.decorator_list)
        self.code += get_source(self.source_lines,
                                node.lineno,
                                node.col_offset,
                                node.end_lineno,
                                node.end_col_offset)[1]
        self.code[-1] += self.get_inline_comment(node.end_lineno)

    def _style_class(self, node):
        lineno = get_function_or_class_node_start(node)[0]
        comments = self.get_comments_before(lineno)

        if comments:
            self.code += comments
        else:
            self.ensure_blank_line()

        self.code += self.visit_decorator_list(node.decorator_list)
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
            else:
                members += comments

                if isinstance(item, ast.AnnAssign):
                    mys_type = format_mys_type(TypeVisitor().visit(item.annotation))
                    members.append(f'    {item.target.id}: {mys_type}')
                else:
                    members += get_source(self.source_lines,
                                          item.lineno,
                                          item.col_offset - 4,
                                          item.end_lineno,
                                          item.end_col_offset)[1]

                members[-1] += self.get_inline_comment(item.end_lineno)

        bases = ', '.join([base.id for base in node.bases])

        if bases:
            bases = f'({bases})'

        self.code.append(f'class {node.name}{bases}:')
        self.code += members
        self.code += methods

    def _style_ann_assign(self, node):
        self.code += self.get_comments_before(node.lineno)
        source = get_source(self.source_lines,
                            node.value.lineno,
                            node.value.col_offset,
                            node.value.end_lineno,
                            node.value.end_col_offset)[1]
        mys_type = format_mys_type(TypeVisitor().visit(node.annotation))
        code = f'{node.target.id}: {mys_type} = '
        source[0] = code + source[0]
        self.code += source

    def _style_other(self, node):
        # Just get everything the node spans for now.
        self.code += self.get_comments_before(node.lineno)
        self.code += get_source(self.source_lines,
                                node.lineno,
                                node.col_offset,
                                node.end_lineno,
                                node.end_col_offset)[1]

    def visit_decorator_list(self, node):
        decorators = []

        for item in node:
            decorators.append(f'@{self.visit(item)}')

        return decorators

    def visit_Name(self, node):
        return node.id

    def visit_Call(self, node):
        params = [self.visit(item) for item in node.args]
        params = ', '.join(params)

        return f'{node.func.id}({params})'
