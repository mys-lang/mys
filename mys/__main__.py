#!/usr/bin/env python3

from mys.cli import app

from mys.cli.callback import main_callback

from mys.cli.commands.new import new
from mys.cli.commands.run import run

app()
