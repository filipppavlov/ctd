import os
import imagecompare

from comparisons import paths
from comparisons.comparison import BaseComparison
from comparisons.filestore import ObjectSerializer, SPECIAL_SYMBOLS


class ImageComparison(BaseComparison):
    def __init__(self):
        self.default_settings = {'max_abs_error': 0}

    def get_default_settings(self):
        return self.default_settings

    def compare(self, x, y, settings):
        try:
            result = imagecompare.compare_images(x.path, y.path)
        except RuntimeError:
            return False
        for each in result['alpha']:
            result['color'][each] = max(result['color'][each], result['alpha'][each])
        result = result['color']
        for each in self.default_settings:
            if result[each] > settings[each]:
                return False
        return True


class ImageRef(object):
    def __init__(self, path):
        self.path = path

    def __eq__(self, other):
        raise RuntimeError()

    def __ne__(self, other):
        return not self.__eq__(other)


class ImageRefSerializer(ObjectSerializer):
    def __init__(self, temp_dir, final_dir):
        self.temp_dir = os.path.normcase(os.path.abspath(temp_dir))
        self.final_dir = os.path.normcase(os.path.abspath(final_dir))
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        if not os.path.exists(final_dir):
            os.makedirs(final_dir)

    def to_string(self, equivalence_class, index, obj):
        path = os.path.normcase(os.path.abspath(obj.path))
        if os.path.commonprefix([path, self.temp_dir]) == self.temp_dir:
            class_dir = os.path.join(self.final_dir, *(paths.encode_special_symbols(x, *SPECIAL_SYMBOLS)
                                                       for x in paths.split(equivalence_class)))
            if not os.path.exists(class_dir):
                os.makedirs(class_dir)
            new_path = os.path.join(class_dir, str(index)) + os.path.splitext(path)[1]
            os.rename(path, new_path)
            obj.path = new_path
        return obj.path

    def from_string(self, equivalence_class, index, string):
        return ImageRef(string)

    def dispose(self, obj):
        os.unlink(os.path.abspath(obj.path))

    def delete_class(self, equivalence_class):
        class_dir = os.path.join(self.final_dir, *(paths.encode_special_symbols(x, *SPECIAL_SYMBOLS)
                                                   for x in paths.split(equivalence_class)))
        if os.path.exists(class_dir):
            for i in os.listdir(class_dir):
                p = os.path.join(class_dir, i)
                if not os.path.isdir(p):
                    try:
                        os.unlink(p)
                    except OSError:
                        pass
