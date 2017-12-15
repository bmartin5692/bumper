#!/usr/bin/env python3

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
import socket, logging, _thread, json


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            self.protocol_version = 'HTTP/1.1'
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            logging.debug("Headers: " + str(self.headers))
            request_body = post_data.decode('utf-8')
            logging.debug("Request: " + request_body)
            if request_body.find('EcoMsgNew') > -1:
                body = '{{"result":"ok","ip":"{}","port":5223}}'.format(socket.gethostbyname(socket.gethostname()))
            else:
                body = '{"result":"ok","ip":"47.88.66.164","port":8005}'
            logging.debug("Response: " + body)
            body = body.encode()
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
            return
        except Exception as e:
            logging.error(e)


class ConfServer():
    def __init__(self):
        try:
            server_address = (socket.gethostbyname(socket.gethostname()), 8007)
            httpd = HTTPServer(server_address, RequestHandler)
            logging.info("ConfServer: running on http://{}:{}".format(server_address[0], server_address[1]))
            _thread.start_new_thread(httpd.serve_forever, ())
        except Exception as e:
            logging.error(e)
