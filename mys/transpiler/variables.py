class Variables:
    """A class that keeps track of which variables that are defined in all
    branches, so that they can be used once they converges.

    """

    def __init__(self, context):
        self._context = context
        self._first_add = True
        self._local_variables = {}

    def add_branch(self, variables, raises_or_returns=False):
        """Add all variables defined in a branch. Should be called once for
        each branch.

        Does nothing the the branch raises or returns.

        """

        if raises_or_returns:
            return

        if self._first_add:
            for name, info in variables.items():
                self._local_variables[name] = info

            self._first_add = False
        else:
            to_remove = []

            for name, info in self._local_variables.items():
                new_info = variables.get(name)

                if not self.is_compatible_types(new_info, info):
                    to_remove.append(name)

            for name in to_remove:
                self._local_variables.pop(name)

    def defined(self):
        """A dictionary of all variables found in all branches.

        """

        return self._local_variables

    def is_compatible_types(self, new_info, info):
        if new_info is None:
            return False

        if new_info == info:
            return True

        if (self._context.is_trait_defined(info)
            and self._context.is_class_defined(new_info)
            and self._context.does_class_implement_trait(new_info, info)):
            return True

        return False
