import unittest
from comparisons.filestore import FileStore, ObjectSerializer
from comparisons.store import SeriesRecord
import comparisons.config as config
import tempfile
import shutil
from datetime import datetime


class TrivialSerializer(ObjectSerializer):
    def to_string(self, equivalence_class, index, obj):
        return str(obj)

    def from_string(self, equivalence_class, index, string):
        return string


class TestFileStore(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_data_from_empty_directory_is_empty(self):
        s = FileStore(self.temp_dir, TrivialSerializer())
        classes, series, settings = s.load_data()
        self.assertEqual(len(classes), 0)
        self.assertEqual(len(series), 0)

    def test_can_serialize_single_object(self):
        s = FileStore(self.temp_dir, TrivialSerializer())
        s.add_class_object('test', 0, '123')
        del s

        s = FileStore(self.temp_dir, TrivialSerializer())
        classes, series, settings = s.load_data()
        self.assertEqual(len(series), 0)
        self.assertEqual(classes, {'test': ['123']})

    def test_can_serialize_multiple_object_of_a_class(self):
        s = FileStore(self.temp_dir, TrivialSerializer())
        s.add_class_object('test', 0, '123')
        s.add_class_object('test', 1, '456')
        del s

        s = FileStore(self.temp_dir, TrivialSerializer())
        classes, series, settings = s.load_data()
        self.assertEqual(len(series), 0)
        self.assertEqual(classes, {'test': ['123', '456']})

    def test_can_serialize_multiple_classes(self):
        s = FileStore(self.temp_dir, TrivialSerializer())
        s.add_class_object('test', 0, '123')
        s.add_class_object('a.b.c', 0, '456')
        del s

        s = FileStore(self.temp_dir, TrivialSerializer())
        classes, series, settings = s.load_data()
        self.assertEqual(len(series), 0)
        self.assertEqual(classes, {'test': ['123'], 'a.b.c': ['456']})

    def test_can_serialize_class_with_wildcard(self):
        s = FileStore(self.temp_dir, TrivialSerializer())
        s.add_class_object('test.' + config.CLASS_WILDCARD, 0, '123')
        del s

        s = FileStore(self.temp_dir, TrivialSerializer())
        classes, series, settings = s.load_data()
        self.assertEqual(len(series), 0)
        self.assertEqual(classes, {'test.' + config.CLASS_WILDCARD: ['123']})

    def test_can_serialize_class_and_series(self):
        s = FileStore(self.temp_dir, TrivialSerializer())
        s.add_class_object('test.' + config.CLASS_WILDCARD, 0, '123')
        timestamp = datetime.now()
        s.add_series_record('test.%sabc%s' % config.VARIABLE_DELIMS, 0, timestamp, "")
        del s

        s = FileStore(self.temp_dir, TrivialSerializer())
        classes, series, settings = s.load_data()
        self.assertEqual(series, {'test.%sabc%s' % config.VARIABLE_DELIMS: ([SeriesRecord(timestamp, 0, None)], None)})
        self.assertEqual(classes, {'test.' + config.CLASS_WILDCARD: ['123']})
        self.assertEqual(settings, {})

    def test_can_serialize_metadata(self):
        s = FileStore(self.temp_dir, TrivialSerializer())
        s.add_class_object('test.' + config.CLASS_WILDCARD, 0, '123')
        timestamp = datetime.now()
        s.add_series_record('test.%sabc%s' % config.VARIABLE_DELIMS, 0, timestamp, "abc")
        del s

        s = FileStore(self.temp_dir, TrivialSerializer())
        classes, series, settings = s.load_data()
        self.assertEqual(series, {'test.%sabc%s' % config.VARIABLE_DELIMS: ([SeriesRecord(timestamp, 0, "abc")], None)})
        self.assertEqual(classes, {'test.' + config.CLASS_WILDCARD: ['123']})
        self.assertEqual(settings, {})
