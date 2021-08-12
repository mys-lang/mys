import glob
import os
import tarfile

import requests

from .package_config import PackageConfig
from .run import Spinner

DOWNLOAD_DIRECTORY = 'build/dependencies'


def rename_one_matching(pattern, to):
    paths = glob.glob(pattern)

    if len(paths) != 1:
        raise Exception(
            f'{len(paths)} paths are matching when expecting exactly one to match')

    os.rename(paths[0], to)


def prepare_download_dependency_from_registry(name, version):
    archive = f'{name}-{version}.tar.gz'
    archive_path = f'{DOWNLOAD_DIRECTORY}/{archive}'

    if os.path.exists(archive_path):
        return None
    else:
        return (name, version, archive, archive_path)


def extract_dependency(name, version, archive_path):
    if version == 'latest':
        rename_one_matching(os.path.join(DOWNLOAD_DIRECTORY, f'{name}-*.tar.gz'),
                            archive_path)

    with tarfile.open(archive_path) as fin:
        fin.extractall(DOWNLOAD_DIRECTORY)

    if version == 'latest':
        rename_one_matching(os.path.join(DOWNLOAD_DIRECTORY, f'{name}-*/'),
                            os.path.join(DOWNLOAD_DIRECTORY, f'{name}-latest'))

    return os.path.join(DOWNLOAD_DIRECTORY, f'{name}-{version}')


def download_dependency_dependencies(config, url, handled_dependencies):
    packages = []

    for name in config['dependencies']:
        if name not in handled_dependencies:
            handled_dependencies.append(name)
            package = prepare_download_dependency_from_registry(name, 'latest')

            if package is not None:
                packages.append(package)

    download_and_extract_packages(packages, handled_dependencies, url)


def download_and_extract_packages(packages, handled_dependencies, url):
    for name, version, archive, archive_path in packages:
        response = requests.get(f'{url}/package/{archive}')

        if response.status_code != 200:
            print(response.text)

            raise Exception(f"Package download failed of package '{name}'.")

        with open(archive_path, 'wb') as fout:
            fout.write(response.content)

        dependency_root = extract_dependency(name, version, archive_path)
        download_dependency_dependencies(PackageConfig(dependency_root),
                                         url,
                                         handled_dependencies)


def download_dependencies(config, url):
    handled_dependencies = list(config['dependencies'])

    with Spinner(text="Downloading dependencies"):
        packages = []

        for name, info in config['dependencies'].items():
            if isinstance(info, str):
                package = prepare_download_dependency_from_registry(name, info)

                if package is not None:
                    packages.append(package)
            else:
                download_dependency_dependencies(PackageConfig(info['path']),
                                                 url,
                                                 handled_dependencies)

        download_and_extract_packages(packages, handled_dependencies, url)
