def find_root_modules(modules):
    """Returns a list of modules that no other module imports from.

    """

    module_imports = {name: 0 for name in modules}

    for neighbors in modules.values():
        for neighbor in neighbors:
            module_imports[neighbor] += 1

    return sorted([name for name, count in module_imports.items() if count == 0])


class Importer:

    def __init__(self, modules):
        self.modules = modules
        self.seen = set()

    def import_module(self, name):
        """Recursivelly find all modules given module imports and the module
        iteslf in the order they shall be initialised.

        """

        # Break circular imports.
        if name in self.seen:
            return []

        self.seen.add(name)
        ordered = []

        for module in self.modules[name]:
            ordered += self.import_module(module)

        ordered.append(name)

        return ordered


def resolve_import_order(modules):
    """Returns a list of all modules ordered by import order suitable for
    initialization. Best effort for cyclic imports.

    """

    root_modules = find_root_modules(modules)
    ordered = []

    for root_module in root_modules:
        ordered += Importer(modules).import_module(root_module)

    for module in sorted(modules):
        if module not in ordered:
            ordered += Importer(modules).import_module(module)

    return ordered
