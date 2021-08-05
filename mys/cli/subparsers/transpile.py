import os

from ...transpiler import Source
from ...transpiler import transpile
from ..utils import add_coverage_argument
from ..utils import add_unsafe_argument
from ..utils import create_file


def do_transpile(_parser, args, _mys_config):
    sources = []

    for i, mysfile in enumerate(args.mysfiles):
        mys_path = os.path.join(args.package_path[i], 'src', mysfile)
        module_hpp = os.path.join(args.package_name[i], mysfile + '.hpp')
        module = '.'.join(module_hpp[:-8].split('/'))
        hpp_path = os.path.join(args.outdir, 'include', module_hpp)
        cpp_path = os.path.join(args.outdir,
                                'src',
                                args.package_name[i],
                                mysfile + '.cpp')

        with open(mys_path, 'r') as fin:
            sources.append(Source(fin.read(),
                                  mysfile,
                                  args.package_version[i],
                                  module,
                                  mys_path,
                                  module_hpp,
                                  args.skip_tests[i] == 'yes',
                                  hpp_path,
                                  cpp_path,
                                  args.main[i] == 'yes'))

    generated = transpile(sources, args.coverage)

    for source, (hpp_1_code, hpp_2_code, cpp_code) in zip(sources, generated):
        os.makedirs(os.path.dirname(source.hpp_path), exist_ok=True)
        os.makedirs(os.path.dirname(source.cpp_path), exist_ok=True)
        create_file(source.hpp_path[:-3] + 'early.hpp', hpp_1_code)
        create_file(source.hpp_path, hpp_2_code)
        create_file(source.cpp_path, cpp_code)


def add_subparser(subparsers):
    subparser = subparsers.add_parser(
        'transpile',
        description='Transpile given Mys file(s) to C++ header and source files.')
    subparser.add_argument('-o', '--outdir',
                           default='.',
                           help='Output directory.')
    subparser.add_argument('-p', '--package-path',
                           required=True,
                           action='append',
                           help='Package path.')
    subparser.add_argument('-n', '--package-name',
                           required=True,
                           action='append',
                           help='Package name.')
    subparser.add_argument('-v', '--package-version',
                           required=True,
                           action='append',
                           help='Package version.')
    subparser.add_argument('-s', '--skip-tests',
                           action='append',
                           choices=['yes', 'no'],
                           help='Skip tests.')
    subparser.add_argument('-m', '--main',
                           action='append',
                           choices=['yes', 'no'],
                           help='Contains main().')
    add_coverage_argument(subparser)
    add_unsafe_argument(subparser)
    subparser.add_argument('mysfiles', nargs='+')
    subparser.set_defaults(func=do_transpile)
