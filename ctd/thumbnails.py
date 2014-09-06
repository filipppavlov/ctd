import os
import tempfile
from PIL import Image

THUMBNAIL_DIR = r'c:\temp\thumbs'


def _get_thumb_size(size, max_size):
    ratio = float(max_size) / float(max(*size))
    return int(size[0] * ratio), int(size[1] * ratio)


class Thumbnails(object):
    def __init__(self):
        try:
            os.makedirs(THUMBNAIL_DIR)
        except OSError:
            pass
        self.thumbs = {}
        self.file = open(os.path.join(THUMBNAIL_DIR, 'thumbs.txt'), 'a+')
        self.file.seek(0)
        for each in self.file:
            record = each.rstrip('\n').split('\t')
            self.thumbs[(record[0], int(record[1]))] = record[2]

    def thumbnail(self, source_path, max_size):
        index = (source_path, max_size)
        if index in self.thumbs:
            return self.thumbs[index]
        im = Image.open(source_path)
        #im = im.resize(_get_thumb_size(im.size, max_size), Image.ANTIALIAS)
        im.thumbnail((max_size, max_size), Image.ANTIALIAS)
        path = tempfile.mkstemp(suffix='.png', dir=THUMBNAIL_DIR)[1]
        im.save(path)
        self.thumbs[index] = path
        self.file.write('%s\t%s\t%s\n' % (index + (path, )))
        self.file.flush()
        return path
