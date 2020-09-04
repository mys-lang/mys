import tarfile
import re
import subprocess
import os
import sys
import argparse
import toml
import shutil
import yaspin
import getpass
import glob
import multiprocessing
from colors import bold
from colors import yellow
from colors import red
from colors import green
from colors import cyan
from colors import blue
import json

from .transpile import transpile
from .version import __version__

MYS_DIR = os.path.dirname(os.path.realpath(__file__))

BULB = yellow('💡', style='bold')
INFO = blue('🛈', style='bold')

PACKAGE_TOML_FMT = '''\
[package]
name = "{name}"
version = "0.1.0"
authors = [{authors}]

[dependencies]
# foobar = "*"
'''

README_FMT = '''\
{name}
{line}

Add more information about your package here!
'''

MAIN_MYS = '''\
def main():
    print('Hello, world!')
'''

MAKEFILE_FMT = '''\
CXX ?= g++
MYS ?= mys
CFLAGS += -I{mys_dir}/lib
CFLAGS += -Wall
CFLAGS += -Wno-unused-variable
CFLAGS += -O3
CFLAGS += -std=c++17
CFLAGS += -fdata-sections
CFLAGS += -ffunction-sections
CFLAGS += -fdiagnostics-color=always
LDFLAGS += -std=c++17
LDFLAGS += -static
LDFLAGS += -Wl,--gc-sections
LDFLAGS += -fdiagnostics-color=always
{srcs}
OBJ = $(SRC:%=build/transpiled/%.o)
EXE = build/app

all: $(EXE)

$(EXE): $(OBJ) build/mys.o
\t$(CXX) $(LDFLAGS) -o $@ $^

build/mys.o: {mys_dir}/lib/mys.cpp
\t$(CXX) $(CFLAGS) -c $^ -o $@

build/transpiled/%.mys.cpp: %.mys
\tmkdir -p $(dir $@)
\t$(MYS) transpile -o $(dir $@) $^

build/transpiled/%.mys.o: build/transpiled/%.mys.cpp
\t$(CXX) $(CFLAGS) -c $^ -o $@
'''

SETUP_PY_FMT = '''\
from setuptools import setup


setup(name='{name}',
      version='{version}',
      description={description},
      long_description=open('README.rst', 'r').read(),
      author={author},
      author_email={author_email},
      install_requires={dependencies})
'''

MANIFEST_IN = '''\
include Package.toml
recursive-include src *.mys
'''

class Spinner(yaspin.api.Yaspin):

    def __init__(self, text):
        super().__init__(text=text, color='yellow')

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type is None:
            self.color = 'green'
            self.ok('✔')
        else:
            self.color = 'red'
            self.ok('✘')

        return super().__exit__(exc_type, exc_val, traceback)

def run_with_spinner(command, message, env=None):
    output = ''

    try:
        with Spinner(text=message):
            result = subprocess.run(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    encoding='utf-8',
                                    env=env)
            output = result.stdout
            result.check_returncode()
    except Exception:
        lines = []

        for line in output.splitlines():
            if 'make: *** ' in line:
                continue

            lines.append(line)

        sys.exit('\n'.join(lines).rstrip())

def run(command, message, verbose, env=None):
    if verbose:
        try:
            subprocess.run(command, check=True, env=env)
            print(green('✔ ') + message)
        except Exception:
            print(red('✘ ') + message)
            raise
    else:
        run_with_spinner(command, message, env)

def git_config_get(item, default=None):
    try:
        return subprocess.check_output(['git', 'config', '--get', item],
                                       encoding='utf-8').strip()
    except Exception:
        return default

def find_authors(authors):
    if authors is not None:
        return ', '.join([f'"{author}"'for author in authors])

    user = git_config_get('user.name', getpass.getuser())
    email = git_config_get('user.email', f'{user}@example.com')

    return f'"{user} <{email}>"'

def do_new(_parser, args):
    name = os.path.basename(args.path)
    authors = find_authors(args.authors)

    with Spinner(text=f"Creating package {name}."):
        os.makedirs(args.path)
        path = os.getcwd()
        os.chdir(args.path)

        try:
            with open('Package.toml', 'w') as fout:
                fout.write(PACKAGE_TOML_FMT.format(name=name,
                                                   authors=authors))

            with open('README.rst', 'w') as fout:
                fout.write(README_FMT.format(name=name.replace('_', ' ').title(),
                                             line='=' * len(name)))

            shutil.copyfile(os.path.join(MYS_DIR, 'lint/pylintrc'), 'pylintrc')
            os.mkdir('src')

            with open('src/main.mys', 'w') as fout:
                fout.write(MAIN_MYS)
        finally:
            os.chdir(path)

    print(f'┌────────────────────────────────────────────────── {BULB} ─┐')
    print('│ Build and run the new package by typing:              │')
    print('│                                                       │')
    print(f'│ {cyan("cd")} {name}' + (51 - len(name)) * ' ' + '│')
    print(f'│ {cyan("mys run")}                                               │')
    print('└───────────────────────────────────────────────────────┘')

class Author:

    def __init__(self, name, email):
        self.name = name
        self.email = email

class Config:

    def __init__(self):
        self.authors = []
        self.config = self.load_package_configuration()

    def load_package_configuration(self):
        with open('Package.toml') as fin:
            config = toml.loads(fin.read())

        package = config.get('package')

        if package is None:
            raise Exception("'[package]' not found in Package.toml.")

        for name in ['name', 'version', 'authors']:
            if name not in package:
                raise Exception(f"'[package].{name}' not found in Package.toml.")

        for author in package['authors']:
            mo = re.match(r'^([^<]+)<([^>]+)>$', author)

            if not mo:
                raise Exception(f"Bad author '{author}'.")

            self.authors.append(Author(mo.group(1).strip(), mo.group(2).strip()))

        if 'dependencies' not in config:
            config['dependencies'] = {}

        return config

    def __getitem__(self, key):
        return self.config[key]

def setup_build():
    os.makedirs('build/transpiled')
    os.makedirs('build/dependencies')

def download_dependencies(config, verbose, local_registry):
    for name, version in config['dependencies'].items():
        archive = f'mys-{name}-{version}.tar.gz'
        path = f'build/dependencies/{archive}'
        download_directory = 'build/dependencies'

        if os.path.exists(path):
            continue

        if local_registry:
            with Spinner(text=f"Copying {archive}."):
                shutil.copyfile(os.path.join(local_registry, archive),
                                os.path.join(download_directory, archive))
        else:
            command = [
                sys.executable, '-m', 'pip', 'download',
                '-d', download_directory,
                f'mys-{name}=={version}'
            ]
            run(command, f"Downloading {archive}.", verbose)

        with Spinner(text=f"Extracting {archive}."):
            with tarfile.open(path) as fin:
                fin.extractall('build/dependencies')

def read_package_configuration():
    try:
        with Spinner('Reading package configuration.'):
            return Config()
    except Exception:
        print(f'┌──────────────────────────────────────────────────────────────── {BULB} ─┐')
        print('│ Current directory does not contain a Mys package (Package.toml does │')
        print('│ not exist).                                                         │')
        print('│                                                                     │')
        print('│ Please enter a Mys package directory, and try again.                │')
        print('│                                                                     │')
        print(f'│ You can create a new package with {cyan("mys new <name>")}.                   │')
        print('└─────────────────────────────────────────────────────────────────────┘')
        sys.exit(1)

def find_package_sources(path, ignores=None):
    if ignores is None:
        ignores = []

    ignores = [path + ignore for ignore in ignores]
    srcs = glob.glob(path + 'src/**.mys', recursive=True)

    return [src for src in srcs if src not in ignores]

def create_makefile(config):
    srcs = find_package_sources('')

    for name, version in config['dependencies'].items():
        path = f'build/dependencies/mys-{name}-{version}/'
        srcs += find_package_sources(path, ignores=['src/main.mys'])

    srcs = '\n'.join([f'SRC += {src}' for src in srcs])

    with open('build/Makefile', 'w') as fout:
        fout.write(MAKEFILE_FMT.format(mys_dir=MYS_DIR, srcs=srcs))

def build_app(verbose, jobs, local_registry):
    config = read_package_configuration()

    if not os.path.exists('build/Makefile'):
        setup_build()

    download_dependencies(config, verbose, local_registry)
    create_makefile(config)

    command = ['make', '-f', 'build/Makefile', '-j', str(jobs)]

    if not verbose:
        command += ['-s']

    run(command, 'Building.', verbose)

def do_build(_parser, args):
    build_app(args.verbose, args.jobs, args.local_registry)

def run_app(args, verbose):
    if verbose:
        print('./build/app')

    subprocess.run(['./build/app'] + args, check=True)

def do_run(_parser, args):
    build_app(args.verbose, args.jobs, args.local_registry)
    run_app(args.args, args.verbose)

def do_clean(_parser, args):
    read_package_configuration()

    with Spinner(text='Cleaning.'):
        shutil.rmtree('build', ignore_errors=True)

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

def do_lint(_parser, args):
    read_package_configuration()
    output = ''
    returncode = 1

    try:
        with Spinner('Linting.'):
            proc = subprocess.run([sys.executable, '-m', 'pylint',
                                   '-j', str(args.jobs),
                                   '--output-format', 'json'
                                   ] + glob.glob('src/**.mys', recursive=True),
                                  stdout=subprocess.PIPE)
            output = proc.stdout.decode()
            returncode = proc.returncode
            proc.check_returncode()
    except Exception:
        pass

    for item in json.loads(output):
        print_lint_message(item)

    if returncode != 0:
        sys.exit(1)

def do_transpile(_parser, args):
    mys_cpp = os.path.join(args.outdir, os.path.basename(args.mysfile) + '.cpp')

    with open(args.mysfile) as fin:
        try:
            source = transpile(fin.read(), args.mysfile)
        except Exception as e:
            sys.exit(str(e))

    with open (mys_cpp, 'w') as fout:
        fout.write(source)

def publish_create_release_package(config, verbose, archive):
    with open('setup.py', 'w') as fout:
        fout.write(SETUP_PY_FMT.format(
            name=f"mys-{config['package']['name']}",
            version=config['package']['version'],
            description="'Short description.'",
            author="'" + ', '.join(
                [author.name for author in config.authors]) + "'",
            author_email="'" + ', '.join(
                [author.email for author in config.authors]) + "'",
            dependencies='[]'))

    with open('MANIFEST.in', 'w') as fout:
        fout.write(MANIFEST_IN)

    shutil.copytree('../../src', 'src')
    shutil.copy('../../Package.toml', 'Package.toml')
    shutil.copy('../../README.rst', 'README.rst')
    run([sys.executable, 'setup.py', 'sdist'], f'Creating {archive}.', verbose)

def publish_upload_release_package(verbose, username, password, archive):
    # Try to hide the password.
    env = os.environ.copy()

    if username is None:
        username = input('Username: ')

    if password is None:
        password = getpass.getpass()

    env['TWINE_USERNAME'] = username
    env['TWINE_PASSWORD'] = password
    command = [sys.executable, '-m', 'twine', 'upload']

    if verbose:
        command += ['--verbose']

    command += glob.glob('dist/*')

    run(command, f'Uploading {archive}.', verbose, env=env)

def do_publish(_parser, args):
    config = read_package_configuration()

    print(f'┌───────────────────────────────────────────────────────── {INFO}  ─┐')
    print("│ Mys is currently using Python's Package Index (PyPI). A PyPI │")
    print("│ account is required to publish your package.                 │")
    print('└──────────────────────────────────────────────────────────────┘')

    publish_dir = 'build/publish'
    shutil.rmtree(publish_dir, ignore_errors=True)
    os.makedirs(publish_dir)
    path = os.getcwd()
    os.chdir(publish_dir)

    try:
        name = config['package']['name']
        version = config['package']['version']
        archive = f"mys-{name}-{version}.tar.gz"
        publish_create_release_package(config, args.verbose, archive)
        publish_upload_release_package(args.verbose,
                                       args.username,
                                       args.password,
                                       archive)
    finally:
        os.chdir(path)

def do_help(parser, _args):
    parser.print_help()

DESCRIPTION = f'''\
The Mys programming language package manager.

Available subcommands are:

    {cyan('new')}      Create a new package.
    {cyan('build')}    Build the appliaction.
    {cyan('run')}      Build and run the application.
    {cyan('clean')}    Remove build output.
    {cyan('lint')}     Perform static code analysis.
    {cyan('publish')}  Publish a release.
'''

def main():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--version',
                        action='version',
                        version=__version__,
                        help='Print version information and exit.')

    subparsers = parser.add_subparsers(dest='subcommand',
                                       help='Subcommand to execute.',
                                       metavar='subcommand')

    # The new subparser.
    subparser = subparsers.add_parser(
        'new',
        description='Create a new package.')
    subparser.add_argument(
        '--author',
        dest='authors',
        action='append',
        help=("Package author as 'Mys Lang <mys.lang@example.com>'. May "
              "be given multiple times."))
    subparser.add_argument('path')
    subparser.set_defaults(func=do_new)

    # The build subparser.
    subparser = subparsers.add_parser(
        'build',
        description='Build the appliaction.')
    subparser.add_argument('--verbose',
                           action='store_true',
                           help='Verbose output.')
    subparser.add_argument('-j', '--jobs',
                           type=int,
                           default=multiprocessing.cpu_count(),
                           help='Maximum number of parallel jobs (default: %(default)s).')
    subparser.add_argument('--local-registry',
                           help='Local registry path.')
    subparser.set_defaults(func=do_build)

    # The run subparser.
    subparser = subparsers.add_parser(
        'run',
        description='Build and run the application.')
    subparser.add_argument('--verbose',
                           action='store_true',
                           help='Verbose output.')
    subparser.add_argument('-j', '--jobs',
                           type=int,
                           default=multiprocessing.cpu_count(),
                           help='Maximum number of parallel jobs (default: %(default)s).')
    subparser.add_argument('--local-registry',
                           help='Local registry path.')
    subparser.add_argument('args', nargs='*')
    subparser.set_defaults(func=do_run)

    # The clean subparser.
    subparser = subparsers.add_parser(
        'clean',
        description='Remove build output.')
    subparser.set_defaults(func=do_clean)

    # The lint subparser.
    subparser = subparsers.add_parser(
        'lint',
        description='Perform static code analysis.')
    subparser.add_argument('-j', '--jobs',
                           type=int,
                           default=multiprocessing.cpu_count(),
                           help='Maximum number of parallel jobs (default: %(default)s).')
    subparser.set_defaults(func=do_lint)

    # The transpile subparser.
    subparser = subparsers.add_parser(
        'transpile',
        description='Transpile given Mys file to C++.')
    subparser.add_argument('-o', '--outdir',
                           default='.',
                           help='Output directory.')
    subparser.add_argument('mysfile')
    subparser.set_defaults(func=do_transpile)

    # The publish subparser.
    subparser = subparsers.add_parser(
        'publish',
        description='Publish a release.')
    subparser.add_argument('--verbose',
                           action='store_true',
                           help='Verbose output.')
    subparser.add_argument('-u', '--username',
                           help='Registry username.')
    subparser.add_argument('-p', '--password',
                           help='Registry password.')
    subparser.set_defaults(func=do_publish)

    # The help subparser.
    subparser = subparsers.add_parser(
        'help',
        description='Show this help.')
    subparser.set_defaults(func=do_help)

    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    try:
        args.func(parser, args)
    except Exception as e:
        sys.exit(str(e))
    except KeyboardInterrupt:
        print()
        sys.exit(1)
