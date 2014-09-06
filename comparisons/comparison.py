class BaseComparison(object):
    def get_default_settings(self):
        return {}

    def compare(self, x, y, settings):
        return x == y
