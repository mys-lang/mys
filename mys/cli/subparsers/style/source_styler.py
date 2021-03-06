from collections import Counter
from textwrap import indent

from ....parser import ast
from ....transpiler.definitions import TypeVisitor
from ....transpiler.utils import OPERATORS
from ....transpiler.utils import format_mys_type
from ....transpiler.utils import has_docstring
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

        return '\n'.join([line.rstrip() for line in self.code])

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

        members = []
        methods = []

        for i, item in enumerate(node.body):
            comments = self.get_comments_before(item.lineno)

            if isinstance(item, ast.FunctionDef):
                methods.append('')
                methods += comments
                methods += self.visit_decorator_list(item.decorator_list, '    ')
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

                if i == 0 and has_docstring(node):
                    members.append('')

        bases = ', '.join([base.id for base in node.bases])

        if bases:
            bases = f'({bases})'

        self.code += self.visit_decorator_list(node.decorator_list)
        self.code.append(f'class {node.name}{bases}:')
        self.code += members

        if self.get_prev_line() == '':
            self.code += methods[1:]
        else:
            self.code += methods

    def _style_ann_assign(self, node):
        self.code += self.get_comments_before(node.lineno)
        source = [self.visit(node.value)]
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

    def visit_decorator_list(self, node, prefix=''):
        decorators = []

        for item in node:
            decorators.append(f'{prefix}@{self.visit(item)}')

        return decorators

    def visit_Name(self, node):
        return node.id

    def visit_Call(self, node):
        params = [self.visit(item) for item in node.args]
        params = ', '.join(params)

        return f'{node.func.id}({params})'

    def visit_list_table(self, node, items):
        if not items:
            return None

        number_of_items_per_row = Counter([item.lineno for item in node.elts])

        if len(number_of_items_per_row) <= 1:
            return None

        rows = sorted(number_of_items_per_row.items())
        leading_rows = rows[:-1]
        last_row = rows[-1]
        items_per_row = leading_rows[0][1]
        linenos = [
            row[0]
            for row in leading_rows
            if row[1] == items_per_row
        ]

        if len(linenos) != len(leading_rows):
            return None

        number_of_items_per_row = leading_rows[0][1]

        if last_row[1] > number_of_items_per_row:
            return None

        column_widths = [0] * number_of_items_per_row

        for i in range(len(items)):
            column_index = i % number_of_items_per_row
            width = len(items[i])

            if width > column_widths[column_index]:
                column_widths[column_index] = width

        column_formats = [f'{{:>{width}}}'for width in column_widths]
        code = []

        for i in range(len(rows)):
            pos = i * number_of_items_per_row
            row_items = []

            for j, item in enumerate(items[pos:pos + number_of_items_per_row]):
                row_items.append(column_formats[j].format(item))

            code.append(', '.join(row_items))

        code = indent(',\n'.join(code), '    ')
        code = f'\n{code}\n'

        return code

    def visit_List(self, node):
        all_items_single_line = True
        items = []

        for item in node.elts:
            code = self.visit(item)

            if '\n' in code:
                all_items_single_line = False

            items.append(code)

        if all_items_single_line:
            code = self.visit_list_table(node, items)

            if code is None:
                code = ', '.join(items)

                # Not taking account of the starting column.
                if len(code) > 70:
                    code = ',\n'.join([f'    {item}' for item in items])
                    code = f'\n{code}\n'
        else:
            items = [indent(item, '    ') for item in items]
            code = ',\n'.join(items)
            code = f'\n{code}\n'

        return f'[{code}]'

    def visit_Dict(self, node):
        items = []

        for key, value in zip(node.keys, node.values):
            key = self.visit(key)
            value = self.visit(value)

            if '\n' in value:
                value = indent(value, '    ').strip()

            items.append(f'    {key}: {value}')

        code = ',\n'.join(items)

        if code:
            code = f'\n{code}\n'

        return f'{{{code}}}'

    def visit_Tuple(self, node):
        all_items_single_line = True
        items = []

        for item in node.elts:
            code = self.visit(item)

            if '\n' in code:
                all_items_single_line = False

            items.append(code)

        if all_items_single_line:
            code = ', '.join(items)

            # Not taking account of the starting column.
            if len(code) > 70:
                code = ',\n'.join([f'    {item}' for item in items])
                code = f'\n{code}\n'
        else:
            items = [indent(item, '    ') for item in items]
            code = ',\n'.join(items)
            code = f'\n{code}\n'

        return f'({code})'

    def visit_Constant(self, node):
        return '\n'.join(get_source(self.source_lines,
                                    node.lineno,
                                    node.col_offset,
                                    node.end_lineno,
                                    node.end_col_offset)[1])

    def visit_UnaryOp(self, node):
        return '-' + self.visit(node.operand)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        op = OPERATORS[type(node.op)]
        right = self.visit(node.right)

        return f'{left} {op} {right}'

    def generic_visit(self, node):
        raise Exception('unsupported node type {type(node)} in the styler')
