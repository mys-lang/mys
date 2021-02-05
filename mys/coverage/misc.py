# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Miscellaneous stuff for coverage.py."""

import errno
import hashlib
import inspect
import os
import os.path
import random
import socket


def join_regex(regexes):
    """Combine a list of regexes into one that matches any of them."""
    return "|".join("(?:%s)" % r for r in regexes)


def file_be_gone(path):
    """Remove a file, and don't get annoyed if it doesn't exist."""
    try:
        os.remove(path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


def ensure_dir(directory):
    """Make sure the directory exists.

    If `directory` is None or empty, do nothing.
    """
    if directory and not os.path.isdir(directory):
        os.makedirs(directory)


def ensure_dir_for_file(path):
    """Make sure the directory for the path exists."""
    ensure_dir(os.path.dirname(path))


def filename_suffix(suffix):
    """Compute a filename suffix for a data file.

    If `suffix` is a string or None, simply return it. If `suffix` is True,
    then build a suffix incorporating the hostname, process id, and a random
    number.

    Returns a string or None.

    """
    if suffix is True:
        # If data_suffix was a simple true value, then make a suffix with
        # plenty of distinguishing information.  We do this here in
        # `save()` at the last minute so that the pid will be correct even
        # if the process forks.
        dice = random.Random(os.urandom(8)).randint(0, 999999)
        suffix = "%s.%s.%06d" % (socket.gethostname(), os.getpid(), dice)
    return suffix


class Hasher:
    """Hashes Python data into md5."""
    def __init__(self):
        self.md5 = hashlib.md5()

    def update(self, v):
        """Add `v` to the hash, recursively if needed."""
        self.md5.update(str(type(v)).encode('utf-8'))
        if isinstance(v, str):
            self.md5.update(v.encode('utf8'))
        elif isinstance(v, bytes):
            self.md5.update(v)
        elif v is None:
            pass
        elif isinstance(v, (int, float)):
            self.md5.update(str(v).encode('utf-8'))
        elif isinstance(v, (tuple, list)):
            for e in v:
                self.update(e)
        elif isinstance(v, dict):
            keys = v.keys()
            for k in sorted(keys):
                self.update(k)
                self.update(v[k])
        else:
            for k in dir(v):
                if k.startswith('__'):
                    continue
                aa = getattr(v, k)
                if inspect.isroutine(aa):
                    continue
                self.update(k)
                self.update(aa)
        self.md5.update(b'.')

    def hexdigest(self):
        """Retrieve the hex digest of the hash."""
        return self.md5.hexdigest()


class DefaultValue:
    """A sentinel object to use for unusual default-value needs.

    Construct with a string that will be used as the repr, for display in help
    and Sphinx output.

    """
    def __init__(self, display_as):
        self.display_as = display_as

    def __repr__(self):
        return self.display_as


class BaseCoverageException(Exception):
    """The base of all Coverage exceptions."""


class CoverageException(BaseCoverageException):
    """An exception raised by a coverage.py function."""


class NoSource(CoverageException):
    """We couldn't find the source for a module."""
