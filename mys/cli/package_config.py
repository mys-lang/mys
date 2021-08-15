import os
import re

import toml

from ..transpiler.utils import is_snake_case
from .mys_dir import MYS_DIR

RE_SEMANTIC_VERSION = re.compile(
    # major, minor and patch
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    # pre release
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    # build metadata
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$")


def is_semantic_version(version):
    return RE_SEMANTIC_VERSION.match(version) is not None


class Author:

    def __init__(self, name, email):
        self.name = name
        self.email = email


class PackageConfig:

    def __init__(self, path, from_version):
        self.path = path
        self.from_version = from_version
        self.authors = []
        self.config = self.load_package_configuration(path)
        self.name = self.config['package']['name']
        self.version = self.config['package']['version']

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

        if not is_semantic_version(package['version']):
            raise Exception(
                "package version must be a semantic version, "
                f"got '{package['version']}'")

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
