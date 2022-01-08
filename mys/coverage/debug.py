# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Control of and utilities for debugging."""


class SimpleReprMixin:
    """A mixin implementing a simple __repr__."""
    simple_repr_ignore = ['simple_repr_ignore', '$coverage.object_id']
