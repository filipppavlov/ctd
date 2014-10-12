class ClassObject(object):
    def __init__(self, index, obj):
        self.index = index
        self.object = obj


class SeriesRecord(object):
    def __init__(self, timestamp, index, metadata):
        self.timestamp = timestamp
        self.index = index
        self.metadata = metadata

    def __eq__(self, other):
        return self.timestamp == other.timestamp and self.index == other.index


DELETE_SERIES = 0
DELETE_CLASS = 1

class Store(object):
    def load_data(self):
        raise NotImplementedError()

    def add_class_object(self, equivalence_class, index, new_object):
        raise NotImplementedError()

    def add_series_record(self, series, index, timestamp, metadata):
        raise NotImplementedError()

    def dispose_object(self, new_object):
        raise NotImplementedError()

    def set_comparison_settings(self, path, settings):
        raise NotImplementedError()

    def set_ideal(self, series, object_index):
        raise NotImplementedError()

    def delete(self, to_delete_list):
        raise NotImplementedError()
