import pathlib
from typing import Optional

import typer
from rich import print

from mys.cli import app
from mys.cli.config.mys import MysConfig
from mys.cli.config.git import GitConfig
from mys.version import __version__


def version_callback(value: bool):
    if value:
        print(f"Mys CLI Version: {__version__}")
        raise typer.Exit(code=0)



@app.callback()
def main_callback(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        False, '--version', is_eager=True,
        callback=version_callback,
        help='Prints the version number and exits'
    ),
    config: Optional[pathlib.Path] = typer.Option(
        None, help='Configuration file to use.'
    ),
    debug: Optional[bool] = typer.Option(
        False, help='Run mys in debug mode.',
    )
):
    '''The Mys programming language package manager.'''

    ctx.meta['MYS'] = MysConfig(config)
    ctx.meta['GIT'] = GitConfig()
    ctx.meta['MYSDEBUG'] = debug
