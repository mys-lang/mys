import shutil
import os

from .utils import build_and_test_module
from .utils import TestCase

class Test(TestCase):

    def setUp(self):
        os.makedirs('tests/build', exist_ok=True)

    def test_enums(self):
        build_and_test_module('enums')

    def test_traits(self):
        build_and_test_module('traits')

    def test_classes(self):
        build_and_test_module('classes')

    def test_bytes(self):
        build_and_test_module('bytes')

    def test_char(self):
        build_and_test_module('char_')

    def test_dict(self):
        build_and_test_module('dict')

    def test_list(self):
        build_and_test_module('list')

    def test_string(self):
        build_and_test_module('string')

    def test_tuple(self):
        build_and_test_module('tuple')
