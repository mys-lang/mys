from collections import defaultdict

from .utils import CompileError
from .utils import is_primitive_type
from .utils import is_snake_case
from .utils import split_dict_mys_type


class State:

    def __init__(self, variables, raises):
        self.variables = variables
        self.raises = raises


class SpecializedFunction:

    def __init__(self, function, call_module_name, call_node):
        self.function = function
        self.first_call_module_name = call_module_name
        self.first_call_node = call_node

    def __str__(self):
        return f'SpecializedFunction(function={self.function})'


class SpecializedClass:

    def __init__(self, definitions, call_module_name, call_node):
        self.definitions = definitions
        self.first_call_module_name = call_module_name
        self.first_call_node = call_node

    def __str__(self):
        return f'SpecializedClass(definitions={self.definitions})'


class Traceback:

    def __init__(self, source_lines):
        self.source_lines = source_lines
        self.entries = []
        self.index = -1
        self.name = None

    def add(self, lineno):
        if lineno - 1 < len(self.source_lines):
            code = self.source_lines[lineno - 1].strip()
        else:
            code = "known bug"

        code = code.replace('\\', '').replace('"', '\\"')
        self.entries.append((self.name, lineno, code))

        return len(self.entries) - 1

    def enter(self, name):
        self.name = name

        return '    __MYS_TRACEBACK_ENTER();'

    def exit(self):
        return '    __MYS_TRACEBACK_EXIT();'

    def set(self, lineno):
        index = self.add(lineno)

        return f'    __MYS_TRACEBACK_SET({index});'


class Context:
    """The context keeps track of defined functions, classes, traits,
    enums and variables in the current scope. Ot also provides other
    services, like unique numbers and full name convertions.

    """

    def __init__(self,
                 module_levels,
                 specialized_functions,
                 specialized_classes,
                 source_lines):
        self.name = '.'.join(module_levels)
        self._stack = [[]]
        self.local_variables = {}
        self._global_variables = {}
        self._classes = {}
        self._traits = {}
        self._functions = {}
        self._enums = {}
        self.return_mys_type = None
        self.mys_type = None
        self.unique_count = 0
        self.constants = {}
        self._name_to_full_name ={}
        self.specialized_functions = specialized_functions
        self.specialized_classes = specialized_classes
        self.comprehensions = []
        self._raises = [False]
        self.source_lines = source_lines
        self.class_name = None
        self.method_comprehensions = defaultdict(list)
        self.traceback = Traceback(source_lines)
        self.package = module_levels[0]

    def unique_number(self):
        self.unique_count += 1

        return self.unique_count

    def unique(self, name):
        return f'__{name}_{self.unique_number()}'

    def make_full_name(self, name):
        """Returns the fully qualified name (full_name) of given function,
        class, trait, enum or global variable name.

        """

        return self._name_to_full_name.get(name)

    def define_local_variable(self, name, mys_type, node):
        if self.is_local_variable_defined(name):
            raise CompileError(f"redefining variable '{name}'", node)

        if not is_snake_case(name):
            raise CompileError("local variable names must be snake case", node)

        if name in self._name_to_full_name:
            raise CompileError(f"redefining '{name}'", node)

        self.local_variables[name] = mys_type
        self._stack[-1].append(name)

    def is_local_variable_defined(self, name):
        """Returns true if given short local variable name is defined.

        """

        return name in self.local_variables

    def get_local_variable_type(self, name):
        return self.local_variables[name]

    def define_global_variable(self, name, full_name, mys_type, _node):
        self._global_variables[name] = mys_type
        self._name_to_full_name[name] = full_name

    def is_global_variable_defined(self, name):
        """Returns true if given name short global variable name is defined.

        """

        return name in self._global_variables

    def get_global_variable_type(self, name):
        return self._global_variables[name]

    def make_full_name_this_module(self, name):
        """Returns the fully qualified name (full_name) of given name as
        defined in the current module.

        """

        return f'{self.name}.{name}'

    def define_class(self, name, full_name, definitions):
        self._name_to_full_name[name] = full_name
        self._classes[full_name] = definitions

    def is_class_defined(self, name):
        """Returns true if given type is a class. Accepts both short names and
        fully qualified names.

        """

        if not isinstance(name, str):
            return False

        full_name = self._name_to_full_name.get(name, name)

        return full_name in self._classes

    def get_class_definitions(self, name):
        full_name = self._name_to_full_name.get(name, name)

        return self._classes[full_name]

    def define_trait(self, name, full_name, definitions):
        self._name_to_full_name[name] = full_name
        self._traits[full_name] = definitions

    def is_trait_defined(self, name):
        """Returns true if given type is a trait. Accepts both short names and
        fully qualified names.

        """

        if not isinstance(name, str):
            return False

        full_name = self._name_to_full_name.get(name, name)

        return full_name in self._traits

    def get_trait_definitions(self, name):
        full_name = self._name_to_full_name.get(name, name)

        return self._traits[full_name]

    def define_function(self, name, full_name, definitions):
        self._name_to_full_name[name] = full_name
        self._functions[full_name] = definitions

    def is_function_defined(self, full_name):
        """Returns true if given fully qualified function name is defined.

        """

        return full_name in self._functions

    def get_functions(self, full_name):
        return self._functions[full_name]

    def define_enum(self, name, full_name, definitions):
        self._name_to_full_name[name] = full_name
        self._enums[full_name] = definitions

    def is_enum_defined(self, name):
        """Returns true if given type is an enum. Accepts both short names and
        fully qualified names.

        """

        if not isinstance(name, str):
            return False

        full_name = self._name_to_full_name.get(name, name)

        return full_name in self._enums

    def get_enum_type(self, name):
        return self.get_enum_definitions(name).type

    def get_enum_definitions(self, name):
        full_name = self._name_to_full_name.get(name, name)

        return self._enums[full_name]

    def is_class_or_trait_defined(self, full_name):
        if self.is_class_defined(full_name):
            return True
        elif self.is_trait_defined(full_name):
            return True

        return False

    def is_type_defined(self, mys_type):
        if isinstance(mys_type, tuple):
            for item_mys_type in mys_type:
                if not self.is_type_defined(item_mys_type):
                    return False
        elif isinstance(mys_type, list):
            for item_mys_type in mys_type:
                if not self.is_type_defined(item_mys_type):
                    return False
        elif isinstance(mys_type, dict):
            key_mys_type, value_mys_type = split_dict_mys_type(mys_type)

            if not self.is_type_defined(key_mys_type):
                return False

            if not self.is_type_defined(value_mys_type):
                return False
        elif isinstance(mys_type, set):
            for item_mys_type in mys_type:
                if not self.is_type_defined(item_mys_type):
                    return False
        elif self.is_class_or_trait_defined(mys_type):
            return True
        elif self.is_enum_defined(mys_type):
            return True
        elif is_primitive_type(mys_type):
            return True
        elif mys_type in ('string', 'bytes', 'regex', 'regexmatch'):
            return True
        elif mys_type is None:
            return True
        else:
            return False

        return True

    def define_specialized_function(self, full_name, function, call_node):
        self.specialized_functions[full_name] = SpecializedFunction(
            function,
            self.name,
            call_node)

    def is_specialized_function_defined(self, full_name):
        return full_name in self.specialized_functions

    def get_specialized_function(self, full_name):
        return self.specialized_functions[full_name].function

    def define_specialized_class(self, full_name, definitions, call_node):
        self.specialized_classes[full_name] = SpecializedClass(
            definitions,
            self.name,
            call_node)

    def is_specialized_class_defined(self, full_name):
        return full_name in self.specialized_classes

    def get_specialized_class(self, full_name):
        return self.specialized_classes[full_name].definitions

    def push(self):
        self._stack.append([])
        self._raises.append(False)

    def pop(self):
        result = {}

        for name in self._stack[-1]:
            result[name] = self.local_variables.pop(name)

        self._stack.pop()

        return State(result, self._raises.pop())

    def set_always_raises(self, value):
        self._raises[-1] = value

    def __str__(self):
        result = ['Context:']
        result.append('  Local variables:')

        for name, value in self.local_variables.items():
            result.append(f'    {name}: {value}')

        result.append('  Global variables:')

        for name, value in self._global_variables.items():
            result.append(f'    {name}: {value}')

        result.append('  Classes:')

        for name, value in self._classes.items():
            result.append(f'    {name}: {value}')

        return '\n'.join(result)
