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
from ..transpiler.utils import METHOD_OPERATORS
from ..transpiler.utils import format_mys_type
from ..transpiler.utils import has_docstring
from ..transpiler.utils import is_private
from ..version import __version__


def is_private_method(name):
    if name in METHOD_OPERATORS:
        return False
    elif name == '__init__':
        return False
    else:
        return is_private(name)


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
        if docstring is None:
            return ''

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

            text = f'class {klass.name}{bases}:\n'
            public_members = [member
                              for member in klass.members.values()
                              if not is_private(member.name)]

            if klass.docstring is not None:
                text += self.process_docstring(klass.docstring, 4)
                text += '\n'

                if len(public_members) > 0:
                    text += '\n'

            for member in public_members:
                text += f'    {member.name}: {format_mys_type(member.type)}\n'

            for methods in klass.methods.values():
                for method in methods:
                    if is_private_method(method.name):
                        continue

                    text += '\n'

                    if method.raises:
                        raises = ', '.join(method.raises)
                        text += f'    @raises({raises})\n'

                    signature_string = method.signature_string(True)
                    text += indent(f'def {signature_string}:', '    ')
                    text += '\n'

                    if method.docstring is not None:
                        text += self.process_docstring(method.docstring, 8)

                    text = text.strip()
                    text += '\n'

            self.items.append(self.make_node(text))

    def process_traits(self, definitions):
        for trait in definitions.traits.values():
            if is_private(trait.name):
                continue

            text = '@trait\n'
            text += f'class {trait.name}:\n'

            if trait.docstring is not None:
                text += self.process_docstring(trait.docstring, 4)
                text += '\n'

            for methods in trait.methods.values():
                for method in methods:
                    if is_private_method(method.name):
                        continue

                    text += '\n'
                    text += f'    def {method.signature_string(True)}:'
                    text += '\n'

                    if method.docstring is not None:
                        text += self.process_docstring(method.docstring, 8)

                    text = text.strip()
                    text += '\n'

            self.items.append(self.make_node(text))

    def process_functions(self, definitions):
        for functions in definitions.functions.values():
            for function in functions:
                if function.is_test:
                    continue

                if is_private(function.name):
                    continue

                for name in function.raises:
                    text += f'@raises({name})\n'

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
