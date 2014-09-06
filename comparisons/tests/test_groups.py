import datetime
import unittest
from comparisons import engine
from comparisons.memorystore import MemoryStore


def _elements_in_iterator(iter):
    return sum([1 for _ in iter])


class TestGroups(unittest.TestCase):

    def test_can_get_top_level_groups(self):
        e = engine.Engine(MemoryStore())
        self.assertEqual(_elements_in_iterator(e.get_top_level_group().series), 0)
        e.add_object('test1', 123)
        e.process_all()
        self.assertEqual(_elements_in_iterator(e.get_top_level_group().series), 1)
        e.add_object('test2', 123)
        e.process_all()
        self.assertEqual(_elements_in_iterator(e.get_top_level_group().series), 2)
        e.add_object('test2.a', 123)
        e.process_all()
        self.assertEqual(_elements_in_iterator(e.get_top_level_group().series), 2)
        self.assertEqual(_elements_in_iterator(e.get_top_level_group().subgroups), 1)
        e.add_object('test3.a', 123)
        e.process_all()
        self.assertEqual(_elements_in_iterator(e.get_top_level_group().subgroups), 2)

    def test_adding_to_same_series_does_not_change_group_series(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.process_all()
        group = e.get_top_level_group()
        self.assertEqual(_elements_in_iterator(group.series), 1)
        e.add_object('test1', 456)
        e.process_all()
        self.assertEqual(_elements_in_iterator(group.series), 1)

    def test_adding_to_same_series_does_not_change_group_subgroups(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1.a', 456)
        e.process_all()
        group = e.get_top_level_group()
        self.assertEqual(_elements_in_iterator(group.subgroups), 1)
        e.add_object('test1.a', 456)
        e.process_all()
        self.assertEqual(_elements_in_iterator(group.subgroups), 1)

    def test_adding_to_different_series_changes_group_subgroups(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1.a', 456)
        e.process_all()
        group = e.get_top_level_group()
        e.add_object('test2.a', 456)
        e.process_all()
        self.assertEqual(_elements_in_iterator(group.subgroups), 2)

    def test_can_get_group(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1.a.b', 456)
        e.process_all()
        self.assertEqual(e.get_group('test1').path, 'test1')
        self.assertEqual(e.get_group('test1.a').path, 'test1.a')

    def test_can_get_group_subgroups(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1.a.b', 456)
        e.add_object('test1.b.b', 456)
        e.add_object('test1.a.c', 456)
        e.add_object('test1.a.d', 456)
        e.add_object('test1.c', 456)
        e.add_object('test1', 456)
        e.process_all()
        g = e.get_group('test1')
        self.assertItemsEqual([x.path for x in g.subgroups], ['test1.a', 'test1.b'])
        g = e.get_group('test1.a')
        self.assertEqual(_elements_in_iterator(g.subgroups), 0)

    def test_can_get_group_series(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1.a.b', 456)
        e.add_object('test1.b.b', 456)
        e.add_object('test1.a.c', 456)
        e.add_object('test1.a.d.e', 456)
        e.add_object('test1.a', 456)
        e.add_object('test1', 456)
        e.process_all()
        g = e.get_group('test1')
        s = [x.path for x in g.series]
        self.assertItemsEqual(s, ['test1.a'])
        g = e.get_group('test1.a')
        self.assertItemsEqual([x.path for x in g.series], ['test1.a.b', 'test1.a.c'])

    def test_can_get_group_last_commit_success(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1', 123)
        e.add_object('test1', 123)
        e.process_all()
        self.assertTrue(e.get_top_level_group().is_last_commit_successful())
        e.add_object('test1', 456)
        e.process_all()
        self.assertFalse(e.get_top_level_group().is_last_commit_successful())

    def test_group_last_commit_success_is_affected_by_subgroups(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1.a.b', 123)
        e.add_object('test1.a.b', 123)
        e.process_all()
        self.assertTrue(e.get_top_level_group().is_last_commit_successful())
        e.add_object('test1.a.b', 456)
        e.process_all()
        self.assertFalse(e.get_top_level_group().is_last_commit_successful())

    def test_top_group_comparison_settings(self):
        e = engine.Engine(MemoryStore())
        e.add_object('test1.a.b', 123)
        e.process_all()
        e.get_comparison_settings('')

    def test_can_get_group_modified_time(self):
        e = engine.Engine(MemoryStore())
        timestamp1 = datetime.datetime(1990, 2, 3)
        e.add_object('test1.a.c', 123, timestamp1)
        timestamp2 = datetime.datetime(1989, 2, 3)
        e.add_object('test1.b', 123, timestamp2)
        timestamp3 = datetime.datetime(1991, 2, 3)
        e.add_object('test2.a', 123, timestamp3)
        e.process_all()
        self.assertEqual(e.get_group('test1').modified, timestamp1)
        self.assertEqual(e.get_group('').modified, timestamp3)

    def test_can_get_descendant_series(self):
        e = engine.Engine(MemoryStore())
        names = 'test1.a.b', 'test1.a.c', 'test1.b.b', 'test1.c'
        for each in names:
            e.add_object(each, 123)
        e.process_all()
        self.assertItemsEqual((x.path for x in e.get_group('test1').descendant_series), names)
