import glob
import multiprocessing
import os
import shutil
import sys

from colors import blue
from colors import cyan
from colors import red
from colors import strip_color
from colors import yellow

from ..coverage import Coverage
from ..coverage import CoverageData
from .mys_dir import MYS_DIR
from .package_config import PackageConfig
from .packages_finder import DOWNLOAD_DIRECTORY
from .packages_finder import download_dependencies
from .run import Spinner
from .run import run

BULB = yellow('💡', style='bold')
INFO = blue('🛈 ', style='bold')
ERROR = red('❌️', style='bold')

OPTIMIZE = {
    'speed': '3',
    'size': 's',
    'debug': '0'
}

TRANSPILE_OPTIONS_FMT = (
    '-n {package_name} -v {package_version} -p {package_path} {flags}')

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
                 jobs,
                 url):
        self.debug = debug
        self.verbose = verbose
        self.optimize = optimize
        self.debug_symbols = debug_symbols
        self.no_ccache = no_ccache
        self.coverage = coverage
        self.unsafe = unsafe
        self.jobs = jobs
        self.url = url


def create_file(path, data):
    with open(path, 'w') as fout:
        fout.write(data)


def read_template_file(path):
    with open(os.path.join(MYS_DIR, 'cli/templates', path)) as fin:
        return fin.read()


def default_jobs():
    return max(1, multiprocessing.cpu_count() - 1)


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


def create_file_from_template_path(path, template_path, **kwargs):
    template = read_template_file(template_path)
    create_file(path, template.format(**kwargs))


def create_file_from_template(path, directory, **kwargs):
    create_file_from_template_path(path, os.path.join(directory, path), **kwargs)


def setup_build():
    os.makedirs(DOWNLOAD_DIRECTORY, exist_ok=True)


def read_package_configuration():
    try:
        with Spinner('Reading package configuration'):
            return PackageConfig('.', None)
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


def find_package_sources(config, ignore_main=False):
    srcs_mys = []
    srcs_hpp = []
    srcs_cpp = []
    oldpath = os.getcwd()
    src_dir = os.path.join(config.path, 'src')
    os.chdir(src_dir)

    try:
        for src in glob.glob('**/*.mys', recursive=True):
            if ignore_main and src == 'main.mys':
                continue

            srcs_mys.append((config, src))

        for src in glob.glob('**/*.hpp', recursive=True):
            srcs_hpp.append((config, src))

        for src in glob.glob('**/*.cpp', recursive=True):
            srcs_cpp.append((config, src))
    finally:
        os.chdir(oldpath)

    return srcs_mys, srcs_hpp, srcs_cpp


def find_dependency_sources(config):
    srcs_mys, srcs_hpp, srcs_cpp = find_package_sources(config, ignore_main=True)

    return srcs_mys, srcs_hpp, srcs_cpp, {config.path}


def find_assets(config, dependencies_configs):
    assets = []
    paths = [(config.name, '.')]

    for dependency_config in dependencies_configs:
        paths.append((dependency_config.name, dependency_config.path))

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


def find_c_dependencies_flags(configs, verbose):
    if shutil.which('mys-config'):
        pkg_config = 'mys-config'
    elif shutil.which('pkg-config'):
        pkg_config = 'pkg-config'
    else:
        raise Exception('mys-config nor pkg-config found')

    cflags = PkgConfigFlags()
    libs = PkgConfigFlags()

    for config in configs:
        for library_name in config['c-dependencies']:
            output = run([pkg_config, library_name, '--cflags'],
                         f'Getting compiler flags {library_name}',
                         verbose)
            cflags.add(output)
            output = run([pkg_config, library_name, '--libs'],
                         f'Getting linker flags for {library_name}',
                         verbose)
            libs.add(output)

    return cflags, libs


def create_makefile(config, dependencies_configs, build_config):
    combo = build_config.optimize

    if build_config.coverage:
        combo += '-coverage'

    if build_config.unsafe:
        combo += '-unsafe'

    build_dir = f'build/{combo}'

    os.makedirs(f'{build_dir}/cpp', exist_ok=True)
    srcs_mys, srcs_hpp, srcs_cpp = find_package_sources(config)
    cflags, libs = find_c_dependencies_flags([config] + dependencies_configs,
                                             build_config.verbose)

    if not srcs_mys:
        box_print(["'src/' is empty. Please create one or more .mys-files."], ERROR)

        raise Exception()

    for dependency_config in dependencies_configs:
        srcs = find_dependency_sources(dependency_config)
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

    if build_config.debug_symbols:
        cflags.flags.append('-g')

    assets = find_assets(config, dependencies_configs)

    for package_config, src in srcs_mys:
        package_name = package_config.name
        flags = []

        if package_name != config.name:
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
                                         package_version=package_config.version,
                                         package_path=package_config.path,
                                         flags=flags))

        transpile_srcs.append(src)
        transpile_srcs_paths.append(os.path.join(package_config.path, 'src', src))
        objs.append(f'OBJ += {module_path}.$(OBJ_SUFFIX)')
        transpiled_cpp.append(f'SRC += {module_path}.cpp')

    for package_config, src in srcs_hpp:
        src_path = os.path.join(package_config.path, 'src', src)
        module_path = f'$(BUILD)/cpp/src/{package_config.name}/{src}'
        copy_hpp_and_cpp.append(COPY_HPP_AND_CPP_FMT.format(src=src_path,
                                                            dst=module_path))
        hpps.append(module_path)

    for package_config, src in srcs_cpp:
        src_path = os.path.join(package_config.path, 'src', src)
        module_path = f'$(BUILD)/cpp/src/{package_config.name}/{src}'
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

    create_file_from_template_path(
        f'{build_dir}/Makefile',
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
        package_name=config.name,
        transpiled_cpp='\n'.join(transpiled_cpp),
        cflags=cflags,
        libs=libs)

    return is_application, build_dir


def build_prepare(build_config, config=None):
    if config is None:
        config = read_package_configuration()

    setup_build()
    dependencies_configs = download_dependencies(config, build_config.url)
    is_application, build_dir = create_makefile(config,
                                                dependencies_configs,
                                                build_config)

    return is_application, build_dir, dependencies_configs


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


def add_url_argument(subparser):
    subparser.add_argument('--url',
                           default='https://mys-lang.org',
                           help='Website URL (default: %(default)s).')


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
    print(f'Coverage report: file://{path}')
