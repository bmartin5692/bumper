#!/usr/bin/env python3

from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
#from http.server import SimpleHTTPRequestHandler
from http import HTTPStatus
from threading import Thread
import socket, logging, ssl, json, sys


class RequestHandler(BaseHTTPRequestHandler):
#class RequestHandler(SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            self.protocol_version = 'HTTP/1.1'
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            logging.debug("Headers: " + str(self.headers))
            request_body = post_data.decode('utf-8')
            logging.debug("Request: " + request_body)
            json_body = json.loads(request_body)
            if "getProductIotMap" in str(self.path):
                body = {"code":0,"data":[{"classid":"dl8fht","product":{"_id":"5acb0fa87c295c0001876ecf","name":"DEEBOT 600 Series","icon":"5acc32067c295c0001876eea","UILogicId":"dl8fht","ota":False,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5acc32067c295c0001876eea"}},{"classid":"02uwxm","product":{"_id":"5ae1481e7ccd1a0001e1f69e","name":"DEEBOT OZMO Slim10 Series","icon":"5b1dddc48bc45700014035a1","UILogicId":"02uwxm","ota":False,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b1dddc48bc45700014035a1"}},{"classid":"y79a7u","product":{"_id":"5b04c0227ccd1a0001e1f6a8","name":"DEEBOT OZMO 900","icon":"5b04c0217ccd1a0001e1f6a7","UILogicId":"y79a7u","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b04c0217ccd1a0001e1f6a7"}},{"classid":"jr3pqa","product":{"_id":"5b43077b8bc457000140363e","name":"DEEBOT 711","icon":"5b5ac4cc8d5a56000111e769","UILogicId":"jr3pqa","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4cc8d5a56000111e769"}},{"classid":"uv242z","product":{"_id":"5b5149b4ac0b87000148c128","name":"DEEBOT 710","icon":"5b5ac4e45f21100001882bb9","UILogicId":"uv242z","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4e45f21100001882bb9"}},{"classid":"ls1ok3","product":{"_id":"5b6561060506b100015c8868","name":"DEEBOT 900 Series","icon":"5ba4a2cb6c2f120001c32839","UILogicId":"ls1ok3","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5ba4a2cb6c2f120001c32839"}}]}
            elif "notify_engine.do" in str(self.path):
                body = {"ret":"ok"}
            else:
                todo = json_body['todo']
                if todo == 'FindBest':
                    service = json_body['service']
                    if service == 'EcoMsgNew':
                        body = {"result":"ok","ip":socket.gethostbyname(socket.gethostname()),"port":5223}
                    elif service == 'EcoUpdate':
                        body = {"result":"ok","ip":"47.88.66.164","port":8005}
                elif todo == 'loginByItToken':
                    body = {
                            "todo": "result",
                            "result": "ok",
                            "userId": json_body["userId"],
                            "resource": json_body["resource"],
                            "token": json_body["token"]
                            }
                elif todo == 'GetDeviceList':
                    #Find a way to handle this automatically
                    #Maybe keep a list of devices from those that have checked into MQTT/XMPP/etc and return them
                    body = {
                            "devices": [
                            {
                            "class": "ls1ok3",
                            "company": "eco-ng",
                            "did": "tmpDeviceID",
                            "name": "tmpName",
                            "nick": "tmpNick",
                            "resource": "tmpResource"
                            }
                            ],
                            "result": "ok",
                            "todo": "result"
                            }
            body = json.dumps(body)
            logging.debug("Response: " + body)
            body = body.encode()
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            logging.error('ConfServer POST: {}'.format(e))

    def do_GET(self):
        try:
            self.protocol_version = 'HTTP/1.1'
            logging.debug("Path: " + self.path)
            
            if "/login?" in str(self.path):
              
                #Could implement basic auth if you wanted, or just accept anything
                #Next up parse the path for variables
                body = {
                        "code": "0000",
                        "data": {
                        "accessToken": "temp_accesstoken",
                        "country": "us",
                        "email": "null@null.com",
                        "uid": "fuid_1",
                        "username": "fusername_1"
                        },
                        "msg": "操作成功",
                        "time": 1547211900690
                        }
                        
    
            elif "/getAuthCode?" in str(self.path):
                body = {
                        "code": "0000",
                        "data": {
                        "authCode": "temp_authcode",
                        "ecovacsUid": "fuid_1"
                        },
                        "msg": "操作成功",
                        "time": 1547211900808
                        }

            elif "/checkVersion?" in str(self.path):
                body = {
                        "code": "0000",
                        "data": {
                            "c": None,
                            "img": None,
                            "r": 0,
                            "t": None,
                            "u": None,
                            "ut": 0,
                            "v": None
                        },
                        "msg": "操作成功",
                        "time": 1548829850462
                    }
            elif "/logout?" in str(self.path):
                body = {"code": "0000","data": None,"msg": "操作成功","time": 1548830041460}
            else:
                body = {}
                       
            body = json.dumps(body)
            logging.debug("Response: " + body)
            body = body.encode()
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Content-Length', len(body))
            self.end_headers()            
            self.wfile.write(body)
        except Exception as e:
            logging.error('ConfServer GET: {}'.format(e))


class HTTPServerThread(HTTPServer, Thread):
    def __init__(self, server_address):
        Thread.__init__(self)
        self.server_address = server_address
        self.handler = RequestHandler
        self.exit_flag = False
        HTTPServer.__init__(self, self.server_address, self.handler)
        
    def handle_error(self, request, client_address):
        self.close_request(request)
    def run(self):
        try:           
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
    def __init__(self, address, usessl=False, run_async=True):
        self.run_async = run_async
        self.server = HTTPServerThread(address)
        try:            
            if usessl:
                self.server.socket = ssl.wrap_socket(self.server.socket, keyfile='./certs/key.pem', certfile='./certs/cert.pem', server_side=True)
            if self.run_async:
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
        if(self.run_async):
            self.server.join()
        logging.info('ConfServer: bye')
