import argparse
import os
import sys
from traceback import print_exc

import toml
from colors import cyan

from ..version import __version__
from .subparsers import build
from .subparsers import clean
from .subparsers import doc
from .subparsers import help as help_
from .subparsers import install
from .subparsers import new
from .subparsers import publish
from .subparsers import run
from .subparsers import style
from .subparsers import test
from .subparsers import transpile
from .utils import create_file

DESCRIPTION = f'''\
The Mys programming language package manager.

Available subcommands are:

    {cyan('new')}      Create a new package.
    {cyan('build')}    Build the appliaction.
    {cyan('run')}      Build and run the application.
    {cyan('test')}     Build and run tests
    {cyan('clean')}    Remove build output.
    {cyan('publish')}  Publish a release.
    {cyan('install')}  Install an application from local package or registry.
    {cyan('doc')}      Build the documentation.
'''


def find_config_file():
    path = os.getenv('MYS_CONFIG')
    config_dir = os.path.expanduser('~/.config/mys')
    config_path = os.path.join(config_dir, 'config.toml')

    if path is not None:
        return path

    if not os.path.exists(config_path):
        os.makedirs(config_dir, exist_ok=True)
        create_file(config_path, '')

    return config_path


def load_mys_config():
    """Mys tool configuration.

    Add validation when needed.

    """

    path = find_config_file()

    try:
        with open(path) as fin:
            return toml.loads(fin.read())
    except toml.decoder.TomlDecodeError:
        raise Exception(f"failed to load Mys configuration file '{path}'")


def create_parser():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument(
        '-C', '--directory',
        help='Change directory to given directory before doing anything.')
    parser.add_argument('--config', help='Configuration file to use.')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')

    subparsers = parser.add_subparsers(dest='subcommand',
                                       help='Subcommand to execute.',
                                       metavar='subcommand')

    new.add_subparser(subparsers)
    build.add_subparser(subparsers)
    run.add_subparser(subparsers)
    test.add_subparser(subparsers)
    clean.add_subparser(subparsers)
    transpile.add_subparser(subparsers)
    publish.add_subparser(subparsers)
    install.add_subparser(subparsers)
    style.add_subparser(subparsers)
    doc.add_subparser(subparsers)
    help_.add_subparser(subparsers)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    if args.directory is not None:
        os.chdir(args.directory)

    try:
        args.func(parser, args, load_mys_config())
    except Exception as e:
        if args.debug:
            print_exc()

        sys.exit(str(e))
    except KeyboardInterrupt:
        print()

        if args.debug:
            raise

        sys.exit(1)
