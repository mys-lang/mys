import argparse
import getpass
import glob
import json
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time
from tempfile import TemporaryDirectory
from traceback import print_exc

import toml
import yaspin
from colors import blue
from colors import cyan
from colors import green
from colors import red
from colors import strip_color
from colors import yellow
from humanfriendly import format_timespan
from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer

from ..transpiler import Source
from ..transpiler import transpile
from ..version import __version__

MYS_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

DOWNLOAD_DIRECTORY = 'build/dependencies'

BULB = yellow('💡', style='bold')
INFO = blue('🛈 ', style='bold')
ERROR = red('❌️', style='bold')

OPTIMIZE = {
    'speed': '3',
    'size': 's',
    'debug': '0'
}

TRANSPILE_OPTIONS_FMT = '-n {package_name} -p {package_path} {flags}'

COPY_HPP_AND_CPP_FMT = '''\
{dst}: {src}
\tmkdir -p $(dir $@)
\tcp $< $@
'''

class BadPackageNameError(Exception):
    pass


def create_file(path, data):
    with open(path, 'w') as fout:
        fout.write(data)


def read_template_file(path):
    with open(os.path.join(MYS_DIR, 'cli/templates', path)) as fin:
        return fin.read()


def find_config_file():
    path = os.getenv('MYS_CONFIG')
    config_dir = os.path.expanduser('~/.config/mys')
    config_path = os.path.join(config_dir, 'config.toml')

    if path is not None:
        return path

    if not os.path.exists(config_path):
        os.makedirs(config_dir, exist_ok=True)
        create_file(config_path, '')

    return config_path


def load_mys_config():
    """Mys tool configuration.

    Add validation when needed.

    """

    path = find_config_file()

    try:
        with open(path) as fin:
            return toml.loads(fin.read())
    except toml.decoder.TomlDecodeError:
        raise Exception(f"failed to load Mys configuration file '{path}'")


def default_jobs():
    return max(1, multiprocessing.cpu_count() - 1)


def duration_start():
    return time.time()


def duration_stop(start_time):
    end_time = time.time()
    duration = format_timespan(end_time - start_time)

    return f' ({duration})'


def box_print(lines, icon, width=None):
    if width is None:
        width = 0

        for line in lines:
            width = max(width, len(strip_color(line)))

    print(f'┌{"─" * (width - 3)} {icon} ─┐')

    for line in lines:
        padding = width - len(strip_color(line))
        print(f'│ {line}{" " * padding} │')

    print(f'└{"─" * (width + 2)}┘')


SPINNER = [
    ' ⠋', ' ⠙', ' ⠹', ' ⠸', ' ⠼', ' ⠴', ' ⠦', ' ⠧', ' ⠇', ' ⠏'
]


class Spinner(yaspin.api.Yaspin):

    def __init__(self, text):
        super().__init__(yaspin.Spinner(SPINNER, 80), text=text, color='yellow')
        self._start_time = duration_start()

    def __exit__(self, exc_type, exc_val, traceback):
        duration = duration_stop(self._start_time)

        if exc_type is None:
            self.write(green(' ✔ ') + self.text + duration)
        else:
            self.write(red(' ✘ ') + self.text + duration)

        return super().__exit__(exc_type, exc_val, traceback)


def run_with_spinner(command, message, env=None):
    output = ''

    try:
        with Spinner(text=message):
            result = subprocess.run(command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    encoding='utf-8',
                                    close_fds=False,
                                    env=env)
            output = result.stdout
            result.check_returncode()
    except Exception:
        lines = []

        for line in output.splitlines():
            if 'make: *** ' in line:
                continue

            lines.append(line)

        raise Exception('\n'.join(lines).rstrip())


def run(command, message, verbose, env=None):
    if verbose:
        start_time = duration_start()

        try:
            print('Command:', ' '.join(command))
            subprocess.run(command, check=True, close_fds=False, env=env)
            print(green(' ✔ ') + message + duration_stop(start_time))
        except Exception:
            print(red(' ✘ ') + message + duration_stop(start_time))
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


def validate_package_name(package_name):
    if not re.match(r'^[a-z][a-z0-9_]*$', package_name):
        raise BadPackageNameError()


def create_file_from_template(path, dirictory, **kwargs):
    template = read_template_file(os.path.join(dirictory, path))
    create_file(path, template.format(**kwargs))


def create_new_file(path, **kwargs):
    create_file_from_template(path, 'new', **kwargs)


def do_new(_parser, args, _mys_config):
    package_name = os.path.basename(args.path)
    authors = find_authors(args.authors)

    try:
        with Spinner(text=f"Creating package {package_name}"):
            validate_package_name(package_name)

            os.makedirs(args.path)
            path = os.getcwd()
            os.chdir(args.path)

            try:
                create_new_file('package.toml',
                                package_name=package_name,
                                authors=authors)
                create_new_file('.gitignore')
                create_new_file('.gitattributes')
                create_new_file('README.rst',
                                package_name=package_name,
                                title=package_name.replace('_', ' ').title(),
                                line='=' * len(package_name))
                create_new_file('LICENSE')
                shutil.copyfile(os.path.join(MYS_DIR, 'cli/templates/new/pylintrc'),
                                'pylintrc')
                os.mkdir('src')
                create_new_file('src/lib.mys')
                create_new_file('src/main.mys')
            finally:
                os.chdir(path)
    except BadPackageNameError:
        box_print(['Package names must start with a letter and only',
                   'contain letters, numbers and underscores. Only lower',
                   'case letters are allowed.',
                   '',
                   'Here are a few examples:',
                   '',
                   f'{cyan("mys new foo")}'
                   f'{cyan("mys new f1")}'
                   f'{cyan("mys new foo_bar")}'],
                  ERROR)
        raise Exception()

    cd = cyan(f'cd {package_name}')

    box_print(['Build and run the new package by typing:',
               '',
               f'{cd}',
               f'{cyan("mys run")}'],
              BULB,
              width=53)


class Author:

    def __init__(self, name, email):
        self.name = name
        self.email = email


class PackageConfig:

    def __init__(self):
        self.authors = []
        self.config = self.load_package_configuration()

    def load_package_configuration(self):
        with open('package.toml') as fin:
            config = toml.loads(fin.read())

        package = config.get('package')

        if package is None:
            raise Exception("'[package]' not found in package.toml.")

        for name in ['name', 'version', 'authors']:
            if name not in package:
                raise Exception(f"'[package].{name}' not found in package.toml.")

        for author in package['authors']:
            mo = re.match(r'^([^<]+)<([^>]+)>$', author)

            if not mo:
                raise Exception(f"Bad author '{author}'.")

            self.authors.append(Author(mo.group(1).strip(), mo.group(2).strip()))

        if 'description' not in package:
            package['description'] = ''

        if 'dependencies' not in config:
            config['dependencies'] = {}

        return config

    def __getitem__(self, key):
        return self.config[key]


def setup_build():
    os.makedirs('build/cpp', exist_ok=True)
    os.makedirs('build/dependencies', exist_ok=True)


def rename_one_matching(pattern, to):
    paths = glob.glob(pattern)

    if len(paths) != 1:
        raise Exception(
            f'{len(paths)} paths are matching when expecting exactly one to match')

    os.rename(paths[0], to)


def prepare_download_dependency_from_registry(name, version):
    if version == '*':
        archive = f'mys-{name}-latest.tar.gz'
        package_specifier = f'mys-{name}'
    else:
        archive = f'mys-{name}-{version}.tar.gz'
        package_specifier = f'mys-{name}=={version}'

    archive_path = f'build/dependencies/{archive}'

    if os.path.exists(archive_path):
        return None
    else:
        return (name, version, package_specifier, archive, archive_path)


def extract_dependency(name, version, archive, archive_path):
    if version == '*':
        rename_one_matching(os.path.join(DOWNLOAD_DIRECTORY, f'mys-{name}-*.tar.gz'),
                            archive_path)

    with Spinner(text=f"Extracting {archive}"):
        with tarfile.open(archive_path) as fin:
            fin.extractall(DOWNLOAD_DIRECTORY)

    if version == '*':
        rename_one_matching(os.path.join(DOWNLOAD_DIRECTORY, f'mys-{name}-*/'),
                            os.path.join(DOWNLOAD_DIRECTORY, f'mys-{name}-latest'))


def download_dependencies(config, verbose):
    packages = []

    for name, info in config['dependencies'].items():
        if isinstance(info, str):
            package = prepare_download_dependency_from_registry(name, info)

            if package is not None:
                packages.append(package)

    if not packages:
        return

    command = [
        sys.executable, '-m', 'pip', 'download',
        '-d', DOWNLOAD_DIRECTORY
    ]
    command += [package_specifier for _, _, package_specifier, _, _ in packages]
    run(command, 'Downloading dependencies', verbose)

    for name, version, _, archive, archive_path in packages:
        extract_dependency(name, version, archive, archive_path)

def read_package_configuration():
    try:
        with Spinner('Reading package configuration'):
            return PackageConfig()
    except FileNotFoundError:
        box_print([
            'Current directory does not contain a Mys package (package.toml does',
            'not exist).',
            '',
            'Please enter a Mys package directory, and try again.',
            '',
            f'You can create a new package with {cyan("mys new <name>")}.'],
                  BULB)

        raise Exception()


def find_package_sources(package_name, path, ignore_main=False):
    srcs_mys = []
    srcs_hpp = []
    srcs_cpp = []
    oldpath = os.getcwd()
    os.chdir(os.path.join(path, 'src'))

    try:
        for src in glob.glob('**/*.mys', recursive=True):
            if ignore_main and src == 'main.mys':
                continue

            srcs_mys.append((package_name, path, src, os.path.join(path, 'src', src)))

        for src in glob.glob('**/*.hpp', recursive=True):
            srcs_hpp.append((package_name, path, src, os.path.join(path, 'src', src)))

        for src in glob.glob('**/*.cpp', recursive=True):
            srcs_cpp.append((package_name, path, src, os.path.join(path, 'src', src)))
    finally:
        os.chdir(oldpath)

    return srcs_mys, srcs_hpp, srcs_cpp


def dependency_path(dependency_name, config):
    for package_name, info in config['dependencies'].items():
        if package_name == dependency_name:
            if isinstance(info, str):
                if info == '*':
                    return f'build/dependencies/mys-{package_name}-latest/'
                else:
                    return f'build/dependencies/mys-{package_name}-{info}/'
            elif 'path' in info:
                return info['path']
            else:
                raise Exception('Bad dependency format.')

    raise Exception(f'Bad dependency {dependency_name}.')


def find_dependency_sources(config):
    srcs_mys = []
    srcs_hpp = []
    srcs_cpp = []

    for package_name in config['dependencies']:
        path = dependency_path(package_name, config)
        srcs = find_package_sources(package_name, path, ignore_main=True)
        srcs_mys += srcs[0]
        srcs_hpp += srcs[1]
        srcs_cpp += srcs[2]

    return srcs_mys, srcs_hpp, srcs_cpp


def create_makefile(config, optimize, no_ccache):
    srcs_mys, srcs_hpp, srcs_cpp = find_package_sources(
        config['package']['name'],
        '.')

    if not srcs_mys:
        box_print(["'src/' is empty. Please create one or more .mys-files."], ERROR)

        raise Exception()

    srcs = find_dependency_sources(config)
    srcs_mys += srcs[0]
    srcs_hpp += srcs[1]
    srcs_cpp += srcs[2]

    transpile_options = []
    transpile_srcs = []
    transpile_srcs_paths = []
    copy_hpp_and_cpp = []
    objs = []
    is_application = False
    transpiled_cpp = []
    hpps = []

    for package_name, package_path, src, _path in srcs_mys:
        flags = []

        if package_name != config['package']['name']:
            flags.append('-s yes')
        else:
            flags.append('-s no')

        if src == 'main.mys':
            is_application = True
            flags.append('-m yes')
        else:
            flags.append('-m no')

        flags = ' '.join(flags)

        module_path = f'build/cpp/src/{package_name}/{src}'
        transpile_options.append(
            TRANSPILE_OPTIONS_FMT.format(package_name=package_name,
                                         package_path=package_path,
                                         flags=flags))

        transpile_srcs.append(src)
        transpile_srcs_paths.append(os.path.join(package_path, 'src', src))
        objs.append(f'OBJ += {module_path}.$(OBJ_SUFFIX)')
        transpiled_cpp.append(f'SRC += {module_path}.cpp')

    for package_name, package_path, src, _path in srcs_hpp:
        src_path = os.path.join(package_path, 'src', src)
        module_path = f'build/cpp/src/{package_name}/{src}'
        copy_hpp_and_cpp.append(COPY_HPP_AND_CPP_FMT.format(src=src_path,
                                                            dst=module_path))
        hpps.append(module_path)

    for package_name, package_path, src, _path in srcs_cpp:
        src_path = os.path.join(package_path, 'src', src)
        module_path = f'build/cpp/src/{package_name}/{src}'
        copy_hpp_and_cpp.append(COPY_HPP_AND_CPP_FMT.format(src=src_path,
                                                            dst=module_path))
        objs.append(f'OBJ += {module_path}.o')
        transpiled_cpp.append(f'SRC += {module_path}.cpp')

    if is_application:
        all_deps = '$(EXE)'
    else:
        all_deps = '$(OBJ)'

    if not no_ccache and shutil.which('ccache'):
        ccache = 'ccache '
    else:
        ccache = ''

    create_file_from_template('build/Makefile',
                              '',
                              mys_dir=MYS_DIR,
                              mys=f'{sys.executable} -m mys',
                              ccache=ccache,
                              objs='\n'.join(objs),
                              optimize=OPTIMIZE[optimize],
                              transpile_options=' '.join(transpile_options),
                              transpile_srcs_paths=' '.join(transpile_srcs_paths),
                              transpile_srcs=' '.join(transpile_srcs),
                              hpps=' '.join(hpps),
                              copy_hpp_and_cpp='\n'.join(copy_hpp_and_cpp),
                              all_deps=all_deps,
                              package_name=config['package']['name'],
                              transpiled_cpp='\n'.join(transpiled_cpp))

    return is_application


def build_prepare(verbose, optimize, no_ccache, config=None):
    if config is None:
        config = read_package_configuration()

    if not os.path.exists('build/Makefile'):
        setup_build()

    download_dependencies(config, verbose)

    return create_makefile(config, optimize, no_ccache)


def build_app(debug, verbose, jobs, is_application):
    command = ['make', '-f', 'build/Makefile', 'all']

    if os.getenv('MAKEFLAGS') is None:
        command += ['-j', str(jobs)]

    if debug:
        command += ['TRANSPILE_DEBUG=--debug']

    if not verbose:
        command += ['-s']

    if is_application:
        command += ['APPLICATION=yes']

    run(command, 'Building', verbose)


def do_build(_parser, args, _mys_config):
    is_application = build_prepare(args.verbose, args.optimize, args.no_ccache)
    build_app(args.debug, args.verbose, args.jobs, is_application)


def run_app(args, verbose):
    if verbose:
        print('./build/app')

    subprocess.run(['./build/app'] + args, check=True)


def style_source(code):
    return highlight(code,
                     PythonLexer(),
                     Terminal256Formatter(style='monokai')).rstrip()


def do_run(_parser, args, _mys_config):
    if build_prepare(args.verbose, args.optimize, args.no_ccache):
        build_app(args.debug, args.verbose, args.jobs, True)
        run_app(args.args, args.verbose)
    else:
        main_1 = style_source('def main():\n')
        main_2 = style_source("    print('Hello, world!')\n")
        func = style_source('main()')
        box_print([
            f"This package is not executable. Create '{cyan('src/main.mys')}' and",
            f"implement '{func}' to make the package executable.",
            '',
            main_1,
            main_2], BULB)

        raise Exception()


def do_test(_parser, args, _mys_config):
    build_prepare(args.verbose, args.optimize, args.no_ccache)

    command = [
        'make', '-f', 'build/Makefile', 'test', 'TEST=yes'
    ]

    if os.getenv('MAKEFLAGS') is None:
        command += ['-j', str(args.jobs)]

    if args.debug:
        command += ['TRANSPILE_DEBUG=--debug']

    run(command, 'Building tests', args.verbose)
    run(['./build/test'], 'Running tests', args.verbose)


def do_clean(_parser, _args, _mys_config):
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


def do_transpile(_parser, args, _mys_config):
    sources = []

    for i, mysfile in enumerate(args.mysfiles):
        mys_path = os.path.join(args.package_path[i], 'src', mysfile)
        module_hpp = os.path.join(args.package_name[i], mysfile + '.hpp')
        module = '.'.join(module_hpp[:-8].split('/'))
        hpp_path = os.path.join(args.outdir, 'include', module_hpp)
        cpp_path = os.path.join(args.outdir,
                                'src',
                                args.package_name[i],
                                mysfile + '.cpp')

        with open(mys_path, 'r') as fin:
            sources.append(Source(fin.read(),
                                  mysfile,
                                  module,
                                  mys_path,
                                  module_hpp,
                                  args.skip_tests[i] == 'yes',
                                  hpp_path,
                                  cpp_path,
                                  args.main[i] == 'yes'))

    generated = transpile(sources)

    for source, (hpp_1_code, hpp_2_code, cpp_code) in zip(sources, generated):
        os.makedirs(os.path.dirname(source.hpp_path), exist_ok=True)
        os.makedirs(os.path.dirname(source.cpp_path), exist_ok=True)
        create_file(source.hpp_path[:-3] + 'early.hpp', hpp_1_code)
        create_file(source.hpp_path, hpp_2_code)
        create_file(source.cpp_path, cpp_code)


def publish_create_release_package(config, verbose, archive):
    create_file_from_template('setup.py',
                              'publish',
                              name=f"mys-{config['package']['name']}",
                              version=config['package']['version'],
                              description=config['package']['description'],
                              author="'" + ', '.join(
                                  [author.name for author in config.authors]) + "'",
                              author_email="'" + ', '.join(
                                  [author.email for author in config.authors]) + "'",
                              dependencies='[]')
    create_file_from_template('MANIFEST.in', 'publish')
    shutil.copytree('../../src', 'src')
    shutil.copy('../../package.toml', 'package.toml')
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


def do_publish(_parser, args, _mys_config):
    config = read_package_configuration()

    box_print([
        "Mys is currently using Python's Package Index (PyPI). A PyPI",
        'account is required to publish your package.'], INFO)

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


def install_clean():
    if not os.path.exists('package.toml'):
        raise Exception('not a package')

    with Spinner(text='Cleaning'):
        shutil.rmtree('build', ignore_errors=True)

def install_download(args):
    command = [
        sys.executable, '-m', 'pip', 'download', f'mys-{args.package}'
    ]
    run(command, 'Downloading package', args.verbose)


def install_extract():
    archive = glob.glob('mys-*.tar.gz')[0]

    with Spinner(text='Extracting package'):
        with tarfile.open(archive) as fin:
            fin.extractall()

    os.remove(archive)


def install_build(args):
    config = read_package_configuration()
    is_application = build_prepare(args.verbose, 'speed', args.no_ccache, config)

    if not is_application:
        box_print(['There is no application to build in this package (src/main.mys ',
                   'missing).'],
                  ERROR)

        raise Exception()

    build_app(args.debug, args.verbose, args.jobs, is_application)

    return config

def install_install(root, _args, config):
    bin_dir = os.path.join(root, 'bin')
    bin_name = config['package']['name']
    src_file = 'build/app'
    dst_file = os.path.join(bin_dir, bin_name)

    with Spinner(text=f"Installing {bin_name} in {bin_dir}"):
        os.makedirs(bin_dir, exist_ok=True)
        shutil.copyfile(src_file, dst_file)
        shutil.copymode(src_file, dst_file)


def install_from_current_dirctory(args, root):
    install_clean()
    config = install_build(args)
    install_install(root, args, config)


def install_from_registry(args, root):
    with TemporaryDirectory()as tmp_dir:
        os.chdir(tmp_dir)
        install_download(args)
        install_extract()
        os.chdir(glob.glob('mys-*')[0])
        config = install_build(args)
        install_install(root, args, config)


def do_install(_parser, args, _mys_config):
    root = os.path.abspath(os.path.expanduser(args.root))

    if args.package is None:
        install_from_current_dirctory(args, root)
    else:
        install_from_registry(args, root)


def do_style(_parser, _args, _mys_config):
    read_package_configuration()

    box_print(['This subcommand is not yet implemented.'], ERROR)

    raise Exception()


def do_help(parser, _args, _mys_config):
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
    {cyan('install')}  Install an application from local package or registry.'
'''


def add_verbose_argument(subparser):
    subparser.add_argument('-v', '--verbose',
                           action='store_true',
                           help='Verbose output.')


def add_jobs_argument(subparser):
    subparser.add_argument(
        '-j', '--jobs',
        type=int,
        default=default_jobs(),
        help='Maximum number of parallel jobs (default: %(default)s).')


def add_optimize_argument(subparser, default):
    subparser.add_argument(
        '-o', '--optimize',
        default=default,
        choices=['speed', 'size', 'debug'],
        help='Optimize the build for given level (default: %(default)s).')


def add_no_ccache_argument(subparser):
    subparser.add_argument('-n', '--no-ccache',
                           action='store_true',
                           help='Do not use ccache.')


def create_parser():
    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('--config', help='Configuration file to use.')
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
    add_verbose_argument(subparser)
    add_jobs_argument(subparser)
    add_optimize_argument(subparser, 'speed')
    add_no_ccache_argument(subparser)
    subparser.set_defaults(func=do_build)

    # The run subparser.
    subparser = subparsers.add_parser(
        'run',
        description='Build and run the application.')
    add_verbose_argument(subparser)
    add_jobs_argument(subparser)
    add_optimize_argument(subparser, 'speed')
    add_no_ccache_argument(subparser)
    subparser.add_argument('args', nargs='*')
    subparser.set_defaults(func=do_run)

    # The test subparser.
    subparser = subparsers.add_parser(
        'test',
        description='Build and run tests.')
    add_verbose_argument(subparser)
    add_jobs_argument(subparser)
    add_optimize_argument(subparser, 'debug')
    add_no_ccache_argument(subparser)
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
    add_jobs_argument(subparser)
    subparser.set_defaults(func=do_lint)

    # The transpile subparser.
    subparser = subparsers.add_parser(
        'transpile',
        description='Transpile given Mys file(s) to C++ header and source files.')
    subparser.add_argument('-o', '--outdir',
                           default='.',
                           help='Output directory.')
    subparser.add_argument('-p', '--package-path',
                           required=True,
                           action='append',
                           help='Package path.')
    subparser.add_argument('-n', '--package-name',
                           required=True,
                           action='append',
                           help='Package name.')
    subparser.add_argument('-s', '--skip-tests',
                           action='append',
                           choices=['yes', 'no'],
                           help='Skip tests.')
    subparser.add_argument('-m', '--main',
                           action='append',
                           choices=['yes', 'no'],
                           help='Contains main().')
    subparser.add_argument('mysfiles', nargs='+')
    subparser.set_defaults(func=do_transpile)

    # The publish subparser.
    subparser = subparsers.add_parser(
        'publish',
        description='Publish a release.')
    add_verbose_argument(subparser)
    subparser.add_argument('-u', '--username',
                           help='Registry username.')
    subparser.add_argument('-p', '--password',
                           help='Registry password.')
    subparser.set_defaults(func=do_publish)

    # The install subparser.
    subparser = subparsers.add_parser(
        'install',
        description='Install an application from local package or registry.')
    add_verbose_argument(subparser)
    add_jobs_argument(subparser)
    add_no_ccache_argument(subparser)
    subparser.add_argument('--root',
                           default='~/.local',
                           help='Root folder to install into (default: %(default)s.')
    subparser.add_argument(
        'package',
        nargs='?',
        help=('Package to install application from. Installs current package if '
              'not given.'))
    subparser.set_defaults(func=do_install)

    # The style subparser.
    subparser = subparsers.add_parser(
        'style',
        description=(
            'Check that the package follows the Mys style guidelines. Automatically '
            'fixes trivial errors and prints the rest.'))
    subparser.set_defaults(func=do_style)

    # The help subparser.
    subparser = subparsers.add_parser(
        'help',
        description='Show this help.')
    subparser.set_defaults(func=do_help)

    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    try:
        args.func(parser, args, load_mys_config())
    except Exception as e:
        if args.debug:
            print_exc()

        sys.exit(str(e))
    except KeyboardInterrupt:
        print()

        if args.debug:
            raise

        sys.exit(1)
