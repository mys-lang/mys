# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Mys source expertise for coverage.py"""

from . import files
from .phystokens import source_encoding
from .phystokens import source_token_lines
from .plugin import FileReporter


def get_mys_source(filename):
    """Return the source code, as unicode."""

    with open(filename, "rb") as fin:
        source = fin.read()

    source = source.replace(b"\r\n", b"\n")
    source = source.replace(b"\r", b"\n")

    # Replace \f because of http://bugs.python.org/issue19035
    source = source.replace(b'\f', b' ')
    source = source.decode(source_encoding(source), "replace")

    # Mys code should always end with a line with a newline.
    if source and source[-1] != '\n':
        source += '\n'

    return source


class MysFileReporter(FileReporter):
    """Report support for a Mys file."""

    def __init__(self, filename, coverage=None):
        self.coverage = coverage
        super().__init__(files.canonical_filename(filename))
        self.relname = files.relative_filename(filename)
        self._source = None
        self._parser = None
        self._excluded = None

    def relative_filename(self):
        return self.relname

    def source(self):
        if self._source is None:
            self._source = get_mys_source(self.filename)

        return self._source

    def source_token_lines(self):
        return source_token_lines(self.source())
