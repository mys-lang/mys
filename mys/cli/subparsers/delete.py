from http.client import responses

import requests

from ..utils import Spinner
from ..utils import add_verbose_argument


def do_delete(_parser, args, _mys_config):
    print(args.package)
    print(args.token)

    with Spinner(f'Deleting {args.package}'):
        response = requests.delete(f'{args.address}/package/{args.package}',
                                   params={'token': args.token})

        if response.status_code != 200:
            raise Exception(
                'Package delete failed with HTTP '
                f'{response.status_code} {responses[response.status_code]}.')


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'delete',
        description='Delete a package from the registry.')
    add_verbose_argument(subparser)
    subparser.add_argument('-a', '--address',
                           default='https://mys-lang.org',
                           help='Registry address (default: %(default)s)')
    subparser.add_argument('package', help='Package to delete.')
    subparser.add_argument('token', help='Package access token.')
    subparser.set_defaults(func=do_delete)
