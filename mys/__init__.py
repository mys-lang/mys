import subprocess
import os
import sys
import argparse
from typing import Tuple

from .version import __version__


u8 = int
u16 = int
u32 = int
u64 = int
s8 = int
s16 = int
s32 = int
s64 = int
f32 = float
f64 = float

Queue = Tuple


PACKAGE_FMT = '''\
[package]
name = "{name}"
version = "0.1.0"
authors = ["Kalle Kula <kalle.kula@company.com>"]
'''

MAIN_MYS = '''\
def main():
    print('Hello, world!')
'''

MAIN_MYS_CPP = '''\
#include <iostream>

int main()
{
    std::cout << "Hello, world!" << std::endl;

    return 0;
}
'''


def _do_new(args):
    os.makedirs(args.path)
    os.chdir(args.path)

    with open('Package.toml', 'w') as fout:
        fout.write(PACKAGE_FMT.format(name=os.path.basename(args.path)))

    os.mkdir('src')

    with open('src/main.mys', 'w') as fout:
        fout.write(MAIN_MYS)


def _do_run(args):
    os.makedirs('build/transpiled')

    with open('build/transpiled/main.mys.cpp', 'w') as fout:
        fout.write(MAIN_MYS_CPP)

    subprocess.run([
        'g++',
        '-std=gnu++17',
        '-o', 'build/app',
        'build/transpiled/main.mys.cpp'])
    subprocess.run(['build/app'])


def main():
    parser = argparse.ArgumentParser(
        description='The Mys programming language command line tool.')

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')

    # Workaround to make the subparser required in Python 3.
    subparsers = parser.add_subparsers(title='subcommands',
                                       dest='subcommand')
    subparsers.required = True

    # The new subparser.
    subparser = subparsers.add_parser(
        'new',
        description='Create a new package.')
    subparser.add_argument('path')
    subparser.set_defaults(func=_do_new)

    # The run subparser.
    subparser = subparsers.add_parser(
        'run',
        description='Run the program.')
    subparser.set_defaults(func=_do_run)

    args = parser.parse_args()

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit('error: ' + str(e))
