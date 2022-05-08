import requests

from ..utils import add_url_argument


def do_list(_parser, args, _mys_config):
    response = requests.get(f'{args.url}/standard-library/list.txt')

    if response.status_code != 200:
        raise Exception("failed to list packages")

    print(response.text)


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'list',
        description='Show packages in registry.')
    add_url_argument(subparser)
    subparser.set_defaults(func=do_list)
