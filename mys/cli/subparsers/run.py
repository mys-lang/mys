import subprocess

from colors import cyan
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer

from ..utils import BULB
from ..utils import BuildConfig
from ..utils import add_coverage_argument
from ..utils import add_debug_symbols_argument
from ..utils import add_jobs_argument
from ..utils import add_no_ccache_argument
from ..utils import add_optimize_argument
from ..utils import add_unsafe_argument
from ..utils import add_url_argument
from ..utils import add_verbose_argument
from ..utils import box_print
from ..utils import build_app
from ..utils import build_prepare
from ..utils import create_coverage_report


def run_app(args, verbose, build_dir):
    command = f'./{build_dir}/app'

    if verbose:
        print(command)

    subprocess.run([command] + args, check=True)


def style_source(code):
    return highlight(code,
                     PythonLexer(),
                     Terminal256Formatter(style='monokai')).rstrip()


def do_run(_parser, args, _mys_config):
    build_config = BuildConfig(args.debug,
                               args.verbose,
                               args.optimize,
                               args.debug_symbols,
                               args.no_ccache,
                               args.coverage,
                               args.unsafe,
                               args.jobs,
                               args.url)
    is_application, build_dir = build_prepare(build_config)

    if is_application:
        build_app(build_config, True, build_dir)
        run_app(args.args, args.verbose, build_dir)

        if args.coverage:
            create_coverage_report()
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
    add_debug_symbols_argument(subparser)
    add_no_ccache_argument(subparser)
    add_url_argument(subparser)
    add_coverage_argument(subparser)
    add_unsafe_argument(subparser)
    subparser.add_argument('args', nargs='*')
    subparser.set_defaults(func=do_run)
