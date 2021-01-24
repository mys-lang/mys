import subprocess

from colors import cyan
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer

from ..utils import BULB
from ..utils import add_jobs_argument
from ..utils import add_no_ccache_argument
from ..utils import add_optimize_argument
from ..utils import add_verbose_argument
from ..utils import box_print
from ..utils import build_app
from ..utils import build_prepare


def run_app(args, verbose):
    if verbose:
        print('./build/app')

    subprocess.run(['./build/app'] + args, check=True)


def style_source(code):
    return highlight(code,
                     PythonLexer(),
                     Terminal256Formatter(style='monokai')).rstrip()


def do_run(_parser, args, _mys_config):
    if build_prepare(args.verbose, args.optimize, args.no_ccache):
        build_app(args.debug, args.verbose, args.jobs, True)
        run_app(args.args, args.verbose)
    else:
        main_1 = style_source('def main():\n')
        main_2 = style_source("    print('Hello, world!')\n")
        func = style_source('main()')
        box_print([
            f"This package is not executable. Create '{cyan('src/main.mys')}' and",
            f"implement '{func}' to make the package executable.",
            '',
            main_1,
            main_2], BULB)

        raise Exception()


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'run',
        description='Build and run the application.')
    add_verbose_argument(subparser)
    add_jobs_argument(subparser)
    add_optimize_argument(subparser, 'speed')
    add_no_ccache_argument(subparser)
    subparser.add_argument('args', nargs='*')
    subparser.set_defaults(func=do_run)
