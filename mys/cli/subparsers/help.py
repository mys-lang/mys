def do_help(parser, _args, _mys_config):
    parser.print_help()


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'help',
        description='Show this help.')
    subparser.set_defaults(func=do_help)
