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
from .imports_visitor import ImportsVisitor
from .definitions import find_definitions
from .header_visitor import HeaderVisitor
from .source_visitor import SourceVisitor
from .base import has_docstring

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
                   source,
                   filename,
                   module_hpp,
                   module,
                   definitions,
                   skip_tests=False,
                   has_main=False):
    # print(module.upper())
    # print(definitions[module])
    namespace = 'mys::' + module_hpp[:-8].replace('/', '::')
    module_levels = module_hpp[:-8].split('/')
    source_lines = source.split('\n')
    header = HeaderVisitor(namespace,
                           module_levels,
                           source_lines,
                           definitions,
                           definitions[module],
                           has_main).visit(tree)
    source = SourceVisitor(module_levels,
                           module_hpp,
                           filename,
                           skip_tests,
                           namespace,
                           source_lines,
                           definitions,
                           definitions[module]).visit(tree)

    return header, source

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
        self.filename = filename
        self.module = module
        self.mys_path = mys_path
        self.module_hpp = module_hpp
        self.skip_tests = skip_tests
        self.hpp_path = hpp_path
        self.cpp_path = cpp_path
        self.has_main = has_main

def make_fully_qualified_names_type(mys_type, module, module_definitions):
    if isinstance(mys_type, list):
        return [make_fully_qualified_names_type(mys_type[0], module, module_definitions)]
    elif isinstance(mys_type, dict):
        return {
            make_fully_qualified_names_type(list(mys_type.keys())[0],
                                            module,
                                            module_definitions):
            make_fully_qualified_names_type(list(mys_type.values())[0],
                                            module,
                                            module_definitions)
        }
    elif isinstance(mys_type, tuple):
        return tuple([make_fully_qualified_names_type(item,
                                                      module,
                                                      module_definitions)
                      for item in mys_type])
    elif mys_type in module_definitions.classes:
        return f'{module}.{mys_type}'
    elif mys_type in module_definitions.traits:
        return f'{module}.{mys_type}'
    elif mys_type in module_definitions.enums:
        return f'{module}.{mys_type}'
    elif mys_type in module_definitions.imports:
        imported_module, new_type = module_definitions.imports[mys_type][0]

        return f'{imported_module}.{new_type}'
    else:
        return mys_type

def make_fully_qualified_names_function(function, module, module_definitions):
    function.returns = make_fully_qualified_names_type(function.returns,
                                                       module,
                                                       module_definitions)

    for param, _ in function.args:
        param.type = make_fully_qualified_names_type(param.type,
                                                     module,
                                                     module_definitions)

def make_fully_qualified_names_variable(module,
                                        variable_definition,
                                        module_definitions):
    variable_definition.type = make_fully_qualified_names_type(
        variable_definition.type,
        module,
        module_definitions)

def make_fully_qualified_names_class(module,
                                     class_definition,
                                     module_definitions):
    for base in list(class_definition.implements):
        node = class_definition.implements.pop(base)

        if base in module_definitions.traits:
            base = make_fully_qualified_names_type(base,
                                                   module,
                                                   module_definitions)
        elif base in module_definitions.imports:
            imported_module, name = module_definitions.imports[base][0]
            base = f'{imported_module}.{name}'
        else:
            raise CompileError('trait does not exist', node)

        class_definition.implements[base] = node

    for member in class_definition.members.values():
        member.type = make_fully_qualified_names_type(member.type,
                                                      module,
                                                      module_definitions)

    for methods in class_definition.methods.values():
        for method in methods:
            make_fully_qualified_names_function(method, module, module_definitions)

def make_fully_qualified_names_trait(module,
                                     trait_definition,
                                     module_definitions):
    for methods in trait_definition.methods.values():
        for method in methods:
            make_fully_qualified_names_function(method, module, module_definitions)

def make_fully_qualified_names_module(module, definitions):
    """Make variable types, members, parameters and return types and
    implemented traits fully qualified names.

    """

    module_definitions = definitions[module]

    for variable_definition in module_definitions.variables.values():
        make_fully_qualified_names_variable(module,
                                            variable_definition,
                                            module_definitions)

    for class_definition in module_definitions.classes.values():
        make_fully_qualified_names_class(module,
                                         class_definition,
                                         module_definitions)

    for trait_definition in module_definitions.traits.values():
        make_fully_qualified_names_trait(module,
                                         trait_definition,
                                         module_definitions)

    for functions in module_definitions.functions.values():
        for function in functions:
            make_fully_qualified_names_function(function, module, module_definitions)

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

        for source, tree in zip(sources, trees):
            definitions[source.module] = find_definitions(tree,
                                                          source.contents.split('\n'),
                                                          source.module_hpp[:-8].split('/'))
            source_lines = source.contents.split('\n')
            module_definitions = definitions[source.module]

            # ToDo: Should not be here, and check imported traits.
            for class_name, class_definitions in module_definitions.classes.items():
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

        for source, tree in zip(sources, trees):
            make_fully_qualified_names_module(source.module, definitions)

        for source, tree in zip(sources, trees):
            generated.append(transpile_file(tree,
                                            source.contents,
                                            source.mys_path,
                                            source.module_hpp,
                                            source.module,
                                            definitions,
                                            source.skip_tests,
                                            source.has_main))

        return generated
    except CompileError as e:
        line = source.contents.splitlines()[e.lineno - 1]
        marker_line = ' ' * e.offset + '^'

        raise Exception(
            style_traceback(f'  File "{source.mys_path}", line {e.lineno}\n'
                            f'    {line}\n'
                            f'    {marker_line}\n'
                            f'CompileError: {e.message}'))
