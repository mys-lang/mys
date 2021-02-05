# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Reporter foundation for coverage.py."""

from .files import FnmatchMatcher
from .files import prep_patterns
from .misc import CoverageException


def get_analysis_to_report(coverage, morfs):
    """Get the files to report on.

    For each morf in `morfs`, if it should be reported on (based on the omit
    and include configuration options), yield a pair, the `FileReporter` and
    `Analysis` for the morf.

    """
    file_reporters = coverage._get_file_reporters(morfs)
    config = coverage.config

    if config.report_include:
        matcher = FnmatchMatcher(prep_patterns(config.report_include))
        file_reporters = [fr for fr in file_reporters if matcher.match(fr.filename)]

    if config.report_omit:
        matcher = FnmatchMatcher(prep_patterns(config.report_omit))
        file_reporters = [fr
                          for fr in file_reporters
                          if not matcher.match(fr.filename)]

    if not file_reporters:
        raise CoverageException("No data to report.")

    for fr in sorted(file_reporters):
        analysis = coverage._analyze(fr)
        yield (fr, analysis)
