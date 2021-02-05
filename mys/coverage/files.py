# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""File wrangling."""

import fnmatch
import hashlib
import ntpath
import os
import os.path
import re
import sys

from .misc import join_regex


def set_relative_directory():
    """Set the directory that `relative_filename` will be relative to."""
    global RELATIVE_DIR, CANONICAL_FILENAME_CACHE

    # The absolute path to our current directory.
    RELATIVE_DIR = os.path.normcase(abs_file(os.curdir) + os.sep)

    # Cache of results of calling the canonical_filename() method, to
    # avoid duplicating work.
    CANONICAL_FILENAME_CACHE = {}


def relative_filename(filename):
    """Return the relative form of `filename`.

    The file name will be relative to the current directory when the
    `set_relative_directory` was called.

    """
    fnorm = os.path.normcase(filename)
    if fnorm.startswith(RELATIVE_DIR):
        filename = filename[len(RELATIVE_DIR):]
    return unicode_filename(filename)


def canonical_filename(filename):
    """Return a canonical file name for `filename`.

    An absolute path with no redundant components and normalized case.

    """
    if filename not in CANONICAL_FILENAME_CACHE:
        cf = filename
        if not os.path.isabs(filename):
            for path in [os.curdir] + sys.path:
                if path is None:
                    continue
                ff = os.path.join(path, filename)
                try:
                    exists = os.path.exists(ff)
                except UnicodeError:
                    exists = False
                if exists:
                    cf = ff
                    break
        cf = abs_file(cf)
        CANONICAL_FILENAME_CACHE[filename] = cf
    return CANONICAL_FILENAME_CACHE[filename]


MAX_FLAT = 200

def flat_rootname(filename):
    """A base for a flat file name to correspond to this file.

    Useful for writing files about the code where you want all the files in
    the same directory, but need to differentiate same-named files from
    different directories.

    For example, the file a/b/c.py will return 'a_b_c_py'

    """
    name = ntpath.splitdrive(filename)[1]
    name = re.sub(r"[\\/.:]", "_", name)
    if len(name) > MAX_FLAT:
        hh = hashlib.sha1(name.encode('UTF-8')).hexdigest()
        name = name[-(MAX_FLAT-len(hh)-1):] + '_' + hh
    return name


def actual_path(filename):
    """The actual path for non-Windows platforms."""
    return filename


def unicode_filename(filename):
    """Return a Unicode version of `filename`."""
    return filename


def abs_file(path):
    """Return the absolute normalized form of `path`."""
    try:
        path = os.path.realpath(path)
    except UnicodeError:
        pass
    path = os.path.abspath(path)
    path = actual_path(path)
    path = unicode_filename(path)
    return path


RELATIVE_DIR = None
CANONICAL_FILENAME_CACHE = None
set_relative_directory()


def prep_patterns(patterns):
    """Prepare the file patterns for use in a `FnmatchMatcher`.

    If a pattern starts with a wildcard, it is used as a pattern
    as-is.  If it does not start with a wildcard, then it is made
    absolute with the current directory.

    If `patterns` is None, an empty list is returned.

    """
    prepped = []
    for pa in patterns or []:
        if pa.startswith(("*", "?")):
            prepped.append(pa)
        else:
            prepped.append(abs_file(pa))
    return prepped


class FnmatchMatcher:
    """A matcher for files by file name pattern."""
    def __init__(self, pats):
        self.pats = list(pats)
        self.re = fnmatches_to_regex(self.pats, case_insensitive=False)

    def __repr__(self):
        return "<FnmatchMatcher %r>" % self.pats

    def info(self):
        """A list of strings for displaying when dumping state."""
        return self.pats

    def match(self, fpath):
        """Does `fpath` match one of our file name patterns?"""
        return self.re.match(fpath) is not None


def fnmatches_to_regex(patterns, case_insensitive=False, partial=False):
    """Convert fnmatch patterns to a compiled regex that matches any of them.

    Slashes are always converted to match either slash or backslash, for
    Windows support, even when running elsewhere.

    If `partial` is true, then the pattern will match if the target string
    starts with the pattern. Otherwise, it must match the entire string.

    Returns: a compiled regex object.  Use the .match method to compare target
    strings.

    """
    regexes = (fnmatch.translate(pattern) for pattern in patterns)
    # Python3.7 fnmatch translates "/" as "/". Before that, it translates as "\/",
    # so we have to deal with maybe a backslash.
    regexes = (re.sub(r"\\?/", r"[\\\\/]", regex) for regex in regexes)

    if partial:
        # fnmatch always adds a \Z to match the whole string, which we don't
        # want, so we remove the \Z.  While removing it, we only replace \Z if
        # followed by paren (introducing flags), or at end, to keep from
        # destroying a literal \Z in the pattern.
        regexes = (re.sub(r'\\Z(\(\?|$)', r'\1', regex) for regex in regexes)

    flags = 0
    if case_insensitive:
        flags |= re.IGNORECASE
    compiled = re.compile(join_regex(regexes), flags=flags)

    return compiled
