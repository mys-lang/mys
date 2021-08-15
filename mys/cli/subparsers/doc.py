import os
import sys

from ..run import run
from ..utils import MYS_DIR
from ..utils import add_verbose_argument
from ..utils import create_file_from_template
from ..utils import read_package_configuration


def join_and(items):
    if len(items) == 0:
        return ''
    elif len(items) == 1:
        return items[0]
    else:
        return ', '.join(items[:-1]) + ' and ' + items[-1]


def do_doc(_parser, args, _mys_config):
    config = read_package_configuration()
    package_name_title = config.name.replace('_', ' ').title()
    authors = ', '.join(config['package']['authors'])
    copyrighters = join_and([author.name for author in config.authors])

    if os.path.exists('doc/images/logo.png'):
        html_logo = "html_logo = 'images/logo.png'"
    else:
        html_logo = ''

    create_file_from_template('doc/conf.py',
                              '.',
                              package_name=package_name_title,
                              authors=authors,
                              copyrighters=copyrighters,
                              html_logo=html_logo)

    path = os.getcwd()
    os.chdir('doc')

    try:
        command = [
            sys.executable, '-m', 'sphinx',
            '-T', '-E',
            '-b', 'html',
            '-d', '../build/doc/doctrees',
            '-D', 'language=en',
            '.', '../build/doc/html'
        ]
        env = os.environ.copy()
        env['PYTHONPATH'] = f'{MYS_DIR}/pygments:' + env.get('PYTHONPATH', '')
        run(command, 'Building documentation', args.verbose, env=env)
    finally:
        os.chdir(path)

    os.remove('doc/conf.py')
    path = os.path.abspath('build/doc/html/index.html')
    print(f'Documentation: file://{path}')


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'doc',
        description='Build the documentation.')
    add_verbose_argument(subparser)
    subparser.set_defaults(func=do_doc)
