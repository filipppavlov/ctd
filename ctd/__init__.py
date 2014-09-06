from flask import Flask
import os
import time

import comparisons.engine
import comparisons.filestore
from imageref.imageref import ImageComparison, ImageRefSerializer
from thumbnails import Thumbnails
from emailalert.emailalert import EmailAlert


TEMP_UPLOAD_DIR = r'c:\temp\tempimg'
ENGINE_DIR = r'c:\temp\comp'
IMAGES_DIR = r'c:\temp\img'
ALERT_FILE = r'c:\temp\emails.txt'

try:
    os.makedirs(TEMP_UPLOAD_DIR)
except OSError:
    pass

try:
    os.makedirs(IMAGES_DIR)
except OSError:
    pass


email_alerts = EmailAlert(ALERT_FILE, 'godknows@imgdiff.com', 'Image series are unstable',
                          'Image series became unstable:\n{series}', 1)
engine = comparisons.engine.Engine(comparisons.filestore.FileStore(r'c:\temp\comp',
                                                                   ImageRefSerializer(TEMP_UPLOAD_DIR, IMAGES_DIR)),
                                   ImageComparison(), email_alerts.alert)
thumbnails = Thumbnails()

app = Flask(__name__)


@app.template_filter('date_to_millis')
def date_to_millis(d):
    """Converts a datetime object to the number of milliseconds since the unix epoch."""
    return int(time.mktime(d.timetuple())) * 1000


def get_last_commit_result(node):
    try:
        if node.is_last_commit_successful():
            return 'success'
        else:
            return 'fail'
    except IndexError:
        return 'none'


@app.context_processor
def utility_processor():
    def get_equivalent_groups(group):
        return engine.get_equivalent_groups(group.path)

    def get_equivalent_series(series):
        return engine.get_equivalent_series(series.path)

    return {'get_last_commit_result': get_last_commit_result, 'get_equivalent_groups': get_equivalent_groups,
            'get_equivalent_series': get_equivalent_series}

# noinspection PyUnresolvedReferences
import ctd.views
# noinspection PyUnresolvedReferences
import ctd.rest
