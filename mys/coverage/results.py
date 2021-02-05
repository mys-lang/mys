# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Results of coverage measurement."""

from ..parser import ast
from ..transpiler.coverage_transformer import CoverageTransformer
from .debug import SimpleReprMixin


def find_statements(filename):
    with open(filename, 'r') as fin:
        source = fin.read()

    coverage_transformer = CoverageTransformer(source)
    coverage_transformer.visit(ast.parse(source))

    return {lineno for lineno, _ in coverage_transformer.variables()}


class Analysis:
    """The results of analyzing a FileReporter."""

    def __init__(self, data, file_reporter, file_mapper):
        self.data = data
        self.file_reporter = file_reporter
        self.filename = file_mapper(self.file_reporter.filename)
        self.statements = find_statements(self.filename)
        self.excluded = set()  # self.file_reporter.excluded_lines()

        # Identify missing statements.
        executed = set(self.data.lines(self.filename) or [])
        # executed = self.file_reporter.translate_lines(executed)
        self.executed = executed
        self.missing = self.statements - self.executed
        self._arc_possibilities = []
        self.exit_counts = {}
        self.no_branch = set()
        n_branches = n_partial_branches = n_missing_branches = 0

        self.numbers = Numbers(
            n_files=1,
            n_statements=len(self.statements),
            n_excluded=len(self.excluded),
            n_missing=len(self.missing),
            n_branches=n_branches,
            n_partial_branches=n_partial_branches,
            n_missing_branches=n_missing_branches,
        )


class Numbers(SimpleReprMixin):
    """The numerical results of measuring coverage.

    This holds the basic statistics from `Analysis`, and is used to roll
    up statistics across files.

    """
    # A global to determine the precision on coverage percentages, the number
    # of decimal places.
    _precision = 0
    _near0 = 1.0              # These will change when _precision is changed.
    _near100 = 99.0

    def __init__(self, n_files=0, n_statements=0, n_excluded=0, n_missing=0,
                    n_branches=0, n_partial_branches=0, n_missing_branches=0
                    ):
        self.n_files = n_files
        self.n_statements = n_statements
        self.n_excluded = n_excluded
        self.n_missing = n_missing
        self.n_branches = n_branches
        self.n_partial_branches = n_partial_branches
        self.n_missing_branches = n_missing_branches

    def init_args(self):
        """Return a list for __init__(*args) to recreate this object."""
        return [
            self.n_files, self.n_statements, self.n_excluded, self.n_missing,
            self.n_branches, self.n_partial_branches, self.n_missing_branches,
        ]

    @classmethod
    def set_precision(cls, precision):
        """Set the number of decimal places used to report percentages."""
        assert 0 <= precision < 10
        cls._precision = precision
        cls._near0 = 1.0 / 10**precision
        cls._near100 = 100.0 - cls._near0

    @property
    def n_executed(self):
        """Returns the number of executed statements."""
        return self.n_statements - self.n_missing

    @property
    def n_executed_branches(self):
        """Returns the number of executed branches."""
        return self.n_branches - self.n_missing_branches

    @property
    def pc_covered(self):
        """Returns a single percentage value for coverage."""
        if self.n_statements > 0:
            numerator, denominator = self.ratio_covered
            pc_cov = (100.0 * numerator) / denominator
        else:
            pc_cov = 100.0
        return pc_cov

    @property
    def pc_covered_str(self):
        """Returns the percent covered, as a string, without a percent sign.

        Note that "0" is only returned when the value is truly zero, and "100"
        is only returned when the value is truly 100.  Rounding can never
        result in either "0" or "100".

        """
        pc = self.pc_covered
        if 0 < pc < self._near0:
            pc = self._near0
        elif self._near100 < pc < 100:
            pc = self._near100
        else:
            pc = round(pc, self._precision)
        return "%.*f" % (self._precision, pc)

    @property
    def ratio_covered(self):
        """Return a numerator and denominator for the coverage ratio."""
        numerator = self.n_executed + self.n_executed_branches
        denominator = self.n_statements + self.n_branches
        return numerator, denominator

    def __add__(self, other):
        nums = Numbers()
        nums.n_files = self.n_files + other.n_files
        nums.n_statements = self.n_statements + other.n_statements
        nums.n_excluded = self.n_excluded + other.n_excluded
        nums.n_missing = self.n_missing + other.n_missing
        nums.n_branches = self.n_branches + other.n_branches
        nums.n_partial_branches = (
            self.n_partial_branches + other.n_partial_branches
            )
        nums.n_missing_branches = (
            self.n_missing_branches + other.n_missing_branches
            )
        return nums

    def __radd__(self, other):
        # Implementing 0+Numbers allows us to sum() a list of Numbers.
        if other == 0:
            return self
        return NotImplemented
