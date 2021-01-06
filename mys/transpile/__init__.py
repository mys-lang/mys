import traceback
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexer import RegexLexer
from pygments.lexer import bygroups
from pygments.lexer import using
from pygments.lexers import PythonLexer
from pygments.style import Style
from pygments.token import Text
from pygments.token import Name
from pygments.token import Number
from pygments.token import Generic
from ..parser import ast
from .utils import CompileError
from .utils import has_docstring
from .imports_visitor import ImportsVisitor
from .definitions import find_definitions
from .definitions import make_fully_qualified_names_module
from .header_visitor import HeaderVisitor
from .source_visitor import SourceVisitor
from .class_transformer import ClassTransformer


class TracebackLexer(RegexLexer):

    tokens = {
        'root': [
            (r'^(  File )("[^"]+")(, line )(\d+)(\n)',
             bygroups(Generic.Error, Name.Builtin, Generic.Error, Number, Text)),
            (r'^(\s+?)(\^)(\n)',
             bygroups(Text, Generic.Error, Text)),
            (r'^(    )(.+)(\n)',
             bygroups(Text, using(PythonLexer), Text)),
            (r'^([^:]+)(: )(.+)(\n)',
             bygroups(Generic.Escape, Text, Name, Text), '#pop')
        ]
    }


def is_trait_method_pure(method, source_lines):
    """A trait method is pure if it has no implementation.

    """

    body = method.node.body

    if has_docstring(method.node, source_lines):
        if len(body) == 1:
            return True

        node = body[1]
    elif len(body) == 1:
        node = body[0]
    else:
        return False

    return isinstance(node, ast.Pass)


def style_traceback(traceback):
    return highlight(traceback,
                     TracebackLexer(),
                     Terminal256Formatter(style='monokai'))


def transpile_file(tree,
                   source_lines,
                   filename,
                   module_hpp,
                   module_levels,
                   module_definitions,
                   definitions,
                   skip_tests,
                   has_main):
    namespace = 'mys::' + '::'.join(module_levels)
    early_header, header = HeaderVisitor(namespace,
                                         module_levels,
                                         module_hpp,
                                         source_lines,
                                         definitions,
                                         module_definitions,
                                         has_main).visit(tree)
    source = SourceVisitor(namespace,
                           module_levels,
                           module_hpp,
                           filename,
                           source_lines,
                           definitions,
                           module_definitions,
                           skip_tests).visit(tree)

    return early_header, header, source


class Source:

    def __init__(self,
                 contents,
                 filename='',
                 module='',
                 mys_path='',
                 module_hpp='',
                 skip_tests=False,
                 hpp_path='',
                 cpp_path='',
                 has_main=False):
        self.contents = contents
        self.source_lines = contents.splitlines()
        self.source_lines.append("''")  # Special line used for default char value.
        self.filename = filename
        self.module = module
        self.module_levels = module.split('.')
        self.mys_path = mys_path
        self.module_hpp = module_hpp
        self.skip_tests = skip_tests
        self.hpp_path = hpp_path
        self.cpp_path = cpp_path
        self.has_main = has_main


def check_that_trait_methods_are_implemented(module_definitions,
                                             definitions,
                                             source_lines):
    # ToDo: Check methods in imported traits.
    for class_definitions in module_definitions.classes.values():
        for implements_trait_name in class_definitions.implements:
            for trait_name, trait_definitions in module_definitions.traits.items():
                if trait_name != implements_trait_name:
                    continue

                for method_name, methods in trait_definitions.methods.items():
                    if method_name in class_definitions.methods:
                        continue

                    if is_trait_method_pure(methods[0], source_lines):
                        raise CompileError(
                            f"trait method '{method_name}' is not implemented",
                            class_definitions.implements[trait_name])

                    class_definitions.methods[method_name].append(methods[0])


def transpile(sources):
    generated = []
    trees = []
    definitions = {}

    try:
        for source in sources:
            trees.append(ast.parse(source.contents, source.mys_path))
    except SyntaxError:
        lines = traceback.format_exc(0).splitlines()

        if 'Traceback (most recent call last):' in lines[0]:
            lines = lines[1:]

        raise Exception(style_traceback('\n'.join(lines)))

    try:
        for source, tree in zip(sources, trees):
            ImportsVisitor().visit(tree)

        for i in range(len(trees)):
            trees[i] = ast.fix_missing_locations(
                ClassTransformer(len(source.source_lines)).visit(trees[i]))

        for source, tree in zip(sources, trees):
            definitions[source.module] = find_definitions(tree,
                                                          source.source_lines,
                                                          source.module_levels)
            check_that_trait_methods_are_implemented(definitions[source.module],
                                                     definitions,
                                                     source.source_lines)

        for source in sources:
            make_fully_qualified_names_module(source.module,
                                              definitions[source.module])

        for source, tree in zip(sources, trees):
            generated.append(transpile_file(tree,
                                            source.source_lines,
                                            source.mys_path,
                                            source.module_hpp,
                                            source.module_levels,
                                            definitions[source.module],
                                            definitions,
                                            source.skip_tests,
                                            source.has_main))

        return generated
    except CompileError as e:
        line = source.source_lines[e.lineno - 1]
        marker_line = ' ' * e.offset + '^'

        raise Exception(
            style_traceback(f'  File "{source.mys_path}", line {e.lineno}\n'
                            f'    {line}\n'
                            f'    {marker_line}\n'
                            f'CompileError: {e.message}'))
