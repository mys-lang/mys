# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Control of and utilities for debugging."""

import contextlib
import os
import sys

# When debugging, it can be helpful to force some options, especially when
# debugging the configuration mechanisms you usually use to control debugging!
# This is a list of forced debugging options.
FORCED_DEBUG = []
FORCED_DEBUG_FILE = None


class DebugControl:
    """Control and output for debugging."""

    show_repr_attr = False      # For SimpleReprMixin

    def __init__(self, options, output):
        """Configure the options and output file for debugging."""
        self.options = list(options) + FORCED_DEBUG
        self.suppress_callers = False

        filters = []
        self.output = DebugOutputFile.get_one(
            output,
            show_process=self.should('process'),
            filters=filters,
        )
        self.raw_output = self.output.outfile

    def should(self, option):
        """Decide whether to output debug information in category `option`."""
        if option == "callers" and self.suppress_callers:
            return False
        return (option in self.options)

    @contextlib.contextmanager
    def without_callers(self):
        """A context manager to prevent call stacks from being logged."""
        old = self.suppress_callers
        self.suppress_callers = True
        try:
            yield
        finally:
            self.suppress_callers = old


class NoDebugging:
    """A replacement for DebugControl that will never try to do anything."""
    def should(self, option):               # pylint: disable=unused-argument
        """Should we write debug messages?  Never."""
        return False


class SimpleReprMixin:
    """A mixin implementing a simple __repr__."""
    simple_repr_ignore = ['simple_repr_ignore', '$coverage.object_id']


class DebugOutputFile:                              # pragma: debugging
    """A file-like object that includes pid and cwd information."""
    def __init__(self, outfile, show_process, filters):
        self.outfile = outfile
        self.show_process = show_process
        self.filters = list(filters)

    SYS_MOD_NAME = '$coverage.debug.DebugOutputFile.the_one'

    @classmethod
    def get_one(cls, fileobj=None, show_process=True, filters=(), interim=False):
        """Get a DebugOutputFile.

        If `fileobj` is provided, then a new DebugOutputFile is made with it.

        If `fileobj` isn't provided, then a file is chosen
        (COVERAGE_DEBUG_FILE, or stderr), and a process-wide singleton
        DebugOutputFile is made.

        `show_process` controls whether the debug file adds process-level
        information, and filters is a list of other message filters to apply.

        `filters` are the text filters to apply to the stream to annotate with
        pids, etc.

        If `interim` is true, then a future `get_one` can replace this one.

        """
        if fileobj is not None:
            # Make DebugOutputFile around the fileobj passed.
            return cls(fileobj, show_process, filters)

        # Because of the way igor.py deletes and re-imports modules,
        # this class can be defined more than once. But we really want
        # a process-wide singleton. So stash it in sys.modules instead of
        # on a class attribute. Yes, this is aggressively gross.
        the_one, is_interim = sys.modules.get(cls.SYS_MOD_NAME, (None, True))
        if the_one is None or is_interim:
            if fileobj is None:
                debug_file_name = os.environ.get("COVERAGE_DEBUG_FILE",
                                                 FORCED_DEBUG_FILE)
                if debug_file_name:
                    fileobj = open(debug_file_name, "a")
                else:
                    fileobj = sys.stderr
            the_one = cls(fileobj, show_process, filters)
            sys.modules[cls.SYS_MOD_NAME] = (the_one, interim)
        return the_one

    def write(self, _text):
        """Just like file.write, but filter through all our filters."""
        self.outfile.flush()

    def flush(self):
        """Flush our file."""
        self.outfile.flush()
