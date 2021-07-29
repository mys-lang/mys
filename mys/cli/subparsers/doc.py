import os
import sys

from ..utils import add_verbose_argument
from ..utils import read_package_configuration
from ..utils import run
from ..utils import create_file_from_template


def do_doc(_parser, args, _mys_config):
    config = read_package_configuration()
    package_name_title = config['package']['name'].replace('_', ' ').title()
    authors = ', '.join(config['package']['authors'])
    create_file_from_template('doc/conf.py',
                              '.',
                              package_name=package_name_title,
                              authors=authors)

    path = os.getcwd()
    os.chdir('doc')

    try:
        command = [
            sys.executable, '-m', 'sphinx',
            '-T', '-E',
            '-b', 'html',
            '-d', '../build/doc/doctrees',
            '-D', 'language=en',
            '.', '../build/doc/html'
        ]
        run(command, 'Building documentation', args.verbose)
    finally:
        os.chdir(path)

    os.remove('doc/conf.py')
    path = os.path.abspath('build/doc/html/index.html')
    print(f'Documentation: {path}')


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'doc',
        description='Build the documentation.')
    add_verbose_argument(subparser)
    subparser.set_defaults(func=do_doc)
