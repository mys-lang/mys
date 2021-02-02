import os

from ..utils import add_jobs_argument
from ..utils import add_no_ccache_argument
from ..utils import add_optimize_argument
from ..utils import add_verbose_argument
from ..utils import build_prepare
from ..utils import run


def add_lines(coverage_data, path, linenos):
    coverage_data.add_lines(
        {path: {lineno: None for lineno in linenos}})


def create_coverage_report():
    from ...coverage import Coverage
    from ...coverage import CoverageData

    coverage_data = CoverageData()

    with open('.mys-coverage.txt', 'r') as fin:
        path = None
        linenos = []

        for line in fin:
            line = line.strip()

            if line.startswith('File:'):
                if path is not None:
                    add_lines(coverage_data, path, linenos)

                path = os.path.abspath(line[6:])
                linenos = []
            else:
                lineno, count = line.split()

                if int(count) > 0:
                    linenos.append(int(lineno))

        if path is not None:
            add_lines(coverage_data, path, linenos)

    coverage_data.write()

    cov = Coverage('.coverage', auto_data=True)
    cov.start()
    cov.stop()
    cov.html_report(directory='covhtml')
    path = os.path.abspath('covhtml/index.html')
    print(f'Coverage report: {path}')


def do_test(_parser, args, _mys_config):
    build_prepare(args.verbose, args.optimize, args.no_ccache)

    command = [
        'make', '-f', 'build/Makefile', 'test', 'TEST=yes'
    ]

    if os.getenv('MAKEFLAGS') is None:
        command += ['-j', str(args.jobs)]

    if args.debug:
        command += ['TRANSPILE_DEBUG=--debug']

    if args.coverage:
        command += ['COVERAGE=yes']

    run(command, 'Building tests', args.verbose)
    run(['./build/test'], 'Running tests', args.verbose)

    if args.coverage:
        create_coverage_report()

def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'test',
        description='Build and run tests.')
    add_verbose_argument(subparser)
    add_jobs_argument(subparser)
    add_optimize_argument(subparser, 'debug')
    add_no_ccache_argument(subparser)
    subparser.add_argument('--coverage',
                           action='store_true',
                           help='Create a coverage report (experimental).')
    subparser.set_defaults(func=do_test)
