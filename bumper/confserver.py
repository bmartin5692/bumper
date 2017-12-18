#!/usr/bin/env python3

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
from http import HTTPStatus
from threading import Thread
import socket, logging, ssl, json, sys


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            self.protocol_version = 'HTTP/1.1'
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            logging.debug("Headers: " + str(self.headers))
            request_body = post_data.decode('utf-8')
            logging.debug("Request: " + request_body)
            json_body = json.loads(request_body)
            todo = json_body['todo']
            if todo == 'FindBest':
                service = json_body['service']
                if service == 'EcoMsgNew':
                    body = '{{"result":"ok","ip":"{}","port":5223}}'.format(socket.gethostbyname(socket.gethostname()))
                elif service == 'EcoUpdate':
                    body = '{"result":"ok","ip":"47.88.66.164","port":8005}'
            elif todo == 'loginByItToken':
                body = "{{'todo': 'result', 'result': 'ok', 'userId': '{}', 'resource': '{}', 'token': '{}'}}".format(json_body['userId'], json_body['resource'], json_body['token'])
            elif todo == 'GetDeviceList':
                body = "{'todo': 'result', 'result': 'ok', 'devices': [{'did': '{}', 'name': '{}', 'class': '{}', 'resource': 'atom', 'nick': None, 'company': 'eco'}]}"
            logging.debug("Response: " + body)
            body = body.encode()
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            logging.error('ConfServer: {}'.format(e))


class HTTPServerThread(HTTPServer, Thread):
    def __init__(self, server_address):
        Thread.__init__(self)
        self.server_address = server_address
        self.handler = RequestHandler
        self.exit_flag = False
    def handle_error(self, request, client_address):
        self.close_request(request)
    def run(self):
        try:
            HTTPServer.__init__(self, self.server_address, self.handler)
            logging.info('ConfServer: listening on {}:{}'.format(self.server_address[0], self.server_address[1]))
            while not self.exit_flag:
                self.handle_request()
        except Exception as e:
            logging.error('ConfServer: {}'.format(e))
    def disconnect(self):
        self.exit_flag = True
        # make a connection to
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.server_address)
        s.close()


class ConfServer():
    def __init__(self, address, ssl=False, async=True):
        try:
            self.async = async
            self.server = HTTPServerThread(address)
            if ssl:
                self.server.socket = ssl.wrap_socket(self.server.socket, keyfile='./certs/key.pem', certfile='./certs/cert.pem', server_side=True)
            if self.async:
                self.server.start()
            else:
                try:
                    self.server.run()
                except KeyboardInterrupt:
                    self.disconnect()
        except Exception as e:
            logging.error('ConfServer: {}'.format(e))
    def disconnect(self):
        logging.info('ConfServer: shutting down...')
        self.server.disconnect()
        if(self.async):
            self.server.join()
        logging.info('ConfServer: bye')
