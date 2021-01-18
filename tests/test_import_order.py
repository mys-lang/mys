from mys.transpiler.import_order import resolve_import_order

from .utils import TestCase


class Test(TestCase):

    def test_imports(self):
        modules = {
            'mypkg.lib': [
                'mypkg1.subpkg1.mod1',
                'mypkg1.lib',
                'mypkg2.lib',
                'mypkg.mod1',
                'mypkg.mod3',
                'mypkg.mod2'
            ],
            'mypkg.mod1': [
                'mypkg.mod3',
                'mypkg.mod2'
            ],
            'mypkg.mod2': [],
            'mypkg.mod3': [],
            'mypkg1.lib': [
                'mypkg2.lib',
                'mypkg2.mod1',
                'mypkg1._mod1',
                'mypkg1._subpkg2.mod1'
            ],
            'mypkg1._mod1': [],
            'mypkg1.subpkg1.mod1': [
                'mypkg1.lib'
            ],
            'mypkg1._subpkg2.mod1': [],
            'mypkg2.lib': [
                'mypkg2.mod1'
            ],
            'mypkg2.mod1': []
        }

        self.assertEqual(resolve_import_order(modules),
                         [
                             'mypkg2.mod1',
                             'mypkg2.lib',
                             'mypkg1._mod1',
                             'mypkg1._subpkg2.mod1',
                             'mypkg1.lib',
                             'mypkg1.subpkg1.mod1',
                             'mypkg.mod3',
                             'mypkg.mod2',
                             'mypkg.mod1',
                             'mypkg.lib'
                         ])

    def test_main(self):
        modules = {
            'foo.main': [
                'foo.foo'
            ],
            'foo.foo': [
                'foo.bar',
                'foo.fie'
            ],
            'foo.bar': [],
            'foo.fie': []
        }

        self.assertEqual(resolve_import_order(modules),
                         [
                             'foo.bar',
                             'foo.fie',
                             'foo.foo',
                             'foo.main'
                         ])

    def test_cyclic(self):
        modules = {
            'foo.main': [
                'foo.foo'
            ],
            'foo.foo': [
                'foo.bar',
                'foo.fie'
            ],
            'foo.bar': ['foo.fie'],
            'foo.fie': ['foo.bar'],
            'foo.fam': ['foo.fum'],
            'foo.fum': ['foo.fam']
        }

        self.assertEqual(resolve_import_order(modules),
                         [
                             'foo.fie',
                             'foo.bar',
                             'foo.foo',
                             'foo.main',
                             'foo.fum',
                             'foo.fam'
                         ])
