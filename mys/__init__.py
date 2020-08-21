import sys
import argparse
from typing import Tuple

from .version import __version__


u8 = int
u16 = int
u32 = int
u64 = int
s8 = int
s16 = int
s32 = int
s64 = int
f32 = float
f64 = float

Queue = Tuple


def _do_run(args):
    raise NotImplementedError('The run subcommand is not yet implemented.')


def main():
    parser = argparse.ArgumentParser(
        description='The Mys programming language command line tool.')

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')

    # Workaround to make the subparser required in Python 3.
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='subcommand')
    subparsers.required = True

    # The run subparser.
    subparser = subparsers.add_parser(
        'run',
        description='Run the program.')
    subparser.set_defaults(func=_do_run)

    args = parser.parse_args()

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit('error: ' + str(e))
