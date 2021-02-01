import glob
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time

import toml
import yaspin
from colors import blue
from colors import cyan
from colors import green
from colors import red
from colors import strip_color
from colors import yellow
from humanfriendly import format_timespan

from ..transpiler.utils import is_snake_case
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


def create_file(path, data):
    with open(path, 'w') as fout:
        fout.write(data)


def read_template_file(path):
    with open(os.path.join(MYS_DIR, 'cli/templates', path)) as fin:
        return fin.read()


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

    return output


def run(command, message, verbose, env=None):
    if verbose:
        start_time = duration_start()

        try:
            print('Command:', ' '.join(command))

            with subprocess.Popen(command,
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT,
                                  encoding='utf-8',
                                  close_fds=False,
                                  env=env) as proc:
                output = []

                while proc.poll() is None:
                    text = proc.stdout.readline()
                    print(text, end="")
                    output.append(text)

                print(proc.stdout.read(), end="")

                if proc.returncode != 0:
                    raise Exception(f'command failed with {proc.returncode}')

            output = ''.join(output)
            print(green(' ✔ ') + message + duration_stop(start_time))
        except Exception:
            print(red(' ✘ ') + message + duration_stop(start_time))
            raise
    else:
        output = run_with_spinner(command, message, env)

    return output


def create_file_from_template(path, dirictory, **kwargs):
    template = read_template_file(os.path.join(dirictory, path))
    create_file(path, template.format(**kwargs))


class Author:

    def __init__(self, name, email):
        self.name = name
        self.email = email


class PackageConfig:

    def __init__(self, path):
        self.authors = []
        self.config = self.load_package_configuration(path)

    def load_package_configuration(self, path):
        with open(os.path.join(path, 'package.toml')) as fin:
            config = toml.loads(fin.read())

        package = config.get('package')

        if package is None:
            raise Exception("'[package]' not found in package.toml.")

        for name in ['name', 'version', 'authors']:
            if name not in package:
                raise Exception(f"'[package].{name}' not found in package.toml.")

        if not is_snake_case(package['name']):
            raise Exception(
                f"package name must be snake case, got '{package['name']}'")

        for author in package['authors']:
            mo = re.match(r'^([^<]+)<([^>]+)>$', author)

            if not mo:
                raise Exception(f"Bad author '{author}'.")

            self.authors.append(Author(mo.group(1).strip(), mo.group(2).strip()))

        if 'description' not in package:
            package['description'] = ''

        dependencies = {
            'fiber': {'path': os.path.join(MYS_DIR, 'lib/packages/fiber')}
        }

        if 'dependencies' in config:
            dependencies.update(config['dependencies'])

        config['dependencies'] = dependencies

        if 'c-dependencies' not in config:
            config['c-dependencies'] = {}

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
            return PackageConfig('.')
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
    packages_paths = set()

    for package_name in config['dependencies']:
        path = dependency_path(package_name, config)
        srcs = find_package_sources(package_name, path, ignore_main=True)
        srcs_mys += srcs[0]
        srcs_hpp += srcs[1]
        srcs_cpp += srcs[2]
        packages_paths.add(path)

    return srcs_mys, srcs_hpp, srcs_cpp, sorted(packages_paths)


class PkgConfigFlags:

    def __init__(self):
        self.flags = []

    def add(self, output):
        # ToDo: Spaces in path.
        for flag in output.strip().split():
            if flag not in self.flags:
                self.flags.append(flag)

    def __str__(self):
        return ' '.join(self.flags)


def find_c_dependencies_flags(packages_paths, verbose, cflags, libs):
    if shutil.which('mys-config'):
        pkg_config = 'mys-config'
    elif shutil.which('pkg-config'):
        pkg_config = 'pkg-config'
    else:
        raise Exception('mys-config nor pkg-config found')

    for path in packages_paths:
        config = PackageConfig(path)

        for library_name in config['c-dependencies']:
            output = run([pkg_config, library_name, '--cflags'],
                         f'Getting compiler flags {library_name}',
                         verbose)
            cflags.add(output)
            output = run([pkg_config, library_name, '--libs'],
                         f'Getting linker flags for {library_name}',
                         verbose)
            libs.add(output)

def create_makefile(config, optimize, no_ccache, verbose):
    srcs_mys, srcs_hpp, srcs_cpp = find_package_sources(
        config['package']['name'],
        '.')
    cflags = PkgConfigFlags()
    libs = PkgConfigFlags()
    find_c_dependencies_flags(['.'], verbose, cflags, libs)

    if not srcs_mys:
        box_print(["'src/' is empty. Please create one or more .mys-files."], ERROR)

        raise Exception()

    srcs = find_dependency_sources(config)
    srcs_mys += srcs[0]
    srcs_hpp += srcs[1]
    srcs_cpp += srcs[2]
    packages_paths = srcs[3]

    transpile_options = []
    transpile_srcs = []
    transpile_srcs_paths = []
    copy_hpp_and_cpp = []
    objs = []
    is_application = False
    transpiled_cpp = []
    hpps = []
    find_c_dependencies_flags(packages_paths, verbose, cflags, libs)

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
                              transpiled_cpp='\n'.join(transpiled_cpp),
                              cflags=cflags,
                              libs=libs)

    return is_application


def build_prepare(verbose, optimize, no_ccache, config=None):
    if config is None:
        config = read_package_configuration()

    if not os.path.exists('build/Makefile'):
        setup_build()

    download_dependencies(config, verbose)

    return create_makefile(config, optimize, no_ccache, verbose)


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
