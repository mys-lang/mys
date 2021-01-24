import os

from ..utils import add_jobs_argument
from ..utils import add_no_ccache_argument
from ..utils import add_optimize_argument
from ..utils import add_verbose_argument
from ..utils import build_prepare
from ..utils import run


def do_test(_parser, args, _mys_config):
    build_prepare(args.verbose, args.optimize, args.no_ccache)

    command = [
        'make', '-f', 'build/Makefile', 'test', 'TEST=yes'
    ]

    if os.getenv('MAKEFLAGS') is None:
        command += ['-j', str(args.jobs)]

    if args.debug:
        command += ['TRANSPILE_DEBUG=--debug']

    run(command, 'Building tests', args.verbose)
    run(['./build/test'], 'Running tests', args.verbose)


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'test',
        description='Build and run tests.')
    add_verbose_argument(subparser)
    add_jobs_argument(subparser)
    add_optimize_argument(subparser, 'debug')
    add_no_ccache_argument(subparser)
    subparser.set_defaults(func=do_test)
