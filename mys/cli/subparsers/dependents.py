import requests

from ..utils import add_url_argument


def do_dependents(_parser, args, _mys_config):
    response = requests.get(
        f'{args.url}/standard-library/{args.package}/dependents.txt')

    if response.status_code != 200:
        raise Exception(f"failed to find dependets on package '{args.package}'")

    print(response.text, end='')


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'dependents',
        description='Show dependents.')
    add_url_argument(subparser)
    subparser.add_argument('package', help='Package to find dependents on.')
    subparser.set_defaults(func=do_dependents)
