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
            local_variables = {}

            for name, info in self._local_variables.items():
                info = self.get_compatible_type(variables.get(name), info)

                if info is not None:
                    local_variables[name] = info

            self._local_variables = local_variables

    def defined(self):
        """A dictionary of all variables found in all branches.

        """

        return self._local_variables

    def get_compatible_type(self, new_info, info):
        if new_info == info:
            return info

        if (self._context.is_trait_defined(info)
            and self._context.is_class_defined(new_info)
            and self._context.does_class_implement_trait(new_info, info)):
            return info

        if (self._context.is_trait_defined(new_info)
            and self._context.is_class_defined(info)
            and self._context.does_class_implement_trait(info, new_info)):
            return new_info

        if (self._context.is_class_defined(new_info)
            and self._context.is_class_defined(info)):
            new_implements = self._context.get_class_definitions(new_info).implements
            implements = self._context.get_class_definitions(info).implements

            for new_item in new_implements:
                for item in implements:
                    if new_item.type == item.type:
                        return item.type

        return None
