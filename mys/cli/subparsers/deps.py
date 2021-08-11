import os

from ..utils import DOWNLOAD_DIRECTORY
from ..utils import PackageConfig
from ..utils import add_url_argument
from ..utils import add_verbose_argument
from ..utils import read_package_configuration


def find_dependencies(config):
    packages = []

    for name, version in config['dependencies'].items():
        if name == 'fiber':
            continue

        if isinstance(version, str):
            package_path = os.path.join(DOWNLOAD_DIRECTORY, f'{name}-{version}')
        else:
            package_path = version['path']

        current_version = PackageConfig(package_path)['package']['version']
        packages.append((name, version, current_version))

    return packages


def show():
    config = read_package_configuration()
    packages = find_dependencies(config)

    for name, version, _ in packages:
        if isinstance(version, str):
            version = f'"{version}"'
        else:
            version = f'{{ path = "{version["path"]}" }}'

        print(f'{name} = {version}')


def versions():
    config = read_package_configuration()
    packages = find_dependencies(config)

    for name, _, current_version in packages:
        print(f'{name} = "{current_version}"')


def do_deps(_parser, args, _mys_config):
    if args.versions:
        versions()
    else:
        show()


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'deps',
        description='Manage dependencies.')
    add_verbose_argument(subparser)
    add_url_argument(subparser)
    subparser.add_argument(
        '--versions',
        action='store_true',
        help='Show all package versions currently used by this package.')
    subparser.set_defaults(func=do_deps)
