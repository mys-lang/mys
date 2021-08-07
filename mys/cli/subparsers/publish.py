import os
import shutil
import tarfile
from http.client import responses

import requests

from ..utils import Spinner
from ..utils import add_verbose_argument
from ..utils import read_package_configuration


def publish_create_release_package(name, version, archive):
    with Spinner(f'Creating {archive}'):
        base_dir = f'{name}-{version}'
        os.makedirs(base_dir)

        if os.path.exists('../../doc'):
            shutil.copytree('../../doc', f'{base_dir}/doc')

        if os.path.exists('../../assets'):
            shutil.copytree('../../assets', f'{base_dir}/assets')

        shutil.copytree('../../src', f'{base_dir}/src')
        shutil.copy('../../package.toml', f'{base_dir}/package.toml')
        shutil.copy('../../README.rst', f'{base_dir}/README.rst')

        with tarfile.open(archive, 'w:gz') as fout:
            fout.add(base_dir)


def publish_upload_release_package(address, access_token, archive):
    with Spinner(f'Uploading {archive}'):
        with open(archive, 'rb') as fin:
            if access_token is None:
                params = None
            else:
                params = {'token': access_token}

            response = requests.post(f'{address}/package/{archive}',
                                     params=params,
                                     data=fin.read())

            if response.status_code != 200:
                raise Exception(
                    'Package publish failed with HTTP '
                    f'{response.status_code} {responses[response.status_code]}.')

    if response.text:
        response_json = response.json()

        if 'token' in response_json:
            print('Access token needed to publish this package again:',
                  response_json['token'])


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
        archive = f"{name}-{version}.tar.gz"
        publish_create_release_package(name, version, archive)
        publish_upload_release_package(args.address, args.token, archive)
    finally:
        os.chdir(path)


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'publish',
        description='Publish a release to the registry.')
    add_verbose_argument(subparser)
    subparser.add_argument('-a', '--address',
                           default='https://mys-lang.org',
                           help='Registry address (default: %(default)s)')
    subparser.add_argument('-t', '--token',
                           help='Package access token.')
    subparser.set_defaults(func=do_publish)
