# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""The version and URL for coverage.py"""
# This file is exec'ed in setup.py, don't import anything!

# Same semantics as sys.version_info.
version_info = (5, 5, 0, "alpha", 0)


def _make_version(major, minor, micro, releaselevel, serial):
    """Create a readable version string from version_info tuple components."""
    assert releaselevel in ['alpha', 'beta', 'candidate', 'final']
    version = "%d.%d" % (major, minor)
    if micro:
        version += ".%d" % (micro,)
    if releaselevel != 'final':
        short = {'alpha': 'a', 'beta': 'b', 'candidate': 'rc'}[releaselevel]
        version += "%s%d" % (short, serial)
    return version


__version__ = _make_version(*version_info)
__url__ = "https://github.com/nedbat/coveragepy"
