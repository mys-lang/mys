from gql import Client
from gql import gql
from gql.transport.requests import RequestsHTTPTransport

from ..utils import add_url_argument


def do_list(_parser, args, _mys_config):
    client = Client(transport=RequestsHTTPTransport(url=f"{args.url}/graphql"))
    response = client.execute(gql("{standardLibrary{packages{name}}}"))

    for package in response['standardLibrary']['packages']:
        print(package['name'])

def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'list',
        description='Show packages in registry.')
    add_url_argument(subparser)
    subparser.set_defaults(func=do_list)
