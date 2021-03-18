import getpass
import glob
import os
import shutil
import sys
import tarfile

import requests

from ..utils import INFO
from ..utils import Spinner
from ..utils import add_verbose_argument
from ..utils import box_print
from ..utils import create_file_from_template
from ..utils import read_package_configuration
from ..utils import run


def publish_create_release_package(config, verbose, archive):
    create_file_from_template('setup.py',
                              'publish',
                              name=f"mys-{config['package']['name']}",
                              version=config['package']['version'],
                              description=config['package']['description'],
                              author="'" + ', '.join(
                                  [author.name for author in config.authors]) + "'",
                              author_email="'" + ', '.join(
                                  [author.email for author in config.authors]) + "'",
                              dependencies='[]')
    create_file_from_template('MANIFEST.in', 'publish')
    shutil.copytree('../../src', 'src')
    shutil.copy('../../package.toml', 'package.toml')
    shutil.copy('../../README.rst', 'README.rst')
    run([sys.executable, 'setup.py', 'sdist'], f'Creating {archive}', verbose)


def publish_upload_release_package(verbose, username, password, archive):
    # Try to hide the password.
    env = os.environ.copy()

    if username is None:
        username = input('Username: ')

    if password is None:
        password = getpass.getpass()

    env['TWINE_USERNAME'] = username
    env['TWINE_PASSWORD'] = password
    command = [sys.executable, '-m', 'twine', 'upload']

    if verbose:
        command += ['--verbose']

    command += glob.glob('dist/*')

    run(command, f'Uploading {archive}', verbose, env=env)


def publish_create_release_package_address(name, version, archive):
    with Spinner(f'Creating {archive}'):
        base_dir = f'{name}-{version}'
        os.makedirs(base_dir)
        shutil.copytree('../../src', f'{base_dir}/src')
        shutil.copy('../../package.toml', f'{base_dir}/package.toml')
        shutil.copy('../../README.rst', f'{base_dir}/README.rst')

        with tarfile.open(archive, 'w:gz') as fout:
            fout.add(base_dir)


def publish_upload_release_package_address(address, archive):
    with Spinner(f'Uploading {archive}'):
        with open(archive, 'rb') as fin:
            requests.post(f'http://{address}/package/{archive}', data=fin.read())


def do_publish(_parser, args, _mys_config):
    config = read_package_configuration()
    publish_dir = 'build/publish'
    shutil.rmtree(publish_dir, ignore_errors=True)
    os.makedirs(publish_dir)
    path = os.getcwd()
    os.chdir(publish_dir)

    try:
        name = config['package']['name']
        version = config['package']['version']

        if args.address is None:
            box_print([
                "Mys is currently using Python's Package Index (PyPI). A PyPI",
                'account is required to publish your package.'], INFO)
            archive = f"mys-{name}-{version}.tar.gz"
            publish_create_release_package(config, args.verbose, archive)
            publish_upload_release_package(args.verbose,
                                           args.username,
                                           args.password,
                                           archive)
        else:
            archive = f"{name}-{version}.tar.gz"
            publish_create_release_package_address(name, version, archive)
            publish_upload_release_package_address(args.address, archive)
    finally:
        os.chdir(path)


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'publish',
        description='Publish a release.')
    add_verbose_argument(subparser)
    subparser.add_argument('-a', '--address',
                           help='Registry address.')
    subparser.add_argument('-u', '--username',
                           help='Registry username.')
    subparser.add_argument('-p', '--password',
                           help='Registry password.')
    subparser.set_defaults(func=do_publish)
