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


class PackagesFinder:

    def __init__(self, url):
        self.config = None
        self.url = url
        self.handled_dependencies = None
        self.packages_configs = None

    def download_dependency_dependencies(self, config):
        packages = []

        for name in config['dependencies']:
            if name not in self.handled_dependencies:
                self.handled_dependencies.append(name)
                package = prepare_download_dependency_from_registry(name, 'latest')

                if package is not None:
                    packages.append(package)

        self.download_and_extract_packages(packages)

    def download_and_extract_packages(self, packages):
        for name, version, archive, archive_path in packages:
            response = requests.get(f'{self.url}/package/{archive}')

            if response.status_code != 200:
                print(response.text)

                raise Exception(f"Package download failed of package '{name}'.")

            with open(archive_path, 'wb') as fout:
                fout.write(response.content)

            dependency_root = extract_dependency(name, version, archive_path)
            self.download_dependency_dependencies(
                self.load_package_config(dependency_root))

    def load_package_config(self, path):
        package_config = PackageConfig(path)
        self.packages_configs.append(package_config)

        return package_config

    def find(self, config):
        self.config = config
        self.handled_dependencies = list(self.config['dependencies'])
        self.packages_configs = []

        with Spinner(text="Downloading dependencies"):
            packages = []

            for name, info in self.config['dependencies'].items():
                if isinstance(info, str):
                    package = prepare_download_dependency_from_registry(name, info)

                    if package is not None:
                        packages.append(package)
                else:
                    self.download_dependency_dependencies(
                        self.load_package_config(info['path']))

            self.download_and_extract_packages(packages)

        return self.packages_configs


def download_dependencies(config, url):
    package_finder = PackagesFinder(url)

    return package_finder.find(config)
