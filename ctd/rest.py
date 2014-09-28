import json
import time

from flask import request, url_for

from . import app, engine, email_alerts, get_last_commit_result


def _series_to_dict(series):
    r = {'url': url_for('rest_series', path=series.path, _external=True),
         'path': series.path,
         'modified': str(series.modified),
         'last_difference': str(series.get_last_difference()),
         'last_commit_result': get_last_commit_result(series),
         'commits_for_stability_period': app.config['COMMIT_COUNT_FOR_STABILITY'],
         'failed_commits_for_stability_period': series.get_difference_count(app.config['COMMIT_COUNT_FOR_STABILITY'])}
    return r


def children_to_json(group_obj):
    r = {'group': {'path': group_obj.path, 'url': url_for('rest_group', path=group_obj.path, _external=True)},
         'subgroups': [],
         'series': []}
    for each in group_obj.subgroups:
        s = _group_to_dict(each)
        r['subgroups'].append(s)
    for each in group_obj.series:
        r['series'].append(_series_to_dict(each))
    return r


def _group_to_dict(group_obj):
    r = {'url': url_for('rest_group', path=group_obj.path, _external=True),
         'path': group_obj.path,
         'modified': str(group_obj.modified),
         'last_difference': str(group_obj.get_last_difference()),
         'last_commit_result': get_last_commit_result(group_obj),
         'commits_for_stability_period': app.config['COMMIT_COUNT_FOR_STABILITY'],
         'failed_commits_for_stability_period': group_obj.get_difference_count(app.config['COMMIT_COUNT_FOR_STABILITY']),
         'children': {'url': url_for('rest_children', path=group_obj.path, _external=True)}}
    return r


@app.route('/rest/search/series')
def rest_search_series():
    return json.dumps([_series_to_dict(x) for x in engine.find_series(request.args.get('substr'))])


@app.route('/rest/search')
def rest_search():
    return json.dumps([_series_to_dict(x) for x in engine.find_series(request.args.get('substr'))] +
                      [_group_to_dict(x) for x in engine.find_groups(request.args.get('substr'))])


@app.route('/rest/group')
def rest_top_group():
    return json.dumps(_group_to_dict(engine.get_top_level_group()))


@app.route('/rest/group/<path>')
def rest_group(path):
    g = engine.get_group(path)
    return json.dumps(_group_to_dict(g))


@app.route('/rest/children')
def rest_top_children():
    return json.dumps(children_to_json(engine.get_top_level_group()))


@app.route('/rest/children/<path>')
def rest_children(path):
    return json.dumps(children_to_json(engine.get_group(path)))


@app.route('/rest/series/<path>')
def rest_series(path):
    return json.dumps(_series_to_dict(engine.get_series(path)))


@app.route('/rest/seriesobjects/<path>')
def rest_series_objects(path):
    series = engine.get_series(path)
    obj = {
        'objects': [{'index': x.index, 'metadata': x.metadata,
                     'timestamp': int(time.mktime(x.timestamp.timetuple())) * 1000, 'series_index': x.series_index}
                    for x in series],
        'url': url_for('rest_series_objects', path=path, _external=True),
        'series': {'url': url_for('rest_series', path=path, _external=True), 'path': series.path}
    }
    return json.dumps(obj)


@app.route('/rest/alerts/add')
def rest_add_alert():
    email_alerts.add_email(request.args.get('email'), request.args.get('path'))
    return "OK"


@app.route('/rest/alerts/remove')
def rest_remove_alert():
    email_alerts.remove_email(request.args.get('email'), request.args.get('path'))
    return "OK"


@app.route('/rest/alerts/list', defaults={'path': ''})
@app.route('/rest/alerts/list/<path>')
def rest_list_alerts(path):
    return json.dumps(email_alerts.get_emails(path))


@app.route('/rest/settings/group', defaults={'path': ''}, methods=['GET', 'PUT'])
@app.route('/rest/settings/group/<path>', methods=['GET', 'PUT'])
def rest_group_set_settings(path):
    if request.method == 'PUT':
        settings = {}
        for each in engine.comparison.get_default_settings():
            settings[each] = float(request.form[each])
        engine.set_comparison_settings(path, settings)
    return json.dumps(engine.get_comparison_settings(path))


@app.route('/rest/settings/ideal/<path>')
def rest_series_ideal(path):
    engine.set_series_ideal(path, request.args.get('index'))
    return "OK"


@app.route('/rest/health/queue')
def queue():
    return json.dumps(engine.get_processing_queue())