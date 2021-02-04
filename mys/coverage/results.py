# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Results of coverage measurement."""

import collections

from ..parser import ast
from ..transpiler.coverage_transformer import CoverageTransformer
from .debug import SimpleReprMixin
from .misc import CoverageException


def find_statements(filename):
    with open(filename, 'r') as fin:
        tree = ast.parse(fin.read())

    coverage_transformer = CoverageTransformer()
    coverage_transformer.visit(tree)

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

        if self.data.has_arcs():
            self._arc_possibilities = sorted(self.file_reporter.arcs())
            self.exit_counts = self.file_reporter.exit_counts()
            self.no_branch = self.file_reporter.no_branch_lines()
            n_branches = self._total_branches()
            mba = self.missing_branch_arcs()
            n_partial_branches = sum(len(v)
                                     for k,v in mba.items()
                                     if k not in self.missing)
            n_missing_branches = sum(len(v) for k,v in mba.items())
        else:
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

    def has_arcs(self):
        """Were arcs measured in this result?"""
        return self.data.has_arcs()

    def arc_possibilities(self):
        """Returns a sorted list of the arcs in the code."""
        return self._arc_possibilities

    def arcs_executed(self):
        """Returns a sorted list of the arcs actually executed in the code."""
        executed = self.data.arcs(self.filename) or []
        executed = self.file_reporter.translate_arcs(executed)
        return sorted(executed)

    def arcs_missing(self):
        """Returns a sorted list of the arcs in the code not executed."""
        possible = self.arc_possibilities()
        executed = self.arcs_executed()
        missing = (
            p for p in possible
                if p not in executed
                    and p[0] not in self.no_branch
        )
        return sorted(missing)

    def arcs_unpredicted(self):
        """Returns a sorted list of the executed arcs missing from the code."""
        possible = self.arc_possibilities()
        executed = self.arcs_executed()
        # Exclude arcs here which connect a line to itself.  They can occur
        # in executed data in some cases.  This is where they can cause
        # trouble, and here is where it's the least burden to remove them.
        # Also, generators can somehow cause arcs from "enter" to "exit", so
        # make sure we have at least one positive value.
        unpredicted = (
            e for e in executed
                if e not in possible
                    and e[0] != e[1]
                    and (e[0] > 0 or e[1] > 0)
        )
        return sorted(unpredicted)

    def _branch_lines(self):
        """Returns a list of line numbers that have more than one exit."""
        return [l1 for l1,count in self.exit_counts.items() if count > 1]

    def _total_branches(self):
        """How many total branches are there?"""
        return sum(count for count in self.exit_counts.values() if count > 1)

    def missing_branch_arcs(self):
        """Return arcs that weren't executed from branch lines.

        Returns {l1:[l2a,l2b,...], ...}

        """
        missing = self.arcs_missing()
        branch_lines = set(self._branch_lines())
        mba = collections.defaultdict(list)
        for l1, l2 in missing:
            if l1 in branch_lines:
                mba[l1].append(l2)
        return mba

    def branch_stats(self):
        """Get stats about branches.

        Returns a dict mapping line numbers to a tuple:
        (total_exits, taken_exits).
        """

        missing_arcs = self.missing_branch_arcs()
        stats = {}
        for lnum in self._branch_lines():
            exits = self.exit_counts[lnum]
            try:
                missing = len(missing_arcs[lnum])
            except KeyError:
                missing = 0
            stats[lnum] = (exits, exits - missing)
        return stats


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

    @classmethod
    def pc_str_width(cls):
        """How many characters wide can pc_covered_str be?"""
        width = 3   # "100"
        if cls._precision > 0:
            width += 1 + cls._precision
        return width

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


def _line_ranges(statements, lines):
    """Produce a list of ranges for `format_lines`."""
    statements = sorted(statements)
    lines = sorted(lines)

    pairs = []
    start = None
    lidx = 0
    for stmt in statements:
        if lidx >= len(lines):
            break
        if stmt == lines[lidx]:
            lidx += 1
            if not start:
                start = stmt
            end = stmt
        elif start:
            pairs.append((start, end))
            start = None
    if start:
        pairs.append((start, end))
    return pairs


def should_fail_under(total, fail_under, precision):
    """Determine if a total should fail due to fail-under.

    `total` is a float, the coverage measurement total. `fail_under` is the
    fail_under setting to compare with. `precision` is the number of digits
    to consider after the decimal point.

    Returns True if the total should fail.

    """
    # We can never achieve higher than 100% coverage, or less than zero.
    if not (0 <= fail_under <= 100.0):
        msg = "fail_under={} is invalid. Must be between 0 and 100.".format(
            fail_under)
        raise CoverageException(msg)

    # Special case for fail_under=100, it must really be 100.
    if fail_under == 100.0 and total != 100.0:
        return True

    return round(total, precision) < fail_under
