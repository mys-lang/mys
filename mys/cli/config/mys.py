import errno
import json
import pathlib
import os
import sys

from rich import print
import toml
import typer


class MysConfig(dict):
    def __init__(self, filepath=None):
        if filepath is None:
            filepath = os.getenv('MYS_CONFIG')

        if filepath is not None:
            filepath = pathlib.Path(filepath)
            if not filepath.exists():
                print('No such file %s' % filepath, file=sys.stderr)
                raise typer.Exit(code=errno.ENOENT)
            if filepath.is_dir():
                print('Path %s is a directory' % filepath, file=sys.stderr)
                raise typer.Exit(code=errno.EISDIR)
        else:
            filepath = pathlib.Path('~/.config/mys/config.toml')

        filepath = filepath.expanduser()
        if filepath.is_dir():
            dirpath = filepath
        else:
            dirpath = filepath.parent
        dirpath.mkdir(parents=True, exist_ok=True)
        if not filepath.exists():
            filepath.touch()

        try:
            data = toml.loads(filepath.read_text())
        except toml.decoder.TomlDecodeError:
            raise typer.Exit(code=errno.EIO)
        for k, v in data.items():
            self[k] = v


    class Theme(dict):
        def __init__(self, theme_name):
            themes_dir = pathlib.Path('~/.config/mys/themes')
            themes_dir.mkdir(exist_ok=True, parents=True)
            theme_path = (
                themes_dir / theme_name
            ).with_suffix('json').expanduser()
            data = json.loads(theme_path.read_text())
            for k, v in data.items:
                self[k] = v

        @staticmethod
        def available_themes():
            themes_dir = pathlib.Path('~/.config/mys/themes')
            return themes_dir.glob('*.json')
