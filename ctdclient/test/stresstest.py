from ctdclient import upload_image
import random
import os
import threading
import time


def _get_random_component():
    letters = "abcdef"  # ghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTSUVWXYZ_1234567890"
    name = ''.join((random.choice(letters) for _ in xrange(0, random.randint(1, 4))))
    if random.randint(0, 1) == 1:
        name = '(' + name + ')'
    return name


def _get_random_series(depth):
    components = (_get_random_component() for _ in xrange(0, random.randint(1, depth)))
    return '.'.join(components)


def stress_test(server, series_count, series_max_depth, upload_count, image_dir, image_count):
    series = [_get_random_series(series_max_depth) for x in xrange(0, series_count)]
    images = []
    for root, dirs, files in os.walk(image_dir):
        images.extend((os.path.join(root, x) for x in files if os.path.splitext(x)[1].lower() in ('.jpg', '.jpeg', '.png')))
    random.shuffle(images)
    images = images[:image_count]
    upload_count = [upload_count, ]

    def upload_thread():
        while upload_count[0] > 0:
            upload_count[0] -= 1
            t = time.clock()
            i = random.choice(images)
            upload_image(server, random.choice(series), i)
            print "Uploaded %s in %s sec" % (i, time.clock() - t)

    threads = [threading.Thread(target=upload_thread) for _ in range(4)]
    for i in threads:
        i.start()
    for i in threads:
        i.join()



stress_test('localhost:5000', 10, 3, 100, r'E:\Pictures\2009-01-25', 30)