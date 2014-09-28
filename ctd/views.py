import os
import tempfile
from flask import render_template, request, send_file, abort

from imageref.imageref import ImageRef
from ctd import app, engine, thumbnails


@app.route('/', defaults={'path': ''})
@app.route('/index', defaults={'path': ''})
@app.route('/group/<path>')
def group(path):
    try:
        g = engine.get_group(path)
    except KeyError:
        abort(404)
        return
    return render_template("group.html", group=g, title=g.path, page_category='group')


@app.route('/groupcompare')
def group_compare():
    g1 = engine.get_group(request.args.get('group1'))
    g2 = engine.get_group(request.args.get('group2'))
    s1 = {x.path[len(g1.path):]: x for x in g1.descendant_series}
    s2 = {x.path[len(g2.path):]: x for x in g2.descendant_series}
    pairs = []
    for each in s1:
        if each in s2:
            if s1[each].get_latest_object().index == s2[each].get_latest_object().index:
                result = 'equal'
            else:
                result = 'differ'
            pairs.append((s1[each], s2[each], each, result))
        else:
            pairs.append((s1[each], None, each, 'missing'))
    for each in s2:
        if each not in s1:
            pairs.append((None, s2[each], each, 'missing'))
    pairs.sort(key=lambda a: (a[0] or a[1]).path)
    problem_count = sum([(0 if (x[3] == 'equal') else 1) for x in pairs])
    return render_template("groupcompare.html", group1=g1, group2=g2, pairs=pairs,
                           title="%s vs %s" % (g1.path, g2.path), page_category='group',
                           problem_count=problem_count)


@app.route('/gallery', defaults={'path': ''})
@app.route('/gallery/<path>')
def gallery(path):
    try:
        g = engine.get_group(path)
    except KeyError:
        abort(404)
        return
    return render_template("gallery.html", group=g, title=g.path, page_category='gallery')


@app.route('/series/<path>')
def series(path):
    try:
        s = engine.get_series(path)
    except KeyError:
        abort(404)
        return
    return render_template("series.html", series=s, title=s.path, page_category='series')


@app.route('/image/<path>/<int:indx>')
def image(path, indx):
    try:
        s = engine.get_series(path)
    except KeyError:
        abort(404)
        return
    try:
        obj = s.get_object(indx)
    except IndexError:
        abort(404)
        return
    if request.args.get('vs'):
        vs = request.args.get('vs')
    else:
        vs = ''
    return render_template("image.html", series=s, object=obj, vs=vs, title="%s #%s" % (s.path, indx),
                           page_category='image')


@app.route('/object/<class_path>/<object_index>')
def object_contents(class_path, object_index):
    try:
        obj = engine.get_equivalence_class(class_path).get_object(int(object_index))
    except (KeyError, IndexError):
        abort(404)
        return
    return send_file(obj.path)


@app.route('/thumbnail/<class_path>/<object_index>/<int:size>')
def thumbnail(class_path, object_index, size):
    try:
        obj = engine.get_equivalence_class(class_path).get_object(int(object_index))
    except (KeyError, IndexError):
        abort(404)
        return
    return send_file(thumbnails.thumbnail(obj.path, max(size, 4)))


@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        rest_post_image(request.form['series'])
    return render_template("submit.html", title="Submit image", page_category='submit')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png']


@app.route('/image/post/<series>', methods=['POST'])
def rest_post_image(series):
    f = request.files['file']
    if f:
        if allowed_file(f.filename):
            filename = os.path.join(app.config['TEMP_UPLOAD_DIR'],
                                    tempfile.mktemp(suffix=os.path.splitext(f.filename)[1],
                                                    dir=app.config['TEMP_UPLOAD_DIR']))
            f.save(filename)
            obj = ImageRef(filename)
            metadata = request.form.get('metadata') or ''
            engine.add_object(series, obj, metadata=metadata)
            return "{\"status\": \"OK\"}", 202
        return "{\"status\": \"ERROR\", \"error\": \"Unsupported file extension\"}", 415
    return "{\"status\": \"ERROR\", \"error\": \"File missing\"}", 400


@app.route('/search')
def search():
    q = request.args.get('q', '')
    return render_template("search.html", groups=engine.find_groups(q), series=engine.find_series(q), title="Search results")