import glob
import json
import subprocess
import sys

from colors import cyan
from colors import red
from colors import yellow

from ..utils import Spinner
from ..utils import add_jobs_argument
from ..utils import read_package_configuration


def print_lint_message(message):
    location = f'{message["path"]}:{message["line"]}:{message["column"]}'
    level = message['type'].upper()
    symbol = message["symbol"]
    message = message["message"]

    if level == 'ERROR':
        level = red(level, style='bold')
    elif level == 'WARNING':
        level = yellow(level, style='bold')
    else:
        level = cyan(level, style='bold')

    print(f'{location} {level} {message} ({symbol})')


def do_lint(_parser, args, _mys_config):
    read_package_configuration()
    output = ''
    returncode = 1

    try:
        with Spinner('Linting'):
            proc = subprocess.run([sys.executable, '-m', 'pylint',
                                   '-j', str(args.jobs),
                                   '--output-format', 'json'
                                   ] + glob.glob('src/**/*.mys', recursive=True),
                                  stdout=subprocess.PIPE)
            output = proc.stdout.decode()
            returncode = proc.returncode
            proc.check_returncode()
    except Exception:
        pass

    for item in json.loads(output):
        print_lint_message(item)

    if returncode != 0:
        raise Exception()


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'lint',
        description='Perform static code analysis.')
    add_jobs_argument(subparser)
    subparser.set_defaults(func=do_lint)
