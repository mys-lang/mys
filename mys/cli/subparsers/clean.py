import os
import shutil

from ..utils import Spinner
from ..utils import read_package_configuration


def remove_file(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

def do_clean(_parser, _args, _mys_config):
    read_package_configuration()

    with Spinner(text='Cleaning'):
        shutil.rmtree('build', ignore_errors=True)
        shutil.rmtree('coverage', ignore_errors=True)
        remove_file('.coverage')
        remove_file('.mys-coverage.txt')


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'clean',
        description='Remove build output.')
    subparser.set_defaults(func=do_clean)
