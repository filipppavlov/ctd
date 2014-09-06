import json
import threading
import os
import datetime

from . import store, paths

CLASSES_DIR = 'classes'
SERIES_DIR = 'series'
TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

SPECIAL_SYMBOLS = '#', os.sep, ('(', ')')
FIELD_SEPARATOR = '|'


class ObjectSerializer(object):
    def to_string(self, equivalence_class, index, obj):
        pass

    def from_string(self, equivalence_class, index, string):
        pass

    def dispose(self, obj):
        pass


class FileStore(store.Store):
    def __init__(self, directory, object_serializer):
        self.object_serializer = object_serializer
        self.directory = os.path.abspath(directory)
        self.lock = threading.Lock()
        self._make_dir(CLASSES_DIR)
        self._make_dir(SERIES_DIR)

    def _walk(self, root_dir, extension):
        for root, dirs, files in os.walk(os.path.join(self.directory, root_dir)):
            for each in files:
                if os.path.splitext(each)[1].lower() != extension:
                    continue
                path = os.path.join(root, each)
                p = os.path.splitext(os.path.relpath(path, os.path.join(self.directory, root_dir)))[0]
                name = paths.decode_special_symbols(p, *SPECIAL_SYMBOLS)
                yield name, path

    def _load_classes(self):
        equivalence_classes = dict()
        for class_name, path in self._walk(CLASSES_DIR, '.class'):
            equivalence_classes[class_name] = []
            with open(path) as f:
                for line in f:
                    equivalence_classes[class_name].append(self.object_serializer.from_string(class_name, len(equivalence_classes[class_name]), line.rstrip('\n')))
        return equivalence_classes

    def _load_series(self):
        series = dict()
        for series_name, path in self._walk(SERIES_DIR, '.series'):
            series[series_name] = ([], None)
            with open(path) as f:
                for i, line in enumerate(f):
                    items = line.rstrip('\n').split(FIELD_SEPARATOR)
                    timestamp = datetime.datetime.strptime(items[0], TIMESTAMP_FORMAT)
                    metadata = ('|'.join(items[2:])).decode('unicode_escape')
                    series[series_name][0].append(store.SeriesRecord(timestamp, int(items[1]), metadata))
        for series_name, path in self._walk(SERIES_DIR, '.ideal'):
            with open(path) as f:
                ideal = int(f.read())
                series[series_name] = (series[series_name][0], ideal)
        return series

    def _load_settings(self):
        settings = {}
        for series_name, path in self._walk(SERIES_DIR, '.settings'):
            with open(path) as f:
                settings[series_name] = json.load(f)
        return settings

    def load_data(self):
        equivalence_classes = self._load_classes()
        series = self._load_series()
        settings = self._load_settings()
        return equivalence_classes, series, settings

    def _get_write_file(self, path, base_dir, extension):
        name = paths.encode_special_symbols(path, *SPECIAL_SYMBOLS)
        dir_name = os.path.dirname(os.path.join(self.directory, base_dir, name))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        return os.path.join(self.directory, base_dir, name) + extension

    def add_class_object(self, equivalence_class, index, new_object):
        with self.lock:
            with open(self._get_write_file(equivalence_class, CLASSES_DIR, '.class'), 'a') as f:
                f.write(self.object_serializer.to_string(equivalence_class, index, new_object) + '\n')

    def add_series_record(self, series, index, timestamp, metadata):
        with self.lock:
            with open(self._get_write_file(series, SERIES_DIR, '.series'), 'a') as f:
                f.write('%s%s%s%s%s\n' % (timestamp.strftime(TIMESTAMP_FORMAT), FIELD_SEPARATOR, str(index),
                                          FIELD_SEPARATOR, metadata.encode('unicode_escape')))

    def dispose_object(self, new_object):
        self.object_serializer.dispose(new_object)

    def set_comparison_settings(self, path, settings):
        with self.lock:
            file_path = self._get_write_file(path, SERIES_DIR, '.settings')
            if settings is None:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            else:
                with open(file_path, 'w') as f:
                    json.dump(settings, f)

    def _make_dir(self, name):
        path = os.path.join(self.directory, name)
        if not os.path.exists(path):
            os.makedirs(path)

    def set_ideal(self, series, object_index):
        with self.lock:
            with open(self._get_write_file(series, SERIES_DIR, '.ideal'), 'w') as f:
                f.write('%s' % object_index)
