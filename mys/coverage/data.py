# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt


def add_data_to_hash(data, filename, hasher):
    """Contribute `filename`'s data to the `hasher`.

    `hasher` is a `coverage.misc.Hasher` instance to be updated with
    the file's data.  It should only get the results data, not the run
    data.

    """
    hasher.update(sorted(data.lines(filename) or []))
    hasher.update(data.file_tracer(filename))
