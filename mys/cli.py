import time
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
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer
from humanfriendly import format_timespan

from .transpile import transpile
from .version import __version__

MYS_DIR = os.path.dirname(os.path.realpath(__file__))

BULB = yellow('💡', style='bold')
INFO = blue('🛈', style='bold')

PACKAGE_TOML_FMT = '''\
[package]
name = "{package_name}"
version = "0.1.0"
authors = [{authors}]

[dependencies]
# foobar = "*"
'''

README_FMT = '''\
{title}
{line}

Add more information about your package here!
'''

LIB_MYS = '''\
def add(first: int, second: int) -> int:
    return first + second

@test
def test_add():
    assert_eq(add(1, 2), 3)
'''

MAIN_MYS_FMT = '''\
def main():
    print('Hello, world!')
'''

MAKEFILE_FMT = '''\
CXX ?= g++
MYS ?= mys
CFLAGS += -I{mys_dir}/lib
CFLAGS += -Ibuild/transpiled/include
CFLAGS += -Wall
CFLAGS += -Wno-unused-variable
CFLAGS += -O3
CFLAGS += -std=c++17
CFLAGS += -fdata-sections
CFLAGS += -ffunction-sections
CFLAGS += -fdiagnostics-color=always
ifeq ($(TEST), yes)
CFLAGS += -DMYS_TEST
OBJ_SUFFIX = test.o
else
OBJ_SUFFIX = o
OBJ += build/transpiled/src/{package_name}/main.mys.o
endif
LDFLAGS += -std=c++17
LDFLAGS += -static
LDFLAGS += -Wl,--gc-sections
LDFLAGS += -fdiagnostics-color=always
{objs}
EXE = build/app
TEST_EXE = build/test

all: {all_deps}

test: $(TEST_EXE)

$(TEST_EXE): $(OBJ) build/mys.$(OBJ_SUFFIX)
\t$(CXX) $(LDFLAGS) -o $@ $^

$(EXE): $(OBJ) build/mys.$(OBJ_SUFFIX)
\t$(CXX) $(LDFLAGS) -o $@ $^

build/mys.$(OBJ_SUFFIX): {mys_dir}/lib/mys.cpp
\t$(CXX) $(CFLAGS) -c $^ -o $@

{transpile_rules}
%.mys.$(OBJ_SUFFIX): %.mys.cpp
\t$(CXX) $(CFLAGS) -c $^ -o $@
'''

TEST_MYS_FMT = '''\
{imports}

def main():
    passed: int = 0
    failed: int = 0
    total: int = 0
{tests}

    print('Passed:', passed)
    print('Failed:', failed)
    print('Total:', total)

    if failed > 0:
        raise Exception()
'''

TEST_FMT = '''\
    try:
        total += 1
        {test}()
        passed += 1
    except Exception as e:
        print(e)
        failed += 1
'''

TRANSPILE_RULE_FMT = '''\
{module_path}.cpp: {module_mys_path}
\t$(MYS) transpile -n {package_name} -p {package_path} {flags} -o build/transpiled {src}
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

def default_jobs():
    return max(1, multiprocessing.cpu_count() - 1)

def duration_start():
    return time.time()

def duration_stop(start_time):
    end_time = time.time()
    duration = format_timespan(end_time - start_time)

    return f' ({duration})'

class Spinner(yaspin.api.Yaspin):

    def __init__(self, text):
        super().__init__(text=text, color='yellow')
        self._start_time = duration_start()

    def __exit__(self, exc_type, exc_val, traceback):
        duration = duration_stop(self._start_time)

        if exc_type is None:
            self.write(green('✔ ') + self.text + duration)
        else:
            self.write(red('✘ ') + self.text + duration)

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
        start_time = duration_start()

        try:
            subprocess.run(command, check=True, env=env)
            print(green('✔ ') + message + duration_stop(start_time))
        except Exception:
            end_time = time.time()
            print(red('✘ ') + message + duration_stop(start_time))
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
    package_name = os.path.basename(args.path)
    authors = find_authors(args.authors)

    with Spinner(text=f"Creating package {package_name}"):
        os.makedirs(args.path)
        path = os.getcwd()
        os.chdir(args.path)

        try:
            with open('Package.toml', 'w') as fout:
                fout.write(PACKAGE_TOML_FMT.format(package_name=package_name,
                                                   authors=authors))

            with open('README.rst', 'w') as fout:
                fout.write(README_FMT.format(
                    title=package_name.replace('_', ' ').title(),
                    line='=' * len(package_name)))

            shutil.copyfile(os.path.join(MYS_DIR, 'lint/pylintrc'), 'pylintrc')
            os.mkdir('src')

            with open('src/lib.mys', 'w') as fout:
                fout.write(LIB_MYS)

            with open('src/main.mys', 'w') as fout:
                fout.write(MAIN_MYS_FMT.format(package_name=package_name))
        finally:
            os.chdir(path)

    cd = cyan(f'cd {package_name}')

    print(f'┌────────────────────────────────────────────────── {BULB} ─┐')
    print('│ Build and run the new package by typing:              │')
    print('│                                                       │')
    print(f'│ {cd}' + (51 - len(package_name)) * ' ' + '│')
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

def download_dependency_from_registry(verbose, name, version):
    archive = f'mys-{name}-{version}.tar.gz'
    path = f'build/dependencies/{archive}'
    download_directory = 'build/dependencies'

    if os.path.exists(path):
        return

    command = [
        sys.executable, '-m', 'pip', 'download',
        '-d', download_directory,
        f'mys-{name}=={version}'
    ]
    run(command, f"Downloading {archive}", verbose)

    with Spinner(text=f"Extracting {archive}."):
        with tarfile.open(path) as fin:
            fin.extractall('build/dependencies')

def download_dependencies(config, verbose):
    for name, info in config['dependencies'].items():
        if isinstance(info, str):
            download_dependency_from_registry(verbose, name, info)

def read_package_configuration():
    try:
        with Spinner('Reading package configuration'):
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

def find_package_sources(package_name, path, ignore_main=False):
    srcs = []
    oldpath = os.getcwd()
    os.chdir(os.path.join(path, 'src'))

    try:
        for src in glob.glob('**.mys', recursive=True):
            if ignore_main and src == 'main.mys':
                continue

            srcs.append((package_name, path, src, os.path.join(path, 'src', src)))
    finally:
        os.chdir(oldpath)

    return srcs

def find_dependency_sources(config):
    srcs = []

    for package_name, info in config['dependencies'].items():
        if isinstance(info, str):
            path = f'build/dependencies/mys-{package_name}-{info}/'
        elif 'path' in info:
            path = info['path']
        else:
            raise Exception('Bad dependency format.')

        srcs += find_package_sources(package_name, path, ignore_main=True)

    return srcs

def create_makefile(config):
    srcs = find_package_sources(config['package']['name'], '.')
    srcs += find_dependency_sources(config)

    transpile_rules = []
    objs = []
    is_application = False

    for package_name, package_path, src, path in srcs:
        flags = []

        if package_name != config['package']['name']:
            flags.append('-s')

        module_path = f'build/transpiled/src/{package_name}/{src}'
        transpile_rules.append(
            TRANSPILE_RULE_FMT.format(module_path=module_path,
                                      module_mys_path=path,
                                      package_name=package_name,
                                      package_path=package_path,
                                      src=src,
                                      flags=' '.join(flags)))

        if src == 'main.mys':
            is_application = True
        else:
            objs.append(f'OBJ += {module_path}.$(OBJ_SUFFIX)')

    if is_application:
        all_deps = '$(EXE)'
    else:
        all_deps = '$(OBJ) build/mys.o'

    with open('build/Makefile', 'w') as fout:
        fout.write(MAKEFILE_FMT.format(mys_dir=MYS_DIR,
                                       objs='\n'.join(objs),
                                       transpile_rules='\n'.join(transpile_rules),
                                       all_deps=all_deps,
                                       package_name=config['package']['name']))

    return is_application

def create_test_mk(config):
    srcs = find_package_sources(config['package']['name'],
                                'tests',
                                ignore_main=True)
    srcs += find_dependency_sources(config)

    transpile_rules = []
    objs = []

    for package_name, package_path, src, path in srcs:
        if src == 'main.mys':
            continue

        module_path = f'build/transpiled/src/{package_name}/{src}'
        transpile_rules.append(
            TRANSPILE_RULE_FMT.format(module_path=module_path,
                                      module_mys_path=path,
                                      package_name=package_name,
                                      package_path=package_path,
                                      src=src))
        objs.append(f'OBJ += {module_path}.o')

    with open('build/test.mk', 'w') as fout:
        fout.write(TEST_MK_FMT.format(mys_dir=MYS_DIR,
                                      objs='\n'.join(objs),
                                      transpile_rules='\n'.join(transpile_rules),
                                      test_files=''))

def build_prepare(verbose):
    config = read_package_configuration()

    if not os.path.exists('build/Makefile'):
        setup_build()

    download_dependencies(config, verbose)

    return create_makefile(config)

def build_app(verbose, jobs):
    is_application = build_prepare(verbose)
    command = ['make', '-f', 'build/Makefile', '-j', str(jobs), 'all']

    if not verbose:
        command += ['-s']

    run(command, 'Building', verbose)

    return is_application

def do_build(_parser, args):
    build_app(args.verbose, args.jobs)

def run_app(args, verbose):
    if verbose:
        print('./build/app')

    subprocess.run(['./build/app'] + args, check=True)

def style_source(code):
    return highlight(code,
                     PythonLexer(),
                     Terminal256Formatter(style='monokai')).rstrip()

def do_run(_parser, args):
    if build_app(args.verbose, args.jobs):
        run_app(args.args, args.verbose)
    else:
        main_1 = style_source('def main():\n')
        main_2 = style_source("    print('Hello, world!')\n")
        func = style_source('main()')
        print(f'┌────────────────────────────────────────────────────── {BULB} ─┐')
        print(f"│ This package is not executable. Create '{cyan('src/main.mys')}' and │")
        print(f"│ implement '{func}' to make the package executable.        │")
        print('│                                                           │')
        print(f'│ {main_1}                                               │')
        print(f"│ {main_2}                                │")
        print('└───────────────────────────────────────────────────────────┘')
        sys.exit(1)

def do_test(_parser, args):
    build_prepare(args.verbose)
    command = [
        'make', '-f', 'build/Makefile', '-j', str(args.jobs), 'test', 'TEST=yes'
    ]
    run(command, 'Building tests', args.verbose)
    run(['./build/test'], 'Running tests', args.verbose)

def do_clean(_parser, args):
    read_package_configuration()

    with Spinner(text='Cleaning'):
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
        with Spinner('Linting'):
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
    module_hpp = os.path.join(args.package_name, args.mysfile + '.hpp')
    hpp_path = os.path.join(args.outdir, 'include', module_hpp)
    cpp_path = os.path.join(args.outdir,
                            'src',
                            args.package_name,
                            args.mysfile + '.cpp')
    mys_path = os.path.join(args.package_path, 'src', args.mysfile)

    with open(mys_path) as fin:
        try:
            header, source = transpile(fin.read(),
                                       mys_path,
                                       module_hpp,
                                       args.skip_tests)
        except Exception as e:
            sys.exit(str(e))

    os.makedirs(os.path.dirname(hpp_path), exist_ok=True)
    os.makedirs(os.path.dirname(cpp_path), exist_ok=True)

    with open (hpp_path, 'w') as fout:
        fout.write(header)

    with open (cpp_path, 'w') as fout:
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
    run([sys.executable, 'setup.py', 'sdist'], f'Creating {archive}', verbose)

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

    run(command, f'Uploading {archive}', verbose, env=env)

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
    {cyan('test')}     Build and run tests
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
    subparser.add_argument('-v', '--verbose',
                           action='store_true',
                           help='Verbose output.')
    subparser.add_argument('-j', '--jobs',
                           type=int,
                           default=default_jobs(),
                           help='Maximum number of parallel jobs (default: %(default)s).')
    subparser.set_defaults(func=do_build)

    # The run subparser.
    subparser = subparsers.add_parser(
        'run',
        description='Build and run the application.')
    subparser.add_argument('-v', '--verbose',
                           action='store_true',
                           help='Verbose output.')
    subparser.add_argument('-j', '--jobs',
                           type=int,
                           default=default_jobs(),
                           help='Maximum number of parallel jobs (default: %(default)s).')
    subparser.add_argument('args', nargs='*')
    subparser.set_defaults(func=do_run)

    # The test subparser.
    subparser = subparsers.add_parser(
        'test',
        description='Build and run tests.')
    subparser.add_argument('-v', '--verbose',
                           action='store_true',
                           help='Verbose output.')
    subparser.add_argument('-j', '--jobs',
                           type=int,
                           default=default_jobs(),
                           help='Maximum number of parallel jobs (default: %(default)s).')
    subparser.set_defaults(func=do_test)

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
                           default=default_jobs(),
                           help='Maximum number of parallel jobs (default: %(default)s).')
    subparser.set_defaults(func=do_lint)

    # The transpile subparser.
    subparser = subparsers.add_parser(
        'transpile',
        description='Transpile given Mys file to C++ header and source files.')
    subparser.add_argument('-o', '--outdir',
                           default='.',
                           help='Output directory.')
    subparser.add_argument('-p', '--package-path',
                           required=True,
                           help='Package path.')
    subparser.add_argument('-n', '--package-name',
                           required=True,
                           help='Package name.')
    subparser.add_argument('-s', '--skip-tests',
                           action='store_true',
                           help='Skip tests.')
    subparser.add_argument('mysfile')
    subparser.set_defaults(func=do_transpile)

    # The publish subparser.
    subparser = subparsers.add_parser(
        'publish',
        description='Publish a release.')
    subparser.add_argument('-v', '--verbose',
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
