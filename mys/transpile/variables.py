class Variables:
    """A class that keeps track of which variables that are defined in all
    branches, so that they can be used once they converges.

    """

    def __init__(self):
        self._first_add = True
        self._local_variables = {}

    def add_branch(self, variables):
        """Add all variables defined in a branch. Should be called once for
        each branch.

        """

        if self._first_add:
            for name, info in variables.items():
                self._local_variables[name] = info

            self._first_add = False
        else:
            to_remove = []

            for name, info in self._local_variables.items():
                new_info = variables.get(name)

                if new_info is None or new_info != info:
                    to_remove.append(name)

            for name in to_remove:
                self._local_variables.pop(name)

    def defined(self):
        """A dictionary of all variables found in all branches.

        """

        return self._local_variables
