# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Coverage data for coverage.py.

This file had the 4.x JSON data support, which is now gone.  This file still
has storage-agnostic helpers, and is kept to avoid changing too many imports.
CoverageData is now defined in sqldata.py, and imported here to keep the
imports working.

"""


def add_data_to_hash(data, filename, hasher):
    """Contribute `filename`'s data to the `hasher`.

    `hasher` is a `coverage.misc.Hasher` instance to be updated with
    the file's data.  It should only get the results data, not the run
    data.

    """
    hasher.update(sorted(data.lines(filename) or []))
    hasher.update(data.file_tracer(filename))
