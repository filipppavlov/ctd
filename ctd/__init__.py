from flask import Flask, render_template
import time

import comparisons.engine
import comparisons.filestore
from imageref.imageref import ImageComparison, ImageRefSerializer
from thumbnails import Thumbnails
from emailalert.emailalert import EmailAlert

try:
    import config
except ImportError:
    import config_default as config


def render_email(to, record):
    with app.app_context():
        return render_template('email.html', to=to, series=record)

email_alerts = EmailAlert(config.ALERT_FILE, config.EMAIL_FROM, config.EMAIL_SUBJECT, render_email, config.EMAIL_PERIOD)
engine = comparisons.engine.Engine(comparisons.filestore.FileStore(config.ENGINE_DIR,
                                                                   ImageRefSerializer(config.TEMP_UPLOAD_DIR,
                                                                                      config.IMAGES_DIR)),
                                   ImageComparison(), email_alerts.alert)
thumbnails = Thumbnails()

app = Flask(__name__)
app.config.from_object(config)


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

    def get_failed_commits_for_stability_period(series):
        return series.get_difference_count(config.COMMIT_COUNT_FOR_STABILITY)

    def get_commits_for_stability_period(series):
        return config.COMMIT_COUNT_FOR_STABILITY

    return {'get_last_commit_result': get_last_commit_result, 'get_equivalent_groups': get_equivalent_groups,
            'get_equivalent_series': get_equivalent_series,
            'get_failed_commits_for_stability_period': get_failed_commits_for_stability_period,
            'get_commits_for_stability_period': get_commits_for_stability_period}

# noinspection PyUnresolvedReferences
import ctd.views
# noinspection PyUnresolvedReferences
import ctd.rest
