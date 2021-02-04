# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Control of and utilities for debugging."""

import contextlib
import inspect
import itertools
import os
import sys

from .misc import isolate_module

os = isolate_module(os)


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

    def write(self, msg):
        """Write a line of debug output.

        `msg` is the line to write. A newline will be appended.

        """
        self.output.write(msg+"\n")
        if self.should('self'):
            caller_self = inspect.stack()[1][0].f_locals.get('self')
            if caller_self is not None:
                self.output.write("self: {!r}\n".format(caller_self))
        self.output.flush()


class NoDebugging:
    """A replacement for DebugControl that will never try to do anything."""
    def should(self, option):               # pylint: disable=unused-argument
        """Should we write debug messages?  Never."""
        return False


class SimpleReprMixin:
    """A mixin implementing a simple __repr__."""
    simple_repr_ignore = ['simple_repr_ignore', '$coverage.object_id']

    def __repr__(self):
        show_attrs = (
            (k, v) for k, v in self.__dict__.items()
            if getattr(v, "show_repr_attr", True)
            and not callable(v)
            and k not in self.simple_repr_ignore
        )
        return "<{klass} @0x{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self),
            attrs=" ".join("{}={!r}".format(k, v) for k, v in show_attrs),
            )


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


OBJ_IDS = itertools.count()
CALLS = itertools.count()
OBJ_ID_ATTR = "$coverage.object_id"
