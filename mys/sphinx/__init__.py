import os
from textwrap import dedent
from textwrap import indent
from textwrap import wrap

from docutils import nodes
from sphinx.directives import SphinxDirective
from sphinx.locale import _

from ..parser import ast
from ..transpiler.definitions import find_definitions
from ..transpiler.utils import has_docstring
from ..transpiler.utils import is_private
from ..version import __version__


class MysFileDirective(SphinxDirective):
    required_arguments = 1
    has_content = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []

    def run(self):
        mys_file_path = os.path.join('..', self.arguments[0])

        with open(mys_file_path, 'r') as fin:
            source = fin.read()

        tree = ast.parse(source)
        definitions = find_definitions(tree,
                                       source.splitlines(),
                                       mys_file_path[:-4].split('/'),
                                       'lib')
        self.process_classes(definitions)
        self.process_functions(definitions)

        return self.items

    def process_classes(self, definitions):
        for klass in definitions.classes.values():
            if is_private(klass.name):
                continue

            text = f'class {klass.name}\n\n'

            for methods in klass.methods.values():
                for method in methods:
                    if is_private(method.name):
                        continue

                    text += '    def ' + method.signature_string()
                    text += '\n\n'

                    if method.docstring is not None:
                        lines = method.docstring.splitlines()
                        text += indent(
                            lines[0] + '\n' + dedent('\n'.join(lines[1:])),
                            '        ')

            self.items.append(nodes.literal_block('text', '', nodes.Text(text)))

    def process_functions(self, definitions):
        for functions in definitions.functions.values():
            for function in functions:
                if function.is_test:
                    continue

                if is_private(function.name):
                    continue

                text = 'def ' + function.signature_string()
                text += '\n\n'

                if function.docstring is not None:
                    lines = function.docstring.splitlines()
                    text += indent(lines[0] + '\n' + dedent('\n'.join(lines[1:])),
                                   '    ')

                self.items.append(nodes.literal_block('text', '', nodes.Text(text)))


def setup(app):
    app.add_directive('mysfile', MysFileDirective)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True
    }
