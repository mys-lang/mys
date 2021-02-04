# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Config file for coverage.py"""

import collections
import configparser
import copy
import os
import os.path

from .misc import CoverageException
from .tomlconfig import TomlConfigParser
from .tomlconfig import TomlDecodeError


class HandyConfigParser(configparser.RawConfigParser):
    """Our specialization of ConfigParser."""

    def __init__(self, our_file):
        """Create the HandyConfigParser.

        `our_file` is True if this config file is specifically for coverage,
        False if we are examining another config file (tox.ini, setup.cfg)
        for possible settings.
        """

        configparser.RawConfigParser.__init__(self)
        self.section_prefixes = ["coverage:"]
        if our_file:
            self.section_prefixes.append("")

    def read(self, filenames, encoding=None):
        """Read a file name as UTF-8 configuration data."""
        kwargs = {}
        kwargs['encoding'] = encoding or "utf-8"
        return configparser.RawConfigParser.read(self, filenames, **kwargs)


# The default line exclusion regexes.
DEFAULT_EXCLUDE = [
    r'#\s*(pragma|PRAGMA)[:\s]?\s*(no|NO)\s*(cover|COVER)',
]

# The default partial branch regexes, to be modified by the user.
DEFAULT_PARTIAL = [
    r'#\s*(pragma|PRAGMA)[:\s]?\s*(no|NO)\s*(branch|BRANCH)',
]

# The default partial branch regexes, based on Python semantics.
# These are any Python branching constructs that can't actually execute all
# their branches.
DEFAULT_PARTIAL_ALWAYS = [
    'while (True|1|False|0):',
    'if (True|1|False|0):',
]


class CoverageConfig:
    """Coverage.py configuration.

    The attributes of this class are the various settings that control the
    operation of coverage.py.

    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self):
        """Initialize the configuration attributes to their defaults."""
        # Metadata about the config.
        # We tried to read these config files.
        self.attempted_config_files = []
        # We did read these config files, but maybe didn't find any content for us.
        self.config_files_read = []
        # The file that gave us our configuration.
        self.config_file = None
        self._config_contents = None

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
        self._crash = None

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

    def from_file(self, filename, our_file):
        """Read configuration from a .rc file.

        `filename` is a file name to read.

        `our_file` is True if this config file is specifically for coverage,
        False if we are examining another config file (tox.ini, setup.cfg)
        for possible settings.

        Returns True or False, whether the file could be read, and it had some
        coverage.py settings in it.

        """
        _, ext = os.path.splitext(filename)
        if ext == '.toml':
            cp = TomlConfigParser(our_file)
        else:
            cp = HandyConfigParser(our_file)

        self.attempted_config_files.append(filename)

        try:
            files_read = cp.read(filename)
        except (configparser.Error, TomlDecodeError) as err:
            raise CoverageException(
                "Couldn't read config file %s: %s" % (filename, err))
        if not files_read:
            return False

        self.config_files_read.extend(map(os.path.abspath, files_read))

        any_set = False

        # Check that there are no unrecognized options.
        all_options = collections.defaultdict(set)
        for option_spec in self.CONFIG_FILE_OPTIONS:
            section, option = option_spec[1].split(":")
            all_options[section].add(option)

        for section, options in all_options.items():
            real_section = cp.has_section(section)
            if real_section:
                for unknown in set(cp.options(section)) - options:
                    raise CoverageException(
                        "Unrecognized option '[%s] %s=' in config file %s" % (
                            real_section, unknown, filename
                        )
                    )

        # [paths] is special
        if cp.has_section('paths'):
            for option in cp.options('paths'):
                self.paths[option] = cp.getlist('paths', option)
                any_set = True

        # Was this file used as a config file? If it's specifically our file,
        # then it was used.  If we're piggybacking on someone else's file,
        # then it was only used if we found some settings in it.
        if our_file:
            used = True
        else:
            used = any_set

        if used:
            self.config_file = os.path.abspath(filename)
            with open(filename, "rb") as fin:
                self._config_contents = fin.read()

        return used

    def copy(self):
        """Return a copy of the configuration."""
        return copy.deepcopy(self)

    CONFIG_FILE_OPTIONS = [
        # These are *args for _set_attr_from_config_option:
        #   (attr, where, type_="")
        #
        #   attr is the attribute to set on the CoverageConfig object.
        #   where is the section:name to read from the configuration file.
        #   type_ is the optional type to apply, by using .getTYPE to read the
        #       configuration value from the file.

        # [run]
        ('branch', 'run:branch', 'boolean'),
        ('command_line', 'run:command_line'),
        ('concurrency', 'run:concurrency', 'list'),
        ('context', 'run:context'),
        ('cover_pylib', 'run:cover_pylib', 'boolean'),
        ('data_file', 'run:data_file'),
        ('debug', 'run:debug', 'list'),
        ('disable_warnings', 'run:disable_warnings', 'list'),
        ('dynamic_context', 'run:dynamic_context'),
        ('note', 'run:note'),
        ('parallel', 'run:parallel', 'boolean'),
        ('relative_files', 'run:relative_files', 'boolean'),
        ('run_include', 'run:include', 'list'),
        ('run_omit', 'run:omit', 'list'),
        ('source', 'run:source', 'list'),
        ('source_pkgs', 'run:source_pkgs', 'list'),
        ('timid', 'run:timid', 'boolean'),
        ('_crash', 'run:_crash'),

        # [report]
        ('exclude_list', 'report:exclude_lines', 'regexlist'),
        ('fail_under', 'report:fail_under', 'float'),
        ('ignore_errors', 'report:ignore_errors', 'boolean'),
        ('partial_always_list', 'report:partial_branches_always', 'regexlist'),
        ('partial_list', 'report:partial_branches', 'regexlist'),
        ('precision', 'report:precision', 'int'),
        ('report_contexts', 'report:contexts', 'list'),
        ('report_include', 'report:include', 'list'),
        ('report_omit', 'report:omit', 'list'),
        ('show_missing', 'report:show_missing', 'boolean'),
        ('skip_covered', 'report:skip_covered', 'boolean'),
        ('skip_empty', 'report:skip_empty', 'boolean'),
        ('sort', 'report:sort'),

        # [html]
        ('extra_css', 'html:extra_css'),
        ('html_dir', 'html:directory'),
        ('html_skip_covered', 'html:skip_covered', 'boolean'),
        ('html_skip_empty', 'html:skip_empty', 'boolean'),
        ('html_title', 'html:title'),
        ('show_contexts', 'html:show_contexts', 'boolean'),

        # [xml]
        ('xml_output', 'xml:output'),
        ('xml_package_depth', 'xml:package_depth', 'int'),

        # [json]
        ('json_output', 'json:output'),
        ('json_pretty_print', 'json:pretty_print', 'boolean'),
        ('json_show_contexts', 'json:show_contexts', 'boolean'),
    ]

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


def config_files_to_try(config_file):
    """What config files should we try to read?

    Returns a list of tuples:
        (filename, is_our_file, was_file_specified)
    """

    # Some API users were specifying ".coveragerc" to mean the same as
    # True, so make it so.
    if config_file == ".coveragerc":
        config_file = True
    specified_file = (config_file is not True)
    if not specified_file:
        # No file was specified. Check COVERAGE_RCFILE.
        config_file = os.environ.get('COVERAGE_RCFILE')
        if config_file:
            specified_file = True
    if not specified_file:
        # Still no file specified. Default to .coveragerc
        config_file = ".coveragerc"
    files_to_try = [
        (config_file, True, specified_file),
        ("setup.cfg", False, False),
        ("tox.ini", False, False),
        ("pyproject.toml", False, False),
    ]
    return files_to_try


def read_coverage_config(config_file, **kwargs):
    """Read the coverage.py configuration.

    Arguments:
        config_file: a boolean or string, see the `Coverage` class for the
            tricky details.
        all others: keyword arguments from the `Coverage` class, used for
            setting values in the configuration.

    Returns:
        config:
            config is a CoverageConfig object read from the appropriate
            configuration file.

    """
    # Build the configuration from a number of sources:
    # 1) defaults:
    config = CoverageConfig()

    # 2) from a file:
    if config_file:
        files_to_try = config_files_to_try(config_file)

        for fname, our_file, specified_file in files_to_try:
            config_read = config.from_file(fname, our_file=our_file)
            if config_read:
                break
            if specified_file:
                raise CoverageException("Couldn't read '%s' as a config file" % fname)

    # $set_env.py: COVERAGE_DEBUG - Options for --debug.
    # 3) from environment variables:
    env_data_file = os.environ.get('COVERAGE_FILE')
    if env_data_file:
        config.data_file = env_data_file
    debugs = os.environ.get('COVERAGE_DEBUG')
    if debugs:
        config.debug.extend(d.strip() for d in debugs.split(","))

    # 4) from constructor arguments:
    config.from_args(**kwargs)

    # Once all the config has been collected, there's a little post-processing
    # to do.
    config.post_process()

    return config
