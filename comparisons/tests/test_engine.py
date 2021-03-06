from comparisons import engine, paths
from comparisons.memorystore import MemoryStore
import datetime
import unittest


def _elements_in_iterator(iterator):
    return sum([1 for _ in iterator])


class TestEngine(unittest.TestCase):
    def test_can_add_object(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', None)

    def test_can_add_object_with_variables(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1.(a)', None)
        e.add_object('(a).test1.(b)', None)

    def test_can_get_latest_object(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.process_all()
        self.assertEqual(e.get_series('test1').get_latest_object().object, 123)
        e.add_object('test1', 234)
        e.process_all()
        self.assertEqual(e.get_series('test1').get_latest_object().object, 234)

    def test_comparison_for_equal_objects_succeeds(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.add_object('test1', 123)
        e.process_all()
        self.assertEqual(e.get_series('test1').get_latest_object().index, 0)

    def test_comparison_for_non_equal_objects_fails(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.add_object('test1', 456)
        e.process_all()
        self.assertEqual(e.get_series('test1').get_latest_object().index, 1)

    def test_can_find_last_equal_object(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.add_object('test1', 456)
        e.add_object('test1', 123)
        e.process_all()
        self.assertEqual(e.get_series('test1').get_latest_object().index, 0)

    def test_can_get_series(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.add_object('test1', 456)
        e.process_all()
        series = e.get_series('test1')
        self.assertEqual(len([x.timestamp for x in series]), 2)
        self.assertItemsEqual([x.object for x in series], [123, 456])

    def test_get_similar_series_rases_when_series_dont_exist(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.process_all()
        with self.assertRaises(KeyError):
            _elements_in_iterator(e.get_equivalent_series(e))

    def test_get_similar_series_is_empty_when_no_similar_series_exist(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.add_object('test2', 123)
        e.process_all()
        self.assertEqual(_elements_in_iterator(e.get_equivalent_series('test1')), 0)
        e.add_object('test1.a', 123)
        e.add_object('test2.b', 123)
        e.process_all()
        self.assertEqual(_elements_in_iterator(e.get_equivalent_series('test1.a')), 0)
        e.add_object('test1.(a)', 123)
        e.add_object('test2.(a)', 123)
        e.process_all()
        self.assertEqual(_elements_in_iterator(e.get_equivalent_series('test1.(a)')), 0)

    def test_can_find_similar_series(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1.(a)', 123)
        e.add_object('test1.(b)', 123)
        e.process_all()
        self.assertEqual(_elements_in_iterator(e.get_equivalent_series('test1.(a)')), 1)

    def test_series_persist_timestamp(self):
        e = engine.Engine(MemoryStore())
        timestamp = datetime.datetime(1990, 2, 3)
        e.add_object('test1', None, timestamp)
        e.process_all()
        self.assertEqual(e.get_series('test1').get_latest_object().timestamp, timestamp)

    def test_series_with_one_object_last_commit_successful_raises(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.process_all()
        with self.assertRaises(IndexError):
            e.get_series('test1').is_last_commit_successful()

    def test_series_with_last_two_equal_records_last_commit_successful_is_true(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.add_object('test1', 123)
        e.process_all()
        self.assertTrue(e.get_series('test1').is_last_commit_successful())

    def test_series_with_last_two_unequal_records_last_commit_successful_is_false(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.add_object('test1', 456)
        e.process_all()
        self.assertFalse(e.get_series('test1').is_last_commit_successful())

    def test_other_records_do_not_influence_series_last_commit_success(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.add_object('test1', 123)
        e.add_object('test1', 456)
        e.process_all()
        self.assertFalse(e.get_series('test1').is_last_commit_successful())
        e.add_object('test1', 456)
        e.process_all()
        self.assertTrue(e.get_series('test1').is_last_commit_successful())

    def test_can_find_series(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.add_object('atest11', 123)
        e.add_object('test2', 456)
        e.process_all()
        self.assertItemsEqual((e.get_series('test1'), e.get_series('atest11')), e.find_series('test1'))

    def test_custom_comparison(self):
        class StrangeComparison(engine.BaseComparison):
            def compare(self, x, y, settings):
                return x != y
        e = engine.Engine(MemoryStore(), StrangeComparison())
        e.add_object('test1', 123)
        e.add_object('test1', 456)
        e.process_all()
        self.assertEqual(e.get_series('test1').get_latest_object().index, 0)

    def test_custom_comparison_settings(self):
        class StrangeComparison(engine.BaseComparison):
            def get_setting_names(self):
                return 'test',

            def compare(self, x, y, settings):
                settings = settings or {}
                return settings.get('test', False)

        e = engine.Engine(MemoryStore(), StrangeComparison())
        e.add_object('test1', 123)
        e.add_object('test1', 456)
        e.process_all()
        self.assertEqual(e.get_series('test1').get_latest_object().index, 1)
        e.add_object('test1', 789, comparison_settings={'test': True})
        e.process_all()
        self.assertEqual(e.get_series('test1').get_latest_object().index, 1)

    def test_comparison_settings_persist_in_series(self):
        class StrangeComparison(engine.BaseComparison):
            def get_setting_names(self):
                return 'test',

            def compare(self, x, y, settings):
                settings = settings or {}
                return settings.get('test', False)

        e = engine.Engine(MemoryStore(), StrangeComparison())
        e.add_object('test1', 123)
        e.add_object('test1', 456)
        e.add_object('test1', 789, comparison_settings={'test': True})
        e.add_object('test1', 123)
        e.process_all()
        self.assertEqual(e.get_series('test1').get_latest_object().index, 1)

    def test_comparison_settings_are_inherited_from_groups(self):
        class StrangeComparison(engine.BaseComparison):
            def get_setting_names(self):
                return 'test',

            def compare(self, x, y, settings):
                settings = settings or {}
                return settings.get('test', False)

        e = engine.Engine(MemoryStore(), StrangeComparison())
        e.add_object('test1.a', 123)
        e.process_all()
        e.set_comparison_settings('test1', {'test': True})
        e.add_object('test1.a', 456)
        e.process_all()
        self.assertEqual(e.get_series('test1.a').get_latest_object().index, 0)

    def test_can_get_series_modified_time(self):
        e = engine.Engine(MemoryStore())
        timestamp = datetime.datetime(1990, 2, 3)
        e.add_object('test', 123, timestamp)
        e.process_all()
        self.assertEqual(e.get_series('test').modified, timestamp)

    def test_can_delete_series(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a', 123)
        e.process_all()
        e.delete_series('a')
        with self.assertRaises(KeyError):
            e.get_series('a')

    def test_can_deleting_non_existing_series_raises(self):
        e = engine.Engine(MemoryStore())
        with self.assertRaises(KeyError):
            e.delete_series('a')

    def test_can_deleting_only_series_in_class_deletes_class(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a', 123)
        e.process_all()
        e.delete_series('a')
        with self.assertRaises(KeyError):
            e.get_equivalence_class('a')

    def test_can_deleting_series_in_class_with_other_series_does_not_delete_class(self):
        e = engine.Engine(MemoryStore())
        e.add_object('(a)', 123)
        e.add_object('(b)', 123)
        e.process_all()
        e.delete_series('(a)')
        self.assertItemsEqual(e.get_equivalence_class(paths.get_equivalence_class_name('(a)')).series,
                              [e.get_series('(b)')])

    def test_deleting_series_deletes_it_from_group(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a', 123)
        e.process_all()
        e.delete_series('a')
        self.assertNotIn('a', [x.path for x in e.get_top_level_group().series])

    def test_deleting_only_series_in_group_deletes_group(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a.b.c', 123)
        e.process_all()
        e.delete_series('a.b.c')
        with self.assertRaises(KeyError):
            e.get_group('a')
        with self.assertRaises(KeyError):
            e.get_group('a.b')
        self.assertTrue(e.get_group(''))

    def test_deleting_series_with_other_series_in_the_group_does_not_delete_group(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a.b', 123)
        e.add_object('a.c', 123)
        e.process_all()
        e.delete_series('a.b')
        self.assertTrue(e.get_group('a'))

    def test_deleting_series_with_other_subgroups_in_the_group_does_not_delete_group(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a.b', 123)
        e.add_object('a.c.d', 123)
        e.process_all()
        e.delete_series('a.b')
        self.assertTrue(e.get_group('a'))

    def test_delete_group_removes_group(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a.b', 123)
        e.process_all()
        e.delete_group('a')
        with self.assertRaises(KeyError):
            e.get_group('a')

    def test_delete_group_is_not_allowed_for_top_group(self):
        e = engine.Engine(MemoryStore())
        with self.assertRaises(RuntimeError):
            e.delete_group('')

    def test_delete_group_removes_child_series(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a.b', 123)
        e.process_all()
        e.delete_group('a')
        with self.assertRaises(KeyError):
            e.get_series('a.b')

    def test_delete_group_removes_descendant_series(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a.b.c', 123)
        e.process_all()
        e.delete_group('a')
        with self.assertRaises(KeyError):
            e.get_series('a.b.c')

    def test_delete_group_removes_descendant_subgroups(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a.b.c', 123)
        e.process_all()
        e.delete_group('a')
        with self.assertRaises(KeyError):
            e.get_group('a.b')

    def test_delete_group_removes_it_from_parent(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a.b', 123)
        e.process_all()
        e.delete_group('a')
        self.assertNotIn('a', e.get_top_level_group().subgroups_by_name)

    def test_delete_group_does_not_remove_series_with_the_same_name(self):
        e = engine.Engine(MemoryStore())
        e.add_object('a.b', 123)
        e.add_object('a', 123)
        e.process_all()
        e.delete_group('a')
        self.assertTrue(e.get_series('a'))
