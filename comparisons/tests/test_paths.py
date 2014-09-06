import unittest
from comparisons import paths, config


class TestPaths(unittest.TestCase):
    def test_empty_path_is_invalid(self):
        with self.assertRaises(ValueError):
            paths.get_equivalence_class_name('')

    def test_path_with_empty_component_is_invalid(self):
        with self.assertRaises(ValueError):
            paths.get_equivalence_class_name('abc..def')

    def test_equivalence_name_for_path_without_variables_is_the_path(self):
        self.assertEqual(paths.get_equivalence_class_name('abc'), 'abc')
        self.assertEqual(paths.get_equivalence_class_name('abc.def'), 'abc.def')

    def test_equivalence_name_for_path_with_variables(self):
        self.assertEqual(paths.get_equivalence_class_name('(abc)'), config.CLASS_WILDCARD)
        self.assertEqual(paths.get_equivalence_class_name('a.(abc)'), 'a.' + config.CLASS_WILDCARD)
        self.assertEqual(paths.get_equivalence_class_name('a.(b).c'), 'a.' + config.CLASS_WILDCARD + '.c')
        self.assertEqual(paths.get_equivalence_class_name('a.(b).c.(def)'), 'a.' + config.CLASS_WILDCARD + '.c.' +
                                                                            config.CLASS_WILDCARD)

    def test_encode_path(self):
        self.assertEqual(paths.encode_special_symbols('a.(abc)', '#', '/', ('$(', ')')), 'a/$(abc)')
        self.assertEqual(paths.encode_special_symbols('*.aaa', '#', '/', ('$(', ')')), '#/aaa')

    def test_decode_path(self):
        self.assertEqual(paths.decode_special_symbols('a/$(abc)', '#', '/', ('$(', ')')), 'a.(abc)')
        self.assertEqual(paths.decode_special_symbols('#/aaa', '#', '/', ('$(', ')')), '*.aaa')
