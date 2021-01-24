from ..utils import ERROR
from ..utils import box_print
from ..utils import read_package_configuration


def do_style(_parser, _args, _mys_config):
    read_package_configuration()

    box_print(['This subcommand is not yet implemented.'], ERROR)

    raise Exception()


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'style',
        description=(
            'Check that the package follows the Mys style guidelines. Automatically '
            'fixes trivial errors and prints the rest.'))
    subparser.set_defaults(func=do_style)
