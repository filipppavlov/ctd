import httplib
import mimetypes
import os
import json


def _post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = _encode_multipart_formdata(fields, files)
    h = httplib.HTTPConnection(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    h.endheaders()
    h.send(body)
    return h.getresponse()


def _encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    boundary = '----------ThIs_Is_tHe_bouNdaRY_$'
    crlf = '\r\n'
    l = []
    for (key, value) in fields:
        l.append('--' + boundary)
        l.append('Content-Disposition: form-data; name="%s"' % key)
        l.append('')
        l.append(value)
    for (key, filename, value) in files:
        l.append('--' + boundary)
        l.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        l.append('Content-Type: %s' % _get_content_type(filename))
        l.append('')
        l.append(value)
    l.append('--' + boundary + '--')
    l.append('')
    body = crlf.join(l)
    content_type = 'multipart/form-data; boundary=%s' % boundary
    return content_type, body


def _get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


class UploadError(RuntimeError):
    def __init__(self, status, message, response):
        self.status = status
        self.message = message
        self.response = response
        super(UploadError, self).__init__(self)

    def __str__(self):
        return 'Status: %s\nResponse: %s\nMessage: %s' % (self.status, self.response, self.message)


def upload_image(server, series, image_path):
    r = _post_multipart(server, 'image/post/' + series, [],
                       [('file', os.path.basename(image_path), open(image_path, 'rb').read())])
    if r.status / 100 != 2:
        raise UploadError(status=r.status, message=r.msg, response=json.loads(r.read()))
    return json.loads(r.read())

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Uploads image to ctd server.')
    parser.add_argument('server', help='Server address')
    parser.add_argument('series', help='Series name')
    parser.add_argument('image', help='Path to image file')

    args = parser.parse_args()

    upload_image(args.server, args.series, args.image)