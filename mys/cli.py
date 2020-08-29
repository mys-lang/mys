import subprocess
import os
import sys
import argparse
import toml
import shutil
import yaspin
import getpass

from .transpile import transpile
from .version import __version__


MYS_DIR = os.path.dirname(os.path.realpath(__file__))

PACKAGE_TOML_FMT = '''\
[package]
name = "{name}"
version = "0.1.0"
authors = [{authors}]

[dependencies]
# foobar = "*"
'''

MAIN_MYS = '''\
def main():
    print('Hello, world!')
'''

MAKEFILE_FMT = '''\
CXX ?= g++
MYS ?= mys
CFLAGS += -I{mys_dir}
CFLAGS += -Wall
CFLAGS += -O3
CFLAGS += -std=c++17
CFLAGS += -fdata-sections
CFLAGS += -ffunction-sections
LDFLAGS += -std=c++17
LDFLAGS += -static
LDFLAGS += -Wl,--gc-sections
EXE = app

all: $(EXE)

$(EXE): transpiled/main.mys.o mys.o
\t$(CXX) $(LDFLAGS) -o $@ $^

mys.o: {mys_dir}/mys.cpp
\t$(CXX) $(CFLAGS) -c $^ -o $@

transpiled/main.mys.cpp: ../src/main.mys
\t$(MYS) -d transpile -o $(dir $@) $^

transpiled/main.mys.o: transpiled/main.mys.cpp
\t$(CXX) $(CFLAGS) -c $^ -o $@
'''


class Spinner(yaspin.api.Yaspin):

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type is None:
            self.color = 'green'
            self.ok('✔')
        else:
            self.color = 'red'
            self.ok('✘')

        return super().__exit__(exc_type, exc_val, traceback)


def git_config_get(item, default=None):
    try:
        return subprocess.check_output(['git', 'config', '--get', item])
    except FileNotFoundError:
        return default


def find_authors(authors):
    if authors is not None:
        return ', '.join([f'"{author}"'for author in authors])

    user = git_config_get('user.name', getpass.getuser())
    email = git_config_get('user.email', f'{user}@example.com')

    return f'"{user} <{email}>"'


def _do_new(args):
    name = os.path.basename(args.path)
    authors = find_authors(args.authors)

    with Spinner(text=f"Creating package '{name}'.", color='yellow') as spinner:
        os.makedirs(args.path)
        path = os.getcwd()
        os.chdir(args.path)

        try:
            with open('Package.toml', 'w') as fout:
                fout.write(PACKAGE_TOML_FMT.format(name=name,
                                                   authors=authors))

            os.mkdir('src')

            with open('src/main.mys', 'w') as fout:
                fout.write(MAIN_MYS)
        finally:
            os.chdir(path)


def load_package_configuration():
    with open('Package.toml') as fin:
        config = toml.loads(fin.read())

    package = config.get('package')

    if package is None:
        raise Exception("'[package]' not found in Package.toml.")

    for name in ['name', 'version', 'authors']:
        if name not in package:
            raise Exception(f"'[package].{name}' not found in Package.toml.")

    return config


def setup_build():
    os.makedirs('build/transpiled')

    with open('build/Makefile', 'w') as fout:
        fout.write(MAKEFILE_FMT.format(mys_dir=MYS_DIR))


def build_app(verbose):
    load_package_configuration()

    if not os.path.exists('build'):
        setup_build()

    command = ['make', '-C', 'build']

    if not verbose:
        command += ['-s']

        try:
            with Spinner(text='Building.', color='yellow') as spinner:
                result = subprocess.run(command,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        encoding='utf-8')
                result.check_returncode()
        finally:
            print(result.stdout, end='')
            print(result.stderr, end='')
    else:
        subprocess.run(command, check=True)


def run_app(args):
    subprocess.run(['build/app'] + args, check=True)


def _do_build(args):
    build_app(args.verbose)


def _do_run(args):
    build_app(args.verbose)
    run_app(args.args)


def _do_clean(args):
    with Spinner(text='Cleaning.', color='yellow') as spinner:
        shutil.rmtree('build', ignore_errors=True)


def _do_transpile(args):
    mys_cpp = os.path.join(args.outdir, os.path.basename(args.mysfile) + '.cpp')

    with open(args.mysfile) as fin:
        source = transpile(fin.read())

    with open (mys_cpp, 'w') as fout:
        fout.write(source)


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
    subparser.add_argument('--author',
                           dest='authors',
                           action='append',
                           help='Package author. May be given multiple times.')
    subparser.add_argument('path')
    subparser.set_defaults(func=_do_new)

    # The build subparser.
    subparser = subparsers.add_parser(
        'build',
        description='Build the appliaction.')
    subparser.add_argument('--verbose',
                           action='store_true',
                           help='Verbose output.')
    subparser.set_defaults(func=_do_build)

    # The run subparser.
    subparser = subparsers.add_parser(
        'run',
        description='Build and run the application.')
    subparser.add_argument('--verbose',
                           action='store_true',
                           help='Verbose output.')
    subparser.add_argument('args', nargs='*')
    subparser.set_defaults(func=_do_run)

    # The clean subparser.
    subparser = subparsers.add_parser(
        'clean',
        description='Remove build output.')
    subparser.set_defaults(func=_do_clean)

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
