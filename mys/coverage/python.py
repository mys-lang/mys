# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Python source expertise for coverage.py"""

import os.path
import types

from . import files
from .misc import CoverageException
from .misc import NoSource
from .phystokens import source_encoding
from .phystokens import source_token_lines
from .plugin import FileReporter


def read_python_source(filename):
    """Read the Python source text from `filename`.

    Returns bytes.

    """
    with open(filename, "rb") as fin:
        source = fin.read()

    return source.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def get_python_source(filename):
    """Return the source code, as unicode."""
    base, ext = os.path.splitext(filename)
    exts = [ext]

    for ext in exts:
        try_filename = base + ext
        if os.path.exists(try_filename):
            # A regular text file: open it.
            source = read_python_source(try_filename)
            break
    else:
        # Couldn't find source.
        exc_msg = "No source for code: '%s'.\n" % (filename,)
        exc_msg += "Aborting report output, consider using -i."
        raise NoSource(exc_msg)

    # Replace \f because of http://bugs.python.org/issue19035
    source = source.replace(b'\f', b' ')
    source = source.decode(source_encoding(source), "replace")

    # Python code should always end with a line with a newline.
    if source and source[-1] != '\n':
        source += '\n'

    return source


def source_for_file(filename):
    """Return the source filename for `filename`.

    Given a file name being traced, return the best guess as to the source
    file to attribute it to.

    """

    return filename


def source_for_morf(morf):
    """Get the source filename for the module-or-file `morf`."""
    if hasattr(morf, '__file__') and morf.__file__:
        filename = morf.__file__
    elif isinstance(morf, types.ModuleType):
        # A module should have had .__file__, otherwise we can't use it.
        # This could be a PEP-420 namespace package.
        raise CoverageException("Module {} has no file".format(morf))
    else:
        filename = morf

    filename = source_for_file(files.unicode_filename(filename))
    return filename


class PythonFileReporter(FileReporter):
    """Report support for a Python file."""

    def __init__(self, morf, coverage=None):
        self.coverage = coverage

        filename = source_for_morf(morf)

        super().__init__(files.canonical_filename(filename))

        if hasattr(morf, '__name__'):
            name = morf.__name__.replace(".", os.sep)
            if os.path.basename(filename).startswith('__init__.'):
                name += os.sep + "__init__"
            name += ".py"
            name = files.unicode_filename(name)
        else:
            name = files.relative_filename(filename)
        self.relname = name

        self._source = None
        self._parser = None
        self._excluded = None

    def relative_filename(self):
        return self.relname

    def source(self):
        if self._source is None:
            self._source = get_python_source(self.filename)
        return self._source

    def source_token_lines(self):
        return source_token_lines(self.source())
