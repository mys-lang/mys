# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/nedbat/coveragepy/blob/master/NOTICE.txt

"""Core control stuff for coverage.py."""

import collections
import contextlib
import os
import os.path
import platform
import sys

from .config import read_coverage_config
from .debug import DebugControl
from .files import abs_file
from .files import relative_filename
from .files import set_relative_directory
from .html import HtmlReporter
from .misc import DefaultValue
from .misc import bool_or_none
from .misc import ensure_dir_for_file
from .misc import isolate_module
from .misc import join_regex
from .plugin import FileReporter
from .python import PythonFileReporter
from .results import Analysis
from .results import Numbers
from .sqldata import CoverageData

os = isolate_module(os)

@contextlib.contextmanager
def override_config(cov, **kwargs):
    """Temporarily tweak the configuration of `cov`.

    The arguments are applied to `cov.config` with the `from_args` method.
    At the end of the with-statement, the old configuration is restored.
    """
    original_config = cov.config
    cov.config = cov.config.copy()
    try:
        cov.config.from_args(**kwargs)
        yield
    finally:
        cov.config = original_config


_DEFAULT_DATAFILE = DefaultValue("MISSING")

class Coverage:
    """Programmatic access to coverage.py.

    To use::

        from coverage import Coverage

        cov = Coverage()
        cov.start()
        #.. call your code ..
        cov.stop()
        cov.html_report(directory='covhtml')

    Note: in keeping with Python custom, names starting with underscore are
    not part of the public API. They might stop working at any point.  Please
    limit yourself to documented methods to avoid problems.

    """

    # The stack of started Coverage instances.
    _instances = []

    @classmethod
    def current(cls):
        """Get the latest started `Coverage` instance, if any.

        Returns: a `Coverage` instance, or None.

        .. versionadded:: 5.0

        """
        if cls._instances:
            return cls._instances[-1]
        else:
            return None

    def __init__(
        self, data_file=_DEFAULT_DATAFILE, data_suffix=None, cover_pylib=None,
        auto_data=False, timid=None, branch=None, config_file=True,
        source=None, source_pkgs=None, omit=None, include=None, debug=None,
        check_preimported=False, context=None,
    ):  # pylint: disable=too-many-arguments
        """
        Many of these arguments duplicate and override values that can be
        provided in a configuration file.  Parameters that are missing here
        will use values from the config file.

        `data_file` is the base name of the data file to use. The config value
        defaults to ".coverage".  None can be provided to prevent writing a data
        file.  `data_suffix` is appended (with a dot) to `data_file` to create
        the final file name.  If `data_suffix` is simply True, then a suffix is
        created with the machine and process identity included.

        `cover_pylib` is a boolean determining whether Python code installed
        with the Python interpreter is measured.  This includes the Python
        standard library and any packages installed with the interpreter.

        If `auto_data` is true, then any existing data file will be read when
        coverage measurement starts, and data will be saved automatically when
        measurement stops.

        If `timid` is true, then a slower and simpler trace function will be
        used.  This is important for some environments where manipulation of
        tracing functions breaks the faster trace function.

        If `branch` is true, then branch coverage will be measured in addition
        to the usual statement coverage.

        `config_file` determines what configuration file to read:

            * If it is ".coveragerc", it is interpreted as if it were True,
              for backward compatibility.

            * If it is a string, it is the name of the file to read.  If the
              file can't be read, it is an error.

            * If it is True, then a few standard files names are tried
              (".coveragerc", "setup.cfg", "tox.ini").  It is not an error for
              these files to not be found.

            * If it is False, then no configuration file is read.

        `source` is a list of file paths or package names.  Only code located
        in the trees indicated by the file paths or package names will be
        measured.

        `source_pkgs` is a list of package names. It works the same as
        `source`, but can be used to name packages where the name can also be
        interpreted as a file path.

        `include` and `omit` are lists of file name patterns. Files that match
        `include` will be measured, files that match `omit` will not.  Each
        will also accept a single string argument.

        `debug` is a list of strings indicating what debugging information is
        desired.

        If `check_preimported` is true, then when coverage is started, the
        already-imported files will be checked to see if they should be
        measured by coverage.  Importing measured files before coverage is
        started can mean that code is missed.

        `context` is a string to use as the :ref:`static context
        <static_contexts>` label for collected data.

        .. versionadded:: 4.0
            The `concurrency` parameter.

        .. versionadded:: 4.2
            The `concurrency` parameter can now be a list of strings.

        .. versionadded:: 5.0
            The `check_preimported` and `context` parameters.

        .. versionadded:: 5.3
            The `source_pkgs` parameter.

        """
        # data_file=None means no disk file at all. data_file missing means
        # use the value from the config file.
        self._no_disk = data_file is None
        if data_file is _DEFAULT_DATAFILE:
            data_file = None

        # Build our configuration from a number of sources.
        self.config = read_coverage_config(
            config_file=config_file,
            data_file=data_file,
            cover_pylib=cover_pylib,
            timid=timid,
            branch=branch,
            parallel=bool_or_none(data_suffix),
            source=source,
            source_pkgs=source_pkgs,
            run_omit=omit,
            run_include=include,
            debug=debug,
            report_omit=omit,
            report_include=include,
            concurrency=None,
            context=context,
            )

        # This is injectable by tests.
        self._debug_file = None

        self._auto_load = self._auto_save = auto_data
        self._data_suffix_specified = data_suffix

        # Is it ok for no data to be collected?
        self._warn_no_data = True
        self._warn_unimported_source = True
        self._warn_preimported_source = check_preimported
        self._no_warn_slugs = None

        # A record of all the warnings that have been issued.
        self._warnings = []

        # Other instance attributes, set later.
        self._data = self._collector = None
        self._inorout = None
        self._data_suffix = self._run_suffix = None
        self._exclude_re = None
        self._debug = None
        self._file_mapper = None

        # State machine variables:
        # Have we initialized everything?
        self._inited = False
        self._inited_for_start = False
        # Have we started collecting and not stopped it?
        self._started = False
        # Should we write the debug output?
        self._should_write_debug = True

    def _init(self):
        """Set all the initial state.

        This is called by the public methods to initialize state. This lets us
        construct a :class:`Coverage` object, then tweak its state before this
        function is called.

        """
        if self._inited:
            return

        self._inited = True

        # Create and configure the debugging controller. COVERAGE_DEBUG_FILE
        # is an environment variable, the name of a file to append debug logs
        # to.
        self._debug = DebugControl(self.config.debug, self._debug_file)

        # Multi-processing uses parallel for the subprocesses, so also use
        # it for the main process.
        self.config.parallel = False

        # _exclude_re is a dict that maps exclusion list names to compiled regexes.
        self._exclude_re = {}

        set_relative_directory()
        self._file_mapper = (relative_filename
                             if self.config.relative_files
                             else abs_file)

    def _post_init(self):
        """Stuff to do after everything is initialized."""
        if self._should_write_debug:
            self._should_write_debug = False
            self._write_startup_debug()

    def _write_startup_debug(self):
        """Write out debug info at startup if needed."""
        with self._debug.without_callers():
            if self._debug.should('config'):
                config_info = sorted(self.config.__dict__.items())
                config_info = [
                    (k, v) for k, v in config_info if not k.startswith('_')
                ]

    def _warn(self, msg, slug=None, once=False):
        """Use `msg` as a warning.

        For warning suppression, use `slug` as the shorthand.

        If `once` is true, only show this warning once (determined by the
        slug.)

        """
        if self._no_warn_slugs is None:
            self._no_warn_slugs = list(self.config.disable_warnings)

        if slug in self._no_warn_slugs:
            # Don't issue the warning
            return

        self._warnings.append(msg)
        if slug:
            msg = "%s (%s)" % (msg, slug)
        if self._debug.should('pid'):
            msg = "[%d] %s" % (os.getpid(), msg)
        sys.stderr.write("Coverage.py warning: %s\n" % msg)

        if once:
            self._no_warn_slugs.append(slug)

    def load(self):
        """Load previously-collected coverage data from the data file."""
        self._init()
        if self._collector:
            self._collector.reset()
        should_skip = (self.config.parallel
                       and not os.path.exists(self.config.data_file))
        if not should_skip:
            self._init_data(suffix=None)
        self._post_init()
        if not should_skip:
            self._data.read()

    def _init_data(self, suffix):
        """Create a data file if we don't have one yet."""
        if self._data is None:
            # Create the data file.  We do this at construction time so that the
            # data file will be written into the directory where the process
            # started rather than wherever the process eventually chdir'd to.
            ensure_dir_for_file(self.config.data_file)
            self._data = CoverageData(
                basename=self.config.data_file,
                suffix=suffix,
                warn=self._warn,
                debug=self._debug,
                no_disk=self._no_disk,
            )

    def start(self):
        """Start measuring code coverage.

        Coverage measurement only occurs in functions called after
        :meth:`start` is invoked.  Statements in the same scope as
        :meth:`start` won't be measured.

        Once you invoke :meth:`start`, you must also call :meth:`stop`
        eventually, or your process might not shut down cleanly.

        """

        if self._auto_load:
            self.load()

        self._started = True

    def stop(self):
        """Stop measuring code coverage."""
        self._started = False

    def _atexit(self):
        """Clean up on process shutdown."""
        if self._debug.should("process"):
            self._debug.write("atexit: pid: {}, instance: {!r}".format(os.getpid(),
                                                                       self))
        if self._started:
            self.stop()
        if self._auto_save:
            self.save()

    def erase(self):
        """Erase previously collected coverage data.

        This removes the in-memory data collected in this session as well as
        discarding the data file.

        """
        self._init()
        self._post_init()
        if self._collector:
            self._collector.reset()
        self._init_data(suffix=None)
        self._data.erase(parallel=self.config.parallel)
        self._data = None
        self._inited_for_start = False

    def clear_exclude(self, which='exclude'):
        """Clear the exclude list."""
        self._init()
        setattr(self.config, which + "_list", [])
        self._exclude_regex_stale()

    def exclude(self, regex, which='exclude'):
        """Exclude source lines from execution consideration.

        A number of lists of regular expressions are maintained.  Each list
        selects lines that are treated differently during reporting.

        `which` determines which list is modified.  The "exclude" list selects
        lines that are not considered executable at all.  The "partial" list
        indicates lines with branches that are not taken.

        `regex` is a regular expression.  The regex is added to the specified
        list.  If any of the regexes in the list is found in a line, the line
        is marked for special treatment during reporting.

        """
        self._init()
        excl_list = getattr(self.config, which + "_list")
        excl_list.append(regex)
        self._exclude_regex_stale()

    def _exclude_regex_stale(self):
        """Drop all the compiled exclusion regexes, a list was modified."""
        self._exclude_re.clear()

    def _exclude_regex(self, which):
        """Return a compiled regex for the given exclusion list."""
        if which not in self._exclude_re:
            excl_list = getattr(self.config, which + "_list")
            self._exclude_re[which] = join_regex(excl_list)
        return self._exclude_re[which]

    def get_exclude_list(self, which='exclude'):
        """Return a list of excluded regex patterns.

        `which` indicates which list is desired.  See :meth:`exclude` for the
        lists that are available, and their meaning.

        """
        self._init()
        return getattr(self.config, which + "_list")

    def save(self):
        """Save the collected coverage data to the data file."""
        data = self.get_data()
        data.write()

    def get_data(self):
        """Get the collected data.

        Also warn about various problems collecting data.

        Returns a :class:`coverage.CoverageData`, the collected coverage data.

        .. versionadded:: 4.0

        """
        self._init()
        self._init_data(suffix=None)
        self._post_init()

        if self._collector and self._collector.flush_data():
            self._post_save_work()

        return self._data

    def _post_save_work(self):
        """After saving data, look for warnings, post-work, etc.

        Warn about things that should have happened but didn't.
        Look for unexecuted files.

        """
        # If there are still entries in the source_pkgs_unmatched list,
        # then we never encountered those packages.
        if self._warn_unimported_source:
            self._inorout.warn_unimported_source()

        # Find out if we got any data.
        if not self._data and self._warn_no_data:
            self._warn("No data was collected.", slug="no-data-collected")

        # Touch all the files that could have executed, so that we can
        # mark completely unexecuted files as 0% covered.
        if self._data is not None:
            file_paths = collections.defaultdict(list)
            unexecuted_files = self._inorout.find_possibly_unexecuted_files()
            for file_path, plugin_name in unexecuted_files:
                file_path = self._file_mapper(file_path)
                file_paths[plugin_name].append(file_path)
            for plugin_name, paths in file_paths.items():
                self._data.touch_files(paths, plugin_name)

        if self.config.note:
            self._warn("The '[run] note' setting is no longer supported.")

    def _get_file_reporter(self, morf):
        """Get a FileReporter for a module or file name."""
        file_reporter = "python"

        if file_reporter == "python":
            file_reporter = PythonFileReporter(morf, self)

        return file_reporter

    def _analyze(self, it):
        """Analyze a single morf or code unit.

        Returns an `Analysis` object.

        """
        # All reporting comes through here, so do reporting initialization.
        self._init()
        Numbers.set_precision(self.config.precision)
        self._post_init()

        data = self.get_data()
        if not isinstance(it, FileReporter):
            it = self._get_file_reporter(it)

        return Analysis(data, it, self._file_mapper)


    def _get_file_reporters(self, morfs=None):
        """Get a list of FileReporters for a list of modules or file names.

        For each module or file name in `morfs`, find a FileReporter.  Return
        the list of FileReporters.

        If `morfs` is a single module or file name, this returns a list of one
        FileReporter.  If `morfs` is empty or None, then the list of all files
        measured is used to find the FileReporters.

        """
        if not morfs:
            morfs = self._data.measured_files()

        # Be sure we have a collection.
        if not isinstance(morfs, (list, tuple, set)):
            morfs = [morfs]

        file_reporters = [self._get_file_reporter(morf) for morf in morfs]
        return file_reporters

    def html_report(
        self, morfs=None, directory=None, ignore_errors=None,
        omit=None, include=None, extra_css=None, title=None,
        skip_covered=None, show_contexts=None, contexts=None,
        skip_empty=None, precision=None,
    ):
        """Generate an HTML report.

        The HTML is written to `directory`.  The file "index.html" is the
        overview starting point, with links to more detailed pages for
        individual modules.

        `extra_css` is a path to a file of other CSS to apply on the page.
        It will be copied into the HTML directory.

        `title` is a text string (not HTML) to use as the title of the HTML
        report.

        See :meth:`report` for other arguments.

        Returns a float, the total percentage covered.

        .. note::
            The HTML report files are generated incrementally based on the
            source files and coverage results. If you modify the report files,
            the changes will not be considered.  You should be careful about
            changing the files in the report folder.

        """
        with override_config(self,
                             ignore_errors=ignore_errors,
                             report_omit=omit,
                             report_include=include,
                             html_dir=directory,
                             extra_css=extra_css,
                             html_title=title,
                             html_skip_covered=skip_covered,
                             show_contexts=show_contexts,
                             report_contexts=contexts,
                             html_skip_empty=skip_empty,
                             precision=precision,
        ):
            reporter = HtmlReporter(self)
            return reporter.report(morfs)

    def sys_info(self):
        """Return a list of (key, value) pairs showing internal information."""

        from . import __file__
        from . import __version__

        self._init()
        self._post_init()

        info = [
            ('version', __version__),
            ('coverage', __file__),
            ('tracer', "-none-"),
            ('CTracer', "unavailable"),
            ('configs_attempted', self.config.attempted_config_files),
            ('configs_read', self.config.config_files_read),
            ('config_file', self.config.config_file),
            ('config_contents',
                repr(self.config._config_contents)
                if self.config._config_contents
                else '-none-'
            ),
            ('data_file', (self._data.data_filename()
                           if self._data is not None
                           else "-none-")),
            ('python', sys.version.replace('\n', '')),
            ('platform', platform.platform()),
            ('implementation', platform.python_implementation()),
            ('executable', sys.executable),
            ('def_encoding', sys.getdefaultencoding()),
            ('fs_encoding', sys.getfilesystemencoding()),
            ('pid', os.getpid()),
            ('cwd', os.getcwd()),
            ('path', sys.path),
            ('environment', sorted(
                ("%s = %s" % (k, v))
                for k, v in os.environ.items()
                if any(slug in k for slug in ("COV", "PY"))
            )),
            ('command_line', " ".join(getattr(sys, 'argv', ['-none-']))),
            ]

        if self._inorout:
            info.extend(self._inorout.sys_info())

        info.extend(CoverageData.sys_info())

        return info


# Mega debugging...
# $set_env.py: COVERAGE_DEBUG_CALLS - Lots and lots of output about calls to Coverage.
if int(os.environ.get("COVERAGE_DEBUG_CALLS", 0)):              # pragma: debugging
    from coverage.debug import decorate_methods
    from coverage.debug import show_calls

    Coverage = decorate_methods(show_calls(show_args=True),
                                butnot=['get_data'])(Coverage)


def process_startup():
    """Call this at Python start-up to perhaps measure coverage.

    If the environment variable COVERAGE_PROCESS_START is defined, coverage
    measurement is started.  The value of the variable is the config file
    to use.

    There are two ways to configure your Python installation to invoke this
    function when Python starts:

    #. Create or append to sitecustomize.py to add these lines::

        import coverage
        coverage.process_startup()

    #. Create a .pth file in your Python installation containing::

        import coverage; coverage.process_startup()

    Returns the :class:`Coverage` instance that was started, or None if it was
    not started by this call.

    """
    cps = os.environ.get("COVERAGE_PROCESS_START")
    if not cps:
        # No request for coverage, nothing to do.
        return None

    # This function can be called more than once in a process. This happens
    # because some virtualenv configurations make the same directory visible
    # twice in sys.path.  This means that the .pth file will be found twice,
    # and executed twice, executing this function twice.  We set a global
    # flag (an attribute on this function) to indicate that coverage.py has
    # already been started, so we can avoid doing it twice.
    #
    # https://github.com/nedbat/coveragepy/issues/340 has more details.

    if hasattr(process_startup, "coverage"):
        # We've annotated this function before, so we must have already
        # started coverage.py in this process.  Nothing to do.
        return None

    cov = Coverage(config_file=cps)
    process_startup.coverage = cov
    cov._warn_no_data = False
    cov._warn_unimported_source = False
    cov._warn_preimported_source = False
    cov._auto_save = True
    cov.start()

    return cov


def _prevent_sub_process_measurement():
    """Stop any subprocess auto-measurement from writing data."""
    auto_created_coverage = getattr(process_startup, "coverage", None)
    if auto_created_coverage is not None:
        auto_created_coverage._auto_save = False
