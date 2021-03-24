import glob
import multiprocessing
import os
import re
import shutil
import subprocess
import sys
import tarfile
import time

import requests
import toml
import yaspin
from colors import blue
from colors import cyan
from colors import green
from colors import red
from colors import strip_color
from colors import yellow
from humanfriendly import format_timespan

from ..coverage import Coverage
from ..coverage import CoverageData
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

COPY_ASSET_FMT = '''\
{dst}: {src}
\tmkdir -p $(dir $@)
\tcp $< $@
'''

class BuildConfig:

    def __init__(self,
                 debug,
                 verbose,
                 optimize,
                 debug_symbols,
                 no_ccache,
                 coverage,
                 unsafe,
                 jobs):
        self.debug = debug
        self.verbose = verbose
        self.optimize = optimize
        self.debug_symbols = debug_symbols
        self.no_ccache = no_ccache
        self.coverage = coverage
        self.unsafe = unsafe
        self.jobs = jobs

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


def create_file_from_template(path, directory, **kwargs):
    template = read_template_file(os.path.join(directory, path))
    create_file(path, template.format(**kwargs))


def create_file_from_template_2(path, template_path, **kwargs):
    template = read_template_file(template_path)
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
    os.makedirs('build/dependencies', exist_ok=True)


def rename_one_matching(pattern, to):
    paths = glob.glob(pattern)

    if len(paths) != 1:
        raise Exception(
            f'{len(paths)} paths are matching when expecting exactly one to match')

    os.rename(paths[0], to)


def prepare_download_dependency_from_registry(name, version):
    archive = f'{name}-{version}.tar.gz'
    archive_path = f'build/dependencies/{archive}'

    if os.path.exists(archive_path):
        return None
    else:
        return (name, version, archive, archive_path)


def extract_dependency(name, version, archive, archive_path):
    if version == 'latest':
        rename_one_matching(os.path.join(DOWNLOAD_DIRECTORY, f'{name}-*.tar.gz'),
                            archive_path)

    with Spinner(text=f"Extracting {archive}"):
        with tarfile.open(archive_path) as fin:
            fin.extractall(DOWNLOAD_DIRECTORY)

    if version == 'latest':
        rename_one_matching(os.path.join(DOWNLOAD_DIRECTORY, f'{name}-*/'),
                            os.path.join(DOWNLOAD_DIRECTORY, f'{name}-latest'))


def download_dependencies(config):
    packages = []

    for name, info in config['dependencies'].items():
        if isinstance(info, str):
            package = prepare_download_dependency_from_registry(name, info)

            if package is not None:
                packages.append(package)

    if not packages:
        return

    with Spinner(text="Downloading dependencies"):
        for _, _, archive, archive_path in packages:
            response = requests.get(f'https://mys-lang.org/package/{archive}')

            if response.status_code != 200:
                print(response.text)

                raise Exception('Package download failed.')

            with open(archive_path, 'wb') as fout:
                fout.write(response.content)

    for name, version, archive, archive_path in packages:
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
                return f'build/dependencies/{package_name}-{info}/'
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


def find_assets(config):
    assets = []
    paths = [(config['package']['name'], '.')]

    for package_name in config['dependencies']:
        paths.append((package_name, dependency_path(package_name, config)))

    for package_name, path in paths:
        oldpath = os.getcwd()
        assets_path = os.path.join(path, 'assets')

        if not os.path.exists(assets_path):
            continue

        os.chdir(assets_path)

        try:
            for asset in glob.glob('**/*', recursive=True):
                if os.path.isfile(asset):
                    assets.append((package_name, assets_path, asset))
        finally:
            os.chdir(oldpath)

    return assets


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


def create_makefile(config, build_config):
    combo = build_config.optimize

    if build_config.coverage:
        combo += '-coverage'

    if build_config.unsafe:
        combo += '-unsafe'

    build_dir = f'build/{combo}'

    os.makedirs(f'{build_dir}/cpp', exist_ok=True)
    srcs_mys, srcs_hpp, srcs_cpp = find_package_sources(
        config['package']['name'],
        '.')
    cflags = PkgConfigFlags()
    libs = PkgConfigFlags()
    find_c_dependencies_flags(['.'], build_config.verbose, cflags, libs)

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
    find_c_dependencies_flags(packages_paths, build_config.verbose, cflags, libs)

    if build_config.debug_symbols:
        cflags.flags.append('-g')

    assets = find_assets(config)

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

        module_path = f'$(BUILD)/cpp/src/{package_name}/{src}'
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
        module_path = f'$(BUILD)/cpp/src/{package_name}/{src}'
        copy_hpp_and_cpp.append(COPY_HPP_AND_CPP_FMT.format(src=src_path,
                                                            dst=module_path))
        hpps.append(module_path)

    for package_name, package_path, src, _path in srcs_cpp:
        src_path = os.path.join(package_path, 'src', src)
        module_path = f'$(BUILD)/cpp/src/{package_name}/{src}'
        copy_hpp_and_cpp.append(COPY_HPP_AND_CPP_FMT.format(src=src_path,
                                                            dst=module_path))
        objs.append(f'OBJ += {module_path}.o')
        transpiled_cpp.append(f'SRC += {module_path}.cpp')

    copy_assets = []
    assets_targets = []

    for package_name, assets_path, asset in assets:
        target = os.path.join(f'$(EXE)-assets/{package_name}', asset)
        copy_assets.append(
            COPY_ASSET_FMT.format(src=os.path.join(assets_path, asset),
                                  dst=target))
        assets_targets.append(target)

    if is_application:
        all_deps = '$(EXE)'
    else:
        all_deps = '$(OBJ)'

    if not build_config.no_ccache and shutil.which('ccache'):
        ccache = 'ccache '
    else:
        ccache = ''

    create_file_from_template_2(f'{build_dir}/Makefile',
                                'build/Makefile',
                                build=build_dir,
                                mys_dir=MYS_DIR,
                                mys=f'{sys.executable} -m mys',
                                ccache=ccache,
                                objs='\n'.join(objs),
                                optimize=OPTIMIZE[build_config.optimize],
                                transpile_options=' '.join(transpile_options),
                                transpile_srcs_paths=' '.join(transpile_srcs_paths),
                                transpile_srcs=' '.join(transpile_srcs),
                                hpps=' '.join(hpps),
                                copy_hpp_and_cpp='\n'.join(copy_hpp_and_cpp),
                                copy_assets='\n'.join(copy_assets),
                                assets=' '.join(assets_targets),
                                all_deps=all_deps,
                                package_name=config['package']['name'],
                                transpiled_cpp='\n'.join(transpiled_cpp),
                                cflags=cflags,
                                libs=libs)

    return is_application, build_dir


def build_prepare(build_config, config=None):
    if config is None:
        config = read_package_configuration()

    setup_build()
    download_dependencies(config)

    return create_makefile(config, build_config)


def build_app(build_config, is_application, build_dir):
    command = ['make', '-f', f'{build_dir}/Makefile', 'all']

    if os.getenv('MAKEFLAGS') is None:
        command += ['-j', str(build_config.jobs)]

    if build_config.debug:
        command += ['TRANSPILE_DEBUG=--debug']

    if not build_config.verbose:
        command += ['-s']

    if is_application:
        command += ['APPLICATION=yes']

    if build_config.coverage:
        command += ['COVERAGE=yes']

    if build_config.unsafe:
        command += ['UNSAFE=yes']

    if build_config.optimize == 'debug':
        command += ['TRACEBACK=yes']

    run(command, 'Building', build_config.verbose)


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


def add_debug_symbols_argument(subparser):
    subparser.add_argument('-g', '--debug-symbols',
                           action='store_true',
                           help='Add debug symbols.')


def add_no_ccache_argument(subparser):
    subparser.add_argument('-n', '--no-ccache',
                           action='store_true',
                           help='Do not use ccache.')


def add_coverage_argument(subparser):
    subparser.add_argument(
        '-c', '--coverage',
        action='store_true',
        help=('Instrument the code and create a coverage report when the '
              'application exits gracefully.'))


def add_unsafe_argument(subparser):
    subparser.add_argument(
        '-u', '--unsafe',
        action='store_true',
        help='Less runtime checks in favour of better performance.')


def _add_lines(coverage_data, path, linenos):
    coverage_data.add_lines(
        {path: {lineno: None for lineno in linenos}})


def _create_coverage_report(include):
    coverage_data = CoverageData()

    with open('.mys-coverage.txt', 'r') as fin:
        path = None
        linenos = []

        for line in fin:
            line = line.strip()

            if line.startswith('File:'):
                if path is not None:
                    _add_lines(coverage_data, path, linenos)

                path = os.path.abspath(line[6:])
                linenos = []
            else:
                lineno, count = line.split()

                if int(count) > 0:
                    linenos.append(int(lineno))

        if path is not None:
            _add_lines(coverage_data, path, linenos)

    coverage_data.write()

    cov = Coverage('.coverage', auto_data=True, include=include)
    cov.start()
    cov.stop()
    cov.html_report(directory='coverage/html')


def create_coverage_report(include=None):
    with Spinner('Creating code coverage report'):
        _create_coverage_report(include)

    path = os.path.abspath('coverage/html/index.html')
    print(f'Coverage report: {path}')
