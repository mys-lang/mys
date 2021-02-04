# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""File wrangling."""

import fnmatch
import hashlib
import ntpath
import os
import os.path
import posixpath
import re
import sys

from .misc import CoverageException
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


def isabs_anywhere(filename):
    """Is `filename` an absolute path on any OS?"""
    return ntpath.isabs(filename) or posixpath.isabs(filename)


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


def sep(ss):
    """Find the path separator used in this string, or os.sep if none."""
    sep_match = re.search(r"[\\/]", ss)
    if sep_match:
        the_sep = sep_match.group(0)
    else:
        the_sep = os.sep
    return the_sep


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


class PathAliases:
    """A collection of aliases for paths.

    When combining data files from remote machines, often the paths to source
    code are different, for example, due to OS differences, or because of
    serialized checkouts on continuous integration machines.

    A `PathAliases` object tracks a list of pattern/result pairs, and can
    map a path through those aliases to produce a unified path.

    """
    def __init__(self):
        self.aliases = []

    def pprint(self):       # pragma: debugging
        """Dump the important parts of the PathAliases, for debugging."""
        for regex, result in self.aliases:
            print("{!r} --> {!r}".format(regex.pattern, result))

    def add(self, pattern, result):
        """Add the `pattern`/`result` pair to the list of aliases.

        `pattern` is an `fnmatch`-style pattern.  `result` is a simple
        string.  When mapping paths, if a path starts with a match against
        `pattern`, then that match is replaced with `result`.  This models
        isomorphic source trees being rooted at different places on two
        different machines.

        `pattern` can't end with a wildcard component, since that would
        match an entire tree, and not just its root.

        """
        pattern_sep = sep(pattern)

        if len(pattern) > 1:
            pattern = pattern.rstrip(r"\/")

        # The pattern can't end with a wildcard component.
        if pattern.endswith("*"):
            raise CoverageException("Pattern must not end with wildcards.")

        # The pattern is meant to match a filepath.  Let's make it absolute
        # unless it already is, or is meant to match any prefix.
        if not pattern.startswith('*') and not isabs_anywhere(pattern +
                                                              pattern_sep):
            pattern = abs_file(pattern)
        if not pattern.endswith(pattern_sep):
            pattern += pattern_sep

        # Make a regex from the pattern.
        regex = fnmatches_to_regex([pattern], case_insensitive=True, partial=True)

        # Normalize the result: it must end with a path separator.
        result_sep = sep(result)
        result = result.rstrip(r"\/") + result_sep
        self.aliases.append((regex, result))

    def map(self, path):
        """Map `path` through the aliases.

        `path` is checked against all of the patterns.  The first pattern to
        match is used to replace the root of the path with the result root.
        Only one pattern is ever used.  If no patterns match, `path` is
        returned unchanged.

        The separator style in the result is made to match that of the result
        in the alias.

        Returns the mapped path.  If a mapping has happened, this is a
        canonical path.  If no mapping has happened, it is the original value
        of `path` unchanged.

        """
        for regex, result in self.aliases:
            mo = regex.match(path)
            if mo:
                new = path.replace(mo.group(0), result)
                new = new.replace(sep(path), sep(result))
                new = canonical_filename(new)
                return new
        return path


def find_python_files(dirname):
    """Yield all of the importable Python files in `dirname`, recursively.

    To be importable, the files have to be in a directory with a __init__.py,
    except for `dirname` itself, which isn't required to have one.  The
    assumption is that `dirname` was specified directly, so the user knows
    best, but sub-directories are checked for a __init__.py to be sure we only
    find the importable files.

    """
    for i, (dirpath, dirnames, filenames) in enumerate(os.walk(dirname)):
        if i > 0 and '__init__.py' not in filenames:
            # If a directory doesn't have __init__.py, then it isn't
            # importable and neither are its files
            del dirnames[:]
            continue
        for filename in filenames:
            # We're only interested in files that look like reasonable Python
            # files: Must end with .py or .pyw, and must not have certain funny
            # characters that probably mean they are editor junk.
            if re.match(r"^[^.#~!$@%^&*()+=,]+\.pyw?$", filename):
                yield os.path.join(dirpath, filename)
