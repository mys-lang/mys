import traceback

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexer import RegexLexer
from pygments.lexer import bygroups
from pygments.lexer import using
from pygments.lexers import PythonLexer
from pygments.style import Style
from pygments.token import Generic
from pygments.token import Name
from pygments.token import Number
from pygments.token import Text

from ..parser import ast
from .class_transformer import ClassTransformer
from .definitions import find_definitions
from .definitions import make_fully_qualified_names_module
from .header_visitor import HeaderVisitor
from .imports_visitor import ImportsVisitor
from .source_visitor import SourceVisitor
from .utils import CompileError
from .utils import has_docstring


class TranspilerError(Exception):
    pass


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


def is_trait_method_pure(method):
    """A trait method is pure if it has no implementation.

    """

    body = method.node.body

    if has_docstring(method.node):
        if len(body) == 1:
            return True

        node = body[1]
    elif len(body) == 1:
        node = body[0]
    else:
        return False

    return isinstance(node, ast.Pass)


def style_traceback(tb):
    return highlight(tb,
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
                   has_main,
                   specialized_functions,
                   specialized_classes):
    namespace = 'mys::' + '::'.join(module_levels)
    header_visitor = HeaderVisitor(namespace,
                                   module_levels,
                                   module_hpp,
                                   source_lines,
                                   definitions,
                                   module_definitions,
                                   has_main)
    header_visitor.visit(tree)
    source_visitor = SourceVisitor(namespace,
                                   module_levels,
                                   module_hpp,
                                   filename,
                                   source_lines,
                                   definitions,
                                   module_definitions,
                                   skip_tests,
                                   specialized_functions,
                                   specialized_classes)
    source_visitor.visit(tree)

    return header_visitor, source_visitor


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


def find_trait_in_module(implements_trait_name, module_definitions):
    for trait_name, trait_definitions in module_definitions.traits.items():
        if trait_name == implements_trait_name:
            return trait_definitions

    return None


def find_trait_in_imports(implements_trait_name,
                          module_definitions,
                          definitions):
    for as_name, import_definitions in module_definitions.imports.items():
        if as_name == implements_trait_name:
            imported_module_name, name = import_definitions[0]
            imported_module_definitions = definitions[imported_module_name]

            return find_trait_in_module(name, imported_module_definitions)

def find_trait(implements_trait_name,
               class_definitions,
               module_definitions,
               definitions):
    trait_definitions = find_trait_in_module(implements_trait_name,
                                             module_definitions)

    if trait_definitions is not None:
        return trait_definitions

    trait_definitions = find_trait_in_imports(implements_trait_name,
                                              module_definitions,
                                              definitions)

    if trait_definitions is not None:
        return trait_definitions

    raise CompileError(
        "trait does not exist",
        class_definitions.implements[implements_trait_name])


def ensure_that_trait_methods_are_implemented(module_definitions,
                                              definitions):
    for class_definitions in module_definitions.classes.values():
        for implements_trait_name in class_definitions.implements:
            if implements_trait_name == 'Error':
                continue

            trait_definitions = find_trait(implements_trait_name,
                                           class_definitions,
                                           module_definitions,
                                           definitions)

            for method_name, methods in trait_definitions.methods.items():
                if method_name in class_definitions.methods:
                    continue

                if is_trait_method_pure(methods[0]):
                    raise CompileError(
                        f"trait method '{method_name}' is not implemented",
                        class_definitions.implements[trait_definitions.name])

                class_definitions.methods[method_name].append(methods[0])


def transpile(sources):
    visitors = {}
    specialized_functions = {}
    specialized_classes = {}
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

    source = None

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

        for source in sources:
            ensure_that_trait_methods_are_implemented(definitions[source.module],
                                                      definitions)

        for source in sources:
            make_fully_qualified_names_module(source.module,
                                              definitions[source.module])

        for source, tree in zip(sources, trees):
            header_visitor, source_visitor = transpile_file(
                tree,
                source.source_lines,
                source.mys_path,
                source.module_hpp,
                source.module_levels,
                definitions[source.module],
                definitions,
                source.skip_tests,
                source.has_main,
                specialized_functions,
                specialized_classes)
            visitors[source.module] = (header_visitor, source_visitor)

        for name, (function, _caller_modules) in specialized_functions.items():
            header_visitor, source_visitor = visitors['.'.join(name.split('.')[:-1])]
            header_visitor.visit_specialized_function(function)
            source_visitor.visit_specialized_function(function)

        for name, (class_definitions, _caller_modules) in specialized_classes.items():
            header_visitor, source_visitor = visitors['.'.join(name.split('.')[:-1])]
            header_visitor.visit_specialized_class(class_definitions)
            source_visitor.visit_specialized_class(class_definitions.name,
                                                   class_definitions)

        return [
            (header_visitor.format_early_hpp(),
             header_visitor.format_hpp(),
             source_visitor.format_cpp())
            for header_visitor, source_visitor in visitors.values()
        ]
    except CompileError as e:
        line = source.source_lines[e.lineno - 1]
        marker_line = ' ' * e.offset + '^'

        raise TranspilerError(
            style_traceback(f'  File "{source.mys_path}", line {e.lineno}\n'
                            f'    {line}\n'
                            f'    {marker_line}\n'
                            f'CompileError: {e.message}'))
