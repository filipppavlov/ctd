import os
import tempfile
from PIL import Image



def _get_thumb_size(size, max_size):
    ratio = float(max_size) / float(max(*size))
    return int(size[0] * ratio), int(size[1] * ratio)


class Thumbnails(object):
    def __init__(self, thumbnal_dir):
        self.thumbnal_dir = thumbnal_dir
        try:
            os.makedirs(thumbnal_dir)
        except OSError:
            pass
        self.thumbs = {}
        self.file = open(os.path.join(thumbnal_dir, 'thumbs.txt'), 'a+')
        self.file.seek(0)
        for each in self.file:
            record = each.rstrip('\n').split('\t')
            self.thumbs[(record[0], int(record[1]))] = record[2]

    def thumbnail(self, source_path, max_size):
        index = (source_path, max_size)
        if index in self.thumbs:
            return self.thumbs[index]
        im = Image.open(source_path)
        im.thumbnail((max_size, max_size), Image.ANTIALIAS)
        path = tempfile.mkstemp(suffix='.png', dir=self.thumbnal_dir)[1]
        im.save(path)
        im = None
        self.thumbs[index] = path
        self.file.write('%s\t%s\t%s\n' % (index + (path, )))
        self.file.flush()
        return path
