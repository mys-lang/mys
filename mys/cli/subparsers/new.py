import getpass
import os
import re
import shutil
import subprocess

from colors import cyan

from ..utils import BULB
from ..utils import ERROR
from ..utils import MYS_DIR
from ..utils import Spinner
from ..utils import box_print
from ..utils import create_file_from_template


class BadPackageNameError(Exception):
    pass


def git_config_get(item, default=None):
    try:
        return subprocess.check_output(['git', 'config', '--get', item],
                                       encoding='utf-8').strip()
    except Exception:
        return default


def create_new_file(path, **kwargs):
    create_file_from_template(path, 'new', **kwargs)


def validate_package_name(package_name):
    if not re.match(r'^[a-z][a-z0-9_]*$', package_name):
        raise BadPackageNameError()


def find_authors(authors):
    if authors is not None:
        return ', '.join([f'"{author}"' for author in authors])

    user = git_config_get('user.name', getpass.getuser())
    email = git_config_get('user.email', f'{user}@example.com')

    return f'"{user} <{email}>"'


def do_new(_parser, args, _mys_config):
    package_name = os.path.basename(args.path)
    authors = find_authors(args.authors)

    try:
        with Spinner(text=f"Creating package {package_name}"):
            validate_package_name(package_name)

            os.makedirs(args.path)
            path = os.getcwd()
            os.chdir(args.path)

            try:
                create_new_file('package.toml',
                                package_name=package_name,
                                authors=authors)
                create_new_file('.gitignore')
                create_new_file('.gitattributes')
                create_new_file('README.rst',
                                package_name=package_name,
                                title=package_name.replace('_', ' ').title(),
                                line='=' * len(package_name))
                create_new_file('LICENSE')
                shutil.copyfile(os.path.join(MYS_DIR, 'cli/templates/new/pylintrc'),
                                'pylintrc')
                os.mkdir('src')
                create_new_file('src/lib.mys')
                create_new_file('src/main.mys')
            finally:
                os.chdir(path)
    except BadPackageNameError:
        box_print(['Package names must start with a letter and only',
                   'contain letters, numbers and underscores. Only lower',
                   'case letters are allowed.',
                   '',
                   'Here are a few examples:',
                   '',
                   f'{cyan("mys new foo")}'
                   f'{cyan("mys new f1")}'
                   f'{cyan("mys new foo_bar")}'],
                  ERROR)
        raise Exception()

    cd = cyan(f'cd {package_name}')

    box_print(['Build and run the new package by typing:',
               '',
               f'{cd}',
               f'{cyan("mys run")}'],
              BULB,
              width=53)


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'new',
        description='Create a new package.')
    subparser.add_argument(
        '--author',
        dest='authors',
        action='append',
        help=("Package author as 'Mys Lang <mys.lang@example.com>'. May "
              "be given multiple times."))
    subparser.add_argument('path')
    subparser.set_defaults(func=do_new)
