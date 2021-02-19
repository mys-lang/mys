import os

from ..utils import BuildConfig
from ..utils import add_coverage_argument
from ..utils import add_jobs_argument
from ..utils import add_no_ccache_argument
from ..utils import add_optimize_argument
from ..utils import add_unsafe_argument
from ..utils import add_verbose_argument
from ..utils import build_prepare
from ..utils import create_coverage_report
from ..utils import run


def do_test(_parser, args, _mys_config):
    build_config = BuildConfig(args.debug,
                               args.verbose,
                               args.optimize,
                               True,
                               args.no_ccache,
                               args.coverage,
                               args.unsafe,
                               args.jobs)
    _, build_dir = build_prepare(build_config)

    command = [
        'make', '-f', f'{build_dir}/Makefile', 'test', 'TEST=yes'
    ]

    if os.getenv('MAKEFLAGS') is None:
        command += ['-j', str(args.jobs)]

    if args.debug:
        command += ['TRANSPILE_DEBUG=--debug']

    if args.coverage:
        command += ['COVERAGE=yes']

    if args.unsafe:
        command += ['UNSAFE=yes']

    if args.test_pattern is None:
        test_pattern = []
    else:
        test_pattern = [args.test_pattern]

    run(command, 'Building tests', args.verbose)
    run([f'./{build_dir}/test'] + test_pattern, 'Running tests', args.verbose)

    if args.coverage:
        create_coverage_report(['./src/**'])


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'test',
        description='Build and run tests.')
    add_verbose_argument(subparser)
    add_jobs_argument(subparser)
    add_optimize_argument(subparser, 'debug')
    add_no_ccache_argument(subparser)
    add_coverage_argument(subparser)
    add_unsafe_argument(subparser)
    subparser.add_argument(
        'test_pattern',
        nargs='?',
        help=("Only run tests matching given pattern. '^' matches the "
              "beginning and '$' matches the end of the test name."))
    subparser.set_defaults(func=do_test)
