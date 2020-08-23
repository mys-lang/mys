import subprocess
import os
import sys
import argparse
from typing import Tuple
import ast
from pprint import pprint
from pprintast import pprintast
import toml

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
authors = ["Your Name <your.name@example.com>"]
'''

MAIN_MYS = '''\
def main():
    print('Hello, world!')
'''

MAIN_MYS_CPP = '''\
#include "mys.hpp"

int main()
{
    std::cout << "Hello, world!" << std::endl;

    return 0;
}
'''

MYS_DIR = os.path.dirname(os.path.realpath(__file__))

MAKEFILE_FMT = '''\
CXX ?= g++
MYS ?= mys
CFLAGS += -I{mys_dir}
CFLAGS += -Wall
CFLAGS += -std=c++17
LDFLAGS += -std=c++17
EXE = app

all: $(EXE)
\t./$(EXE)

$(EXE): transpiled/main.mys.o
\t$(CXX) $(LDFLAGS) -o $@ $^

transpiled/main.mys.cpp: ../src/main.mys
\t$(MYS) transpile -o $(dir $@) $^

transpiled/main.mys.o: transpiled/main.mys.cpp
\t$(CXX) $(CFLAGS) -c transpiled/main.mys.cpp -o transpiled/main.mys.o
'''


def _do_new(args):
    os.makedirs(args.path)
    path = os.getcwd()
    os.chdir(args.path)

    try:
        with open('Package.toml', 'w') as fout:
            fout.write(PACKAGE_FMT.format(name=os.path.basename(args.path)))

        os.mkdir('src')

        with open('src/main.mys', 'w') as fout:
            fout.write(MAIN_MYS)
    finally:
        os.chdir(path)


def load_package_configuration():
    with open('Package.toml') as fin:
        config = toml.loads(fin.read())

    print('Package config:')
    pprint(config)


def setup_build():
    os.makedirs('build/transpiled')

    with open('build/Makefile', 'w') as fout:
        fout.write(MAKEFILE_FMT.format(mys_dir=MYS_DIR))


def _do_run(args):
    load_package_configuration()

    if not os.path.exists('build'):
        setup_build()

    subprocess.run(['make', '-C', 'build'], check=True)


def transpile(path):
    with open(path) as fin:
        data = fin.read()

    pprintast(data)


def _do_transpile(args):
    mys_cpp = os.path.join(args.outdir, os.path.basename(args.mysfile) + '.cpp')
    transpile(args.mysfile)

    with open (mys_cpp, 'w') as fout:
        fout.write(MAIN_MYS_CPP)


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
    subparser.add_argument('args', nargs='*')
    subparser.set_defaults(func=_do_run)

    # The transpile subparser.
    subparser = subparsers.add_parser(
        'transpile',
        description='Transpile given Mys file to C++.')
    subparser.add_argument('-o', '--outdir',
                           default='.',
                           help='Output directory.')
    subparser.add_argument('mysfile')
    subparser.set_defaults(func=_do_transpile)

    args = parser.parse_args()

    if args.debug:
        args.func(args)
    else:
        try:
            args.func(args)
        except BaseException as e:
            sys.exit('error: ' + str(e))
