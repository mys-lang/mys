# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Config file for coverage.py"""

import collections
import copy
import os

# The default line exclusion regexes.
DEFAULT_EXCLUDE = [
    r'#\s*(pragma|PRAGMA)[:\s]?\s*(no|NO)\s*(cover|COVER)'
]

# The default partial branch regexes, to be modified by the user.
DEFAULT_PARTIAL = [
    r'#\s*(pragma|PRAGMA)[:\s]?\s*(no|NO)\s*(branch|BRANCH)'
]

# The default partial branch regexes, based on Python semantics.
# These are any Python branching constructs that can't actually execute all
# their branches.
DEFAULT_PARTIAL_ALWAYS = [
    'while (True|1|False|0):',
    'if (True|1|False|0):'
]


class CoverageConfig:
    """Coverage.py configuration.

    The attributes of this class are the various settings that control the
    operation of coverage.py.

    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        """Initialize the configuration attributes to their defaults."""
        # Defaults for [run] and [report]
        self._include = None
        self._omit = None

        # Defaults for [run]
        self.branch = False
        self.command_line = None
        self.concurrency = None
        self.context = None
        self.cover_pylib = False
        self.data_file = ".coverage"
        self.debug = []
        self.disable_warnings = []
        self.dynamic_context = None
        self.note = None
        self.parallel = False
        self.relative_files = False
        self.run_include = None
        self.run_omit = None
        self.source = None
        self.source_pkgs = []
        self.timid = False

        # Defaults for [report]
        self.exclude_list = DEFAULT_EXCLUDE[:]
        self.fail_under = 0.0
        self.ignore_errors = False
        self.report_include = None
        self.report_omit = None
        self.partial_always_list = DEFAULT_PARTIAL_ALWAYS[:]
        self.partial_list = DEFAULT_PARTIAL[:]
        self.precision = 0
        self.report_contexts = None
        self.show_missing = False
        self.skip_covered = False
        self.skip_empty = False
        self.sort = None

        # Defaults for [html]
        self.extra_css = None
        self.html_dir = "htmlcov"
        self.html_skip_covered = None
        self.html_skip_empty = None
        self.html_title = "Coverage report"
        self.show_contexts = False

        # Defaults for [xml]
        self.xml_output = "coverage.xml"
        self.xml_package_depth = 99

        # Defaults for [json]
        self.json_output = "coverage.json"
        self.json_pretty_print = False
        self.json_show_contexts = False

        # Defaults for [paths]
        self.paths = collections.OrderedDict()

    MUST_BE_LIST = [
        "debug", "concurrency",
        "report_omit", "report_include",
        "run_omit", "run_include",
    ]

    def from_args(self, **kwargs):
        """Read config values from `kwargs`."""
        for k, v in kwargs.items():
            if v is not None:
                if k in self.MUST_BE_LIST and isinstance(v, str):
                    v = [v]
                setattr(self, k, v)

    def copy(self):
        """Return a copy of the configuration."""
        return copy.deepcopy(self)

    def post_process_file(self, path):
        """Make final adjustments to a file path to make it usable."""
        return os.path.expanduser(path)

    def post_process(self):
        """Make final adjustments to settings to make them usable."""
        self.data_file = self.post_process_file(self.data_file)
        self.html_dir = self.post_process_file(self.html_dir)
        self.xml_output = self.post_process_file(self.xml_output)
        self.paths = collections.OrderedDict(
            (k, [self.post_process_file(f) for f in v])
            for k, v in self.paths.items()
        )


def read_coverage_config(config_file, **kwargs):
    """Read the coverage.py configuration.

    Arguments:
        all others: keyword arguments from the `Coverage` class, used for
            setting values in the configuration.

    Returns:
        config:
            config is a CoverageConfig object read from the appropriate
            configuration file.

    """

    del config_file
    config = CoverageConfig()
    config.from_args(**kwargs)
    config.post_process()

    return config
