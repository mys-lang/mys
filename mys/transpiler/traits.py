from ..parser import ast
from .utils import CompileError
from .utils import has_docstring


def _is_trait_method_pure(method):
    """A trait method is pure if it has no implementation. That is, the
    body is a docstring and/or one or more pass.

    """

    body = method.node.body
    body_iter = iter(body)

    if has_docstring(method.node):
        if len(body) == 1:
            return True

        next(body_iter)

    for item in body_iter:
        if not isinstance(item, ast.Pass):
            return False

    return True


def _find_trait_in_module(trait_name, module_definitions):
    return module_definitions.traits.get(trait_name)


def _find_trait_in_imports(implements_trait_name,
                           module_definitions,
                           definitions):
    import_definitions = module_definitions.imports.get(implements_trait_name)

    if import_definitions is None:
        return None

    imported_module_name, name = import_definitions[0]
    imported_module_definitions = definitions[imported_module_name]

    return _find_trait_in_module(name, imported_module_definitions)


def _find_trait(implements_trait_name,
                class_definitions,
                module_definitions,
                definitions):
    trait_definitions = _find_trait_in_module(implements_trait_name,
                                              module_definitions)

    if trait_definitions is not None:
        return trait_definitions

    trait_definitions = _find_trait_in_imports(implements_trait_name,
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

            trait_definitions = _find_trait(implements_trait_name,
                                            class_definitions,
                                            module_definitions,
                                            definitions)

            for method_name, methods in trait_definitions.methods.items():
                if method_name in class_definitions.methods:
                    continue

                if _is_trait_method_pure(methods[0]):
                    raise CompileError(
                        f"pure trait method '{method_name}' is not implemented",
                        class_definitions.implements[trait_definitions.name])

                class_definitions.methods[method_name].append(methods[0])
