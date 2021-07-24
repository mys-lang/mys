import shutil

from ..utils import DOWNLOAD_DIRECTORY
from ..utils import add_url_argument
from ..utils import add_verbose_argument
from ..utils import download_dependencies
from ..utils import read_package_configuration
from ..utils import setup_build


def do_fetch(_parser, args, _mys_config):
    config = read_package_configuration()
    shutil.rmtree(DOWNLOAD_DIRECTORY, ignore_errors=True)
    setup_build()
    download_dependencies(config, args.url)


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'fetch',
        description='Download and extract all dependencies.')
    add_verbose_argument(subparser)
    add_url_argument(subparser)
    subparser.set_defaults(func=do_fetch)
