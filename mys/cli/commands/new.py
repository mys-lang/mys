import errno
import getpass
import os
import pathlib
import re
from typing import Optional, List

import typer
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich import box

from mys.cli import app
from mys.cli.constants import MYS_DIR, ERROR, BULB

def find_authors(git_config, authors):
    if authors is not None:
        return ', '.join([f'"{author}"'for author in authors])

    user = git_config.get('user.name', getpass.getuser())
    email = git_config.get('user.email', f'{user}@example.com')

    return f'"{user} <{email}>"'


def create_file(path: pathlib.Path, directory: str, **kwargs):
    template_path = MYS_DIR / 'cli' / 'templates' / directory / path
    template = template_path.read_text(encoding='utf-8')
    (pathlib.Path.cwd() / path).parent.mkdir(parents=True, exist_ok=True)
    (pathlib.Path.cwd() / path).write_text(template.format(**kwargs))


@app.command('new')
def new(
    ctx: typer.Context, path: pathlib.Path,
    author: Optional[List[str]] = typer.Option(None)
):
    '''
    Create a new package.
    '''
    package_name = path.name
    namespace = {
        'package_name': package_name,
        'authors': find_authors(ctx.meta['GIT'], author),
        'line': '=' * len(package_name),
        'title': package_name.replace('_', ' ').title()
    }
    root = (MYS_DIR / 'cli' / 'templates' / 'new')
    files = [
        str(fp.as_posix())
        .replace(
            str(root.as_posix()), ''
        ).lstrip('/')
        for fp in root.rglob('*')
        if fp.is_file()
    ]
    console = Console()

    if not re.match(r'^[a-z][a-z0-9_]*$', package_name):
        print(Panel.fit(
            f'''\
            Package names must start with a letter and only  {ERROR}
            contain letters, numbers and underscores. Only lower
            case letters are allowed.'

            Here are a few examples:

            [cyan]mys new foo[/cyan]
            [cyan]mys new f1[/cyan]
            [cyan]mys new foo_bar[/cyan]
            ''', box=box.SQUARE,
        ))
        raise typer.Exit(code=errno.EIO)

    with console.status(f'Creating package {package_name}', spinner='dots'):
        path.mkdir(parents=True, exist_ok=True)
        cwd = pathlib.Path.cwd()
        os.chdir(path)
        try:
            while files:
                filepath = files.pop()
                create_file(pathlib.Path(filepath), 'new', **namespace)
        finally:
            os.chdir(cwd)
    print(Panel.fit(
        f'''\
        Build and run the new package by typing:  {BULB}

        [cyan]cd {package_name}[/cyan]
        [cyan]mys run[/cyan]
        ''', box=box.SQUARE,
    ))
