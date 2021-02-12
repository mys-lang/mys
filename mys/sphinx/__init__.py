import os
from textwrap import dedent
from textwrap import indent
from textwrap import wrap

from docutils import nodes
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
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
        self.process_enums(definitions)
        self.process_traits(definitions)
        self.process_classes(definitions)
        self.process_functions(definitions)

        return self.items

    def process_enums(self, definitions):
        for enum in definitions.enums.values():
            if is_private(enum.name):
                continue

            text = f'@enum({enum.type})\n'
            text += f'class {enum.name}:\n'

            if enum.docstring is not None:
                text += self.process_docstring(enum.docstring, 4)
                text += '\n\n'

            for member_name, _ in enum.members:
                text += f'    {member_name}'
                text += '\n'

            self.items.append(self.make_node(text))

    def process_docstring(self, docstring, indention):
        lines = docstring.splitlines()
        text = '"""'
        text += indent(lines[0] + '\n' + dedent('\n'.join(lines[1:])),
                       ' ' * indention).rstrip()
        text += '"""'

        return text

    def make_node(self, text):
        text = highlight(text, PythonLexer(), HtmlFormatter())

        return nodes.raw('',
                         text.replace('&quot;&quot;&quot;', ''),
                         format='html')

    def process_classes(self, definitions):
        for klass in definitions.classes.values():
            if is_private(klass.name):
                continue

            bases = ', '.join(klass.implements)

            if bases:
                bases = f'({bases})'

            text = f'class {klass.name}{bases}:'

            for methods in klass.methods.values():
                for method in methods:
                    if is_private(method.name):
                        continue

                    text += '\n\n'
                    text += f'    def {method.signature_string(True)}:'
                    text += '\n'

                    if method.docstring is not None:
                        text += self.process_docstring(method.docstring, 8)

                    text = text.strip()

            self.items.append(self.make_node(text))

    def process_traits(self, definitions):
        for trait in definitions.traits.values():
            if is_private(trait.name):
                continue

            text = '@trait\n'
            text += f'class {trait.name}:'

            for methods in trait.methods.values():
                for method in methods:
                    if is_private(method.name):
                        continue

                    text += '\n\n'
                    text += f'    def {method.signature_string(True)}:'
                    text += '\n'

                    if method.docstring is not None:
                        text += self.process_docstring(method.docstring, 8)

                    text = text.strip()

            self.items.append(self.make_node(text))

    def process_functions(self, definitions):
        for functions in definitions.functions.values():
            for function in functions:
                if function.is_test:
                    continue

                if is_private(function.name):
                    continue

                text = f'def {function.signature_string(False)}:'
                text += '\n'

                if function.docstring is not None:
                    text += self.process_docstring(function.docstring, 4)

                self.items.append(self.make_node(text))


def setup(app):
    app.add_directive('mysfile', MysFileDirective)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True
    }
