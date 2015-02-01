import datetime
import threading
from comparisons.comparison import BaseComparison

import comparisons.store as store
import comparisons.paths as paths
from comparisons.store import SeriesRecord
from comparisons.queue import ComparisonQueue


class ObjectRecord(object):
    def __init__(self, obj, index, series_index, timestamp, metadata):
        self.object = obj
        self.index = index
        self.series_index = series_index
        self.timestamp = timestamp
        self.metadata = metadata


class Series(object):
    def __init__(self, path, equivalence_class):
        self.path = path
        self.equivalence_class = equivalence_class
        self.records = []
        self.comparison_settings = None
        self.ideal = None

    @property
    def modified(self):
        return self.get_latest_object().timestamp

    def get_last_difference(self):
        if len(self.records) == 0:
            return None
        index = self.get_latest_object().index
        for each in range(len(self.records) - 2, -1, -1):
            if self.records[each].index != index:
                return self.records[each + 1].timestamp
        return None

    def is_last_commit_successful(self):
        if len(self.records) < 2:
            raise IndexError('series does not have enough records')
        if self.ideal is not None:
            return self.records[self.ideal].index == self.records[len(self.records) - 1].index
        return self.records[len(self.records) - 1].index == self.records[len(self.records) - 2].index

    def get_latest_object(self):
        return self.get_object(len(self.records) - 1)

    def get_object(self, index):
        record = self.records[index]
        return ObjectRecord(self.equivalence_class.get_object(record.index), record.index, index, record.timestamp, record.metadata)

    def __iter__(self):
        for i, record in enumerate(self.records):
            yield ObjectRecord(self.equivalence_class.get_object(record.index), record.index, i, record.timestamp, record.metadata)

    def get_difference_count(self, commit_count):
        return len(set((x.index for x in self.records[-commit_count:])))

    def get_ideal(self):
        if self.ideal is None:
            return None
        return self.get_object(self.ideal)

    def get_name(self):
        return paths.split(self.path)[-1]


class Group(object):
    def __init__(self, path):
        self.path = path
        self.subgroups = []
        self.series = []
        self.subgroups_by_name = {}
        self.comparison_settings = None

    @property
    def modified(self):
        ret = None
        for each in self.subgroups:
            m = each.modified
            if m is not None and (ret is None or m > ret):
                ret = m
        for each in self.series:
            m = each.modified
            if m is not None and (ret is None or m > ret):
                ret = m
        return ret

    def get_last_difference(self):
        ret = None
        for each in self.subgroups:
            m = each.get_last_difference()
            if m is not None and (ret is None or m > ret):
                ret = m
        for each in self.series:
            m = each.get_last_difference()
            if m is not None and (ret is None or m > ret):
                ret = m
        return ret

    def is_last_commit_successful(self):
        result = None
        for each in self.series:
            try:
                if not each.is_last_commit_successful():
                    return False
                else:
                    result = True
            except IndexError:
                pass
        for each in self.subgroups:
            try:
                if not each.is_last_commit_successful():
                    return False
                else:
                    result = True
            except IndexError:
                pass
        if result is None:
            raise IndexError('group series do not have enough records')
        return True

    @property
    def descendant_series(self):
        series = []
        for each in self.series:
            series.append(each)
        for each in self.subgroups:
            series.extend(each.descendant_series)
        return series

    def get_difference_count(self, commit_count):
        count = 0
        dcount = 0
        for each in self.descendant_series:
            dcount += each.get_difference_count(commit_count)
            count += 1
        if count == 0:
            return 0
        return int(float(dcount) / count)

    def get_name(self):
        return paths.split(self.path)[-1]


class EquivalenceClass(object):
    def __init__(self, name):
        self.name = name
        self.objects = []
        self.series = []

    def get_object(self, index):
        return self.objects[index]


def _get_object_index_in_class(equivalence_class, obj, comparison, settings):
    for i in xrange(len(equivalence_class.objects) - 1, -1, -1):
        if comparison(obj, equivalence_class.objects[i], settings):
            return i
    return None


class AlertType(object):
    SERIES_CREATED = 0
    NO_DIFFERENCE = 1
    NEW_OBJECT = 2
    EXISTING_OBJECT = 3


class Engine(object):
    def __init__(self, store, comparison=None, alert=None):
        self.store = store
        self.alert = alert
        self.classes = {}
        self.comparison = comparison or BaseComparison()
        store_classes, store_series, store_settings = self.store.load_data()
        for each in store_classes:
            c = EquivalenceClass(each)
            c.objects.extend(store_classes[each])
            self.classes[each] = c
        self.series = {}
        for each in store_series:
            c = self.classes[paths.get_equivalence_class_name(each)]
            s = Series(each, c)
            if each in store_settings:
                s.comparison_settings = store_settings[each]
            c.series.append(s)
            s.records.extend(store_series[each][0])
            s.ideal = store_series[each][1]
            self.series[each] = s
        self.top_group = Group('')
        self.groups = {'': self.top_group}
        for each in self.series:
            self._create_groups(self.series[each])
        for each in self.groups:
            if each in store_settings:
                self.groups[each].comparison_settings = store_settings[each]
        self.queue = ComparisonQueue()
        self.workers = []
        for i in xrange(8):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            t.start()
            self.workers.append(t)

    def _worker(self):
        while True:
            self.queue.get(self._add_object)

    def _create_groups(self, series):
        group = self.top_group
        components = paths.split(series.path)
        del components[-1]
        for each in components:
            if each not in group.subgroups_by_name:
                g = Group(paths.join(group.path, each))
                group.subgroups.append(g)
                group.subgroups_by_name[each] = g
                group = g
                self.groups[g.path] = g
            else:
                group = group.subgroups_by_name[each]
        group.series.append(series)

    def add_object(self, path, new_object, timestamp=None, comparison_settings=None, metadata=''):
        equivalence_name = paths.get_equivalence_class_name(path)
        if timestamp is None:
            timestamp = datetime.datetime.now()
        self.queue.put(equivalence_name, path, equivalence_name, new_object, timestamp, comparison_settings, metadata)

    def process_all(self):
        self.queue.join()

    def get_comparison_settings(self, path):
        if path in self.series:
            if self.series[path].comparison_settings is not None:
                return self.series[path].comparison_settings
        group = self.top_group
        groups = [group]
        if path != '':
            components = paths.split(path)
            for each in components:
                if each in group.subgroups_by_name:
                    group = group.subgroups_by_name[each]
                    groups.append(group)
        groups.reverse()
        for each in groups:
            if each.comparison_settings is not None:
                return each.comparison_settings
        return self.comparison.get_default_settings()

    def _get_comparison_settings(self, series):
        if series.comparison_settings is not None:
            return series.comparison_settings
        group = self.top_group
        groups = [group]
        components = paths.split(series.path)
        del components[-1]
        for each in components:
            group = group.subgroups_by_name[each]
            groups.append(group)
        groups.reverse()
        for each in groups:
            if each.comparison_settings is not None:
                return each.comparison_settings
        return self.comparison.get_default_settings()

    def _add_object(self, path, equivalence_name, new_object, timestamp, comparison_settings, metadata):
        if equivalence_name not in self.classes:
            self.classes[equivalence_name] = EquivalenceClass(equivalence_name)
        if path not in self.series:
            self.series[path] = Series(path, self.classes[equivalence_name])
            self.classes[equivalence_name].series.append(self.series[path])
            self._create_groups(self.series[path])
        series = self.series[path]
        if comparison_settings is not None:
            series.comparison_settings = comparison_settings
        comparison_settings = self._get_comparison_settings(series)
        eq_class = series.equivalence_class
        index = _get_object_index_in_class(eq_class, new_object, self.comparison.compare, comparison_settings)
        if index is None:
            index = len(eq_class.objects)
            self.store.add_class_object(eq_class.name, len(eq_class.objects), new_object)
            eq_class.objects.append(new_object)
        else:
            self.store.dispose_object(new_object)
        self.store.add_series_record(series.path, index, timestamp, metadata)
        series.records.append(SeriesRecord(timestamp, index, metadata))
        if self.alert:
            self.alert(series)

    def get_series(self, path):
        return self.series[path]

    def get_equivalence_class(self, path):
        return self.classes[path]

    def get_equivalent_series(self, path):
        series = self.get_series(path)
        for each in series.equivalence_class.series:
            if each == series:
                continue
            yield each

    def get_equivalent_groups(self, path):
        if path == '':
            return
        class_name = paths.get_equivalence_class_name(path)
        for each in self.groups:
            if each != path and each != '' and paths.get_equivalence_class_name(each) == class_name:
                yield self.groups[each]

    def get_top_level_group(self):
        return self.top_group

    def get_group(self, path):
        return self.groups[path]

    def find_groups(self, substr):
        substr = substr.lower()
        for each in self.groups:
            if substr in each.lower():
                yield self.groups[each]

    def find_series(self, substr):
        substr = substr.lower()
        for each in self.series:
            if substr in each.lower():
                yield self.series[each]

    def set_comparison_settings(self, path, settings):
        if path in self.series:
            self.series[path].comparison_settings = settings
        if path in self.groups:
            self.groups[path].comparison_settings = settings
        self.store.set_comparison_settings(path, settings)

    def set_series_ideal(self, path, ideal_index):
        series = self.series[path]
        if ideal_index < 0 or ideal_index >= len(series.records):
            raise IndexError()
        series.ideal = ideal_index
        self.store.set_ideal(path, ideal_index)

    def get_processing_queue(self):
        return [x[1][0] for x in self.queue.queue]

    def _delete_class_for_series(self, series):
        c = series.equivalence_class
        c.series.remove(series)
        if len(c.series) == 0:
            del self.classes[c.name]
            return [(store.DELETE_CLASS, c.name)]
        return []

    def _delete_parent_groups(self, path):
        series = self.series[path]
        components = paths.split(path)
        self.groups[paths.join(*components[:-1])].series.remove(series)
        for i in range(len(components) - 2, -1, -1):
            p = paths.join(*components[:i + 1])
            g = self.groups[p]
            if len(g.subgroups) == 0 and len(g.series) == 0:
                del self.groups[p]
                parent = self.groups[paths.join(*components[:i])]
                del parent.subgroups_by_name[components[i]]
                parent.subgroups.remove(g)
            else:
                break

    def _delete_series(self, path):
        to_delete = [(store.DELETE_SERIES, path)]
        series = self.series[path]
        self._delete_parent_groups(path)
        del self.series[path]
        to_delete.extend(self._delete_class_for_series(series))
        return to_delete

    def delete_series(self, path):
        self.store.delete(self._delete_series(path))

    def delete_group(self, path):
        if path == '':
            raise RuntimeError('can not delete top group')
        group = self.groups[path]
        series = [x.path for x in group.descendant_series]
        to_delete = []
        for each in series:
            to_delete.extend(self._delete_series(each))
        self.store.delete(to_delete)

    def get_ancestors(self, group_or_series):
        components = paths.split(group_or_series.path)
        ancestors = []
        for i in xrange(1, len(components)):
            path = '.'.join(components[0:i])
            ancestors.append(self.get_group(path))
        return ancestors