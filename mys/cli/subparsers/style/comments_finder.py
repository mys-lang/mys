from ....parser import ast
from .utils import get_function_or_class_node_start
from .utils import get_source


class CommentsFinder(ast.NodeVisitor):
    """Look for comments and blank lines in source code not spanned by AST
    nodes.

    """

    def __init__(self, source_lines):
        self.comments = []
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
        lineno, source_lines = self.get_source(lineno, col_offset)
        filtered_source_lines = []

        for i, line in enumerate(source_lines, lineno):
            if line == '':
                if line == self.source_lines[i - 1]:
                    filtered_source_lines.append(line)
            else:
                pos = line.find('#')

                if pos != -1:
                    if line != self.source_lines[i - 1]:
                        line = line[pos:]

                    filtered_source_lines.append(line)

            if not filtered_source_lines:
                lineno += 1

        if filtered_source_lines:
            self.comments.append((lineno, filtered_source_lines))

    def visit_Module(self, node):
        for item in node.body:
            self.visit(item)

        if self.source_lines:
            self.add_comments(len(self.source_lines), len(self.source_lines[-1]))

    def visit_FunctionDef(self, node):
        lineno, col_offset = get_function_or_class_node_start(node)
        self.add_comments(lineno, col_offset)
        self.prev_end_lineno = node.lineno
        self.prev_end_col_offset = node.col_offset
        self.visit(node.args)

        for item in node.body:
            self.visit(item)

    def visit_ClassDef(self, node):
        lineno, col_offset = get_function_or_class_node_start(node)
        self.add_comments(lineno, col_offset)
        self.prev_end_lineno = node.lineno
        self.prev_end_col_offset = node.col_offset

        for item in node.body:
            self.visit(item)

    def generic_visit(self, node):
        if hasattr(node, 'lineno'):
            self.add_comments(node.lineno, node.col_offset)
            self.prev_end_lineno = node.end_lineno
            self.prev_end_col_offset = node.end_col_offset

        super().generic_visit(node)
