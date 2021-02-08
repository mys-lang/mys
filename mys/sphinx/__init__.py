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

    def run(self):
        mys_file_path = self.arguments[0]

        with open(mys_file_path, 'r') as fin:
            source = fin.read()

        tree = ast.parse(source)
        definitions = find_definitions(tree,
                                       source.splitlines(),
                                       [mys_file_path[:-4].split('/')],
                                       'lib')
        items = []

        for functions in definitions.functions.values():
            for function in functions:
                if function.is_test:
                    continue

                text = function.signature_string()

                if function.docstring is not None:
                    text += '\n\n'
                    lines = function.docstring.splitlines()
                    text += indent(lines[0] + dedent('\n'.join(lines[1:])), '    ')

                items.append(nodes.literal_block('', '', nodes.Text(text)))

        return items


def setup(app):
    app.add_directive('mysfile', MysFileDirective)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True
    }
