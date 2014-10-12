from comparisons.store import Store


class MemoryStore(Store):
    def load_data(self):
        return {}, {}, {}

    def add_class_object(self, equivalence_class, index, new_object):
        pass

    def add_series_record(self, series, index, timestamp, metadata):
        pass

    def dispose_object(self, new_object):
        pass

    def set_comparison_settings(self, path, settings):
        pass

    def set_ideal(self, series, object_index):
        pass

    def delete(self, to_delete_list):
        pass
