import json
import socket
import BaseHTTPServer
import SocketServer
import threading
import unittest
import ctdclient.client as client


class _MockServer(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, result_code, response, request, client_address, server):
        self.result_code = result_code
        self.response = response
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_POST(self):
        self.send_response(self.result_code)
        self.send_header("Content-Length", str(len(self.response)))
        self.end_headers()
        self.wfile.write(self.response)


def _run_server(result_code, response):
    def get_server(request, client_address, server):
        return _MockServer(result_code, response, request, client_address, server)

    httpd = SocketServer.TCPServer(("127.0.0.1", 8123), get_server)

    def run():
        httpd.handle_request()
    threading.Thread(target=run).start()


class TestUpload(unittest.TestCase):
    def test_providing_invalid_file_raises(self):
        with self.assertRaises(IOError):
            client.upload_image('', 'test', 'this_image_does_not_exist')

    def test_providing_invalid_server_raises(self):
        with self.assertRaises(socket.gaierror):
            client.upload_image('this_server_does_not_exist', 'test', __file__)

    def test_upload_error_when_server_returns_error_code(self):
        _run_server(500, 'bad response')
        with self.assertRaises(client.UploadError):
            self.assertEquals(client.upload_image('127.0.0.1:8123', 'test', __file__), 'bad response')

    def test_upload_error_json_response_is_parsed(self):
        response = {'filed1': 'abc', 'field2': [1, 3]}
        _run_server(500, json.dumps(response))
        with self.assertRaises(client.UploadError):
            self.assertEquals(client.upload_image('127.0.0.1:8123', 'test', __file__), response)

    def test_upload_succeeds(self):
        _run_server(200, 'my response')
        self.assertEquals(client.upload_image('127.0.0.1:8123', 'test', __file__), 'my response')

    def test_upload_json_response_is_parsed(self):
        response = {'filed1': 'abc', 'field2': [1, 3]}
        _run_server(200, json.dumps(response))
        self.assertEquals(client.upload_image('127.0.0.1:8123', 'test', __file__), response)
