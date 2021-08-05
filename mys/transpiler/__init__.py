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
from .coverage_transformer import CoverageTransformer
from .definitions import find_definitions
from .definitions import make_fully_qualified_names_module
from .header_visitor import HeaderVisitor
from .import_order import resolve_import_order
from .imports_visitor import ImportsVisitor
from .source_visitor import SourceVisitor
from .traits import ensure_that_trait_methods_are_implemented
from .utils import CompileError


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


def format_location_source(source, lineno, offset):
    line = source.source_lines[lineno - 1]
    marker_line = ' ' * offset + '^'

    return (f'  File "{source.mys_path}", line {lineno}\n'
            f'    {line}\n'
            f'    {marker_line}\n')


def style_traceback(tb):
    return highlight(tb,
                     TracebackLexer(),
                     Terminal256Formatter(style='monokai'))


def transpile_file(tree,
                   source_lines,
                   filename,
                   version,
                   module_hpp,
                   module_levels,
                   module_definitions,
                   definitions,
                   skip_tests,
                   has_main,
                   specialized_functions,
                   specialized_classes,
                   coverage_variables):
    namespace = 'mys::' + '::'.join(module_levels)
    source_visitor = SourceVisitor(namespace,
                                   module_levels,
                                   module_hpp,
                                   filename,
                                   version,
                                   source_lines,
                                   definitions,
                                   module_definitions,
                                   skip_tests,
                                   specialized_functions,
                                   specialized_classes,
                                   coverage_variables)
    source_visitor.visit(tree)
    header_visitor = HeaderVisitor(namespace,
                                   module_levels,
                                   module_hpp,
                                   source_lines,
                                   definitions,
                                   module_definitions,
                                   has_main,
                                   specialized_classes,
                                   source_visitor.method_comprehensions)
    header_visitor.visit(tree)

    return header_visitor, source_visitor


class Source:

    def __init__(self,
                 contents,
                 filename='',
                 version='',
                 module='',
                 mys_path='',
                 module_hpp='',
                 skip_tests=False,
                 hpp_path='',
                 cpp_path='',
                 has_main=False):
        self.contents = contents
        self.source_lines = contents.splitlines()
        self.filename = filename
        self.version = version
        self.module = module
        self.module_levels = module.split('.')
        self.mys_path = mys_path
        self.module_hpp = module_hpp
        self.skip_tests = skip_tests
        self.hpp_path = hpp_path
        self.cpp_path = cpp_path
        self.has_main = has_main
        self.coverage_variables = {}

    def __str__(self):
        return '\n'.join([
            'Source:',
            f'  module: {self.module}',
            f'  filename: {self.filename}',
            f'  mys_path: {self.mys_path}',
            f'  skip_tests: {self.skip_tests}'
        ])

def transpile(sources, coverage=False):
    visitors = {}
    specialized_functions = {}
    specialized_classes = {}
    trees = []
    definitions = {}
    source_by_module = {source.module: source for source in sources}

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

        if coverage:
            for source, i in zip(sources, range(len(trees))):
                coverage_transformer = CoverageTransformer(source.contents)
                trees[i] = ast.fix_missing_locations(
                    coverage_transformer.visit(trees[i]))
                source.coverage_variables = coverage_transformer.variables()

        for source, i in zip(sources, range(len(trees))):
            trees[i] = ast.fix_missing_locations(ClassTransformer().visit(trees[i]))

        for source, tree in zip(sources, trees):
            definitions[source.module] = find_definitions(tree,
                                                          source.source_lines,
                                                          source.module_levels,
                                                          source.module)

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
                source.version,
                source.module_hpp,
                source.module_levels,
                definitions[source.module],
                definitions,
                source.skip_tests,
                source.has_main,
                specialized_functions,
                specialized_classes,
                source.coverage_variables)
            visitors[source.module] = (header_visitor, source_visitor)

        for name, function in specialized_functions.items():
            header_visitor, source_visitor = visitors['.'.join(name.split('.')[:-1])]
            header_visitor.visit_specialized_function(function.function)

            try:
                source_visitor.visit_specialized_function(function.function)
            except CompileError as e:
                raise TranspilerError(
                    style_traceback(
                        format_location_source(
                            source_by_module[function.first_call_module_name],
                            function.first_call_node.lineno,
                            function.first_call_node.col_offset)
                        + format_location_source(
                            source_by_module[function.function.module_name],
                            e.lineno,
                            e.offset)
                        + f'CompileError: {e.message}'))

        for name, klass in specialized_classes.items():
            header_visitor, source_visitor = visitors['.'.join(name.split('.')[:-1])]
            header_visitor.visit_specialized_class(name.split('.')[-1],
                                                   klass.definitions)

            try:
                source_visitor.visit_specialized_class(name.split('.')[-1],
                                                       klass.definitions)
            except CompileError as e:
                raise TranspilerError(
                    style_traceback(
                        format_location_source(
                            source_by_module[klass.first_call_module_name],
                            klass.first_call_node.lineno,
                            klass.first_call_node.col_offset)
                        + format_location_source(
                            source_by_module[klass.definitions.module_name],
                            e.lineno,
                            e.offset)
                        + f'CompileError: {e.message}'))

        module_imports = {}

        for source in sources:
            module_imports[source.module] = []

            for imports in definitions[source.module].imports.values():
                for imported_module, _ in imports:
                    if imported_module not in module_imports[source.module]:
                        module_imports[source.module].append(imported_module)

        ordered_modules = resolve_import_order(module_imports)
        last_source_visitor = visitors[ordered_modules[-1]][1]
        last_source_visitor.add_application_init(ordered_modules)
        last_source_visitor.add_application_exit(ordered_modules)

        return [
            (header_visitor.format_early_hpp(),
             header_visitor.format_hpp(),
             source_visitor.format_cpp())
            for header_visitor, source_visitor in visitors.values()
        ]
    except CompileError as e:
        raise TranspilerError(
            style_traceback(
                format_location_source(source, e.lineno, e.offset)
                + f'CompileError: {e.message}'))
