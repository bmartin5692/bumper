#!/usr/bin/env python3

import sys, socket, threading, re, time, logging, uuid, xml.etree.ElementTree as ET


class XMPPServer():
    server_id = 'bumper'
    bot_id = 'bumpy'
    client_id = None
    clients = []
    exit_flag = False

    def __init__(self, address):
        try:
            # Initialize bot server
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(address)
            self.socket.listen(1)
            logging.info('XMPPServer: listening on {}:{}'.format(address[0], address[1]))
            while not self.exit_flag:
                logging.info('XMPPServer: awaiting connection')
                connection, client_address = self.socket.accept()
                # disconnect any clients with this ip
                for client in self.clients:
                    if client.address == client_address[0]:                        
                        client.disconnect()
                        client.join()
                thread_id = uuid.uuid4()
                client = Client(thread_id, connection, client_address)
                
                client.start()
                self.clients.append(client)
            self.socket.close()
        except PermissionError as e:
            if "bind" in e.strerror:
                logging.exception("Error binding xmppserver, exiting. Try using a different hostname or IP.\r\n {}".format(e))        
            exit(1)            
        except Exception as e:
            logging.exception('XMPPServer: {}'.format(e))
            exit(1)
        except KeyboardInterrupt:
            logging.exception('XMPPServer: Keyboard interrupt')
        finally:
            self.disconnect()
            logging.info('XMPPServer: bye')

    def disconnect(self):
        try:
            logging.info('XMPPServer: waiting for all client threads to exit')
            for client in self.clients:
                client.disconnect()
                client.join()
            self.exit_flag = True
            logging.info('XMPPServer: shutting down...')
        except Exception as e:
            logging.exception("XMPPServer Exception: {}".format(e))  


class Client(threading.Thread):
    IDLE = 0
    CONNECT = 1
    INIT = 2
    BIND = 3
    READY = 4
    DISCONNECT = 5
    UNKNOWN = 0
    BOT = 1
    CONTROLLER = 2

    def __init__(self, thread_id, connection, client_address):
        threading.Thread.__init__(self)
        self.id = thread_id
        self.name = "XMPP Thread {}".format(client_address[0])
        self.type = self.UNKNOWN
        self.state = self.IDLE
        self.connection = connection
        self.address = client_address[0]
        self.clientresource = ""

    def send(self, command):
        try:
            logging.debug('XMPPServer to {}: {}'.format(self.address, command))
            self.connection.send(command.encode())
        except OSError as e:
            logging.error('XMPPServer: {}'.format(e))            
        except Exception as e:
            logging.exception("XMPPServer Exception: {}".format(e))



    def disconnect(self):
        try:
            logging.info('XMPPServer: {} with resource {} disconnecting'.format(self.address, self.clientresource))
            self.connection.close()
            self._set_state('DISCONNECT')
 
        except Exception as e:
            logging.exception("XMPPServer Exception: {}".format(e))        

    def _tag_strip_uri(self, tag):
        try:
            if tag[0] == '{':
                uri, ignore, tag = tag[1:].partition('}')
            return tag
        except Exception as e:
            logging.exception("XMPPServer Exception: {}".format(e))           

    def _set_state(self, state):
        try:
            new_state = getattr(Client, state)
            if self.state > new_state:
                raise Exception('XMPPServer: {} illegal state change {}->{}'.format(self.address, self.state, new_state))
            logging.debug('XMPPServer: {} state: {}'.format(self.address, state))
            self.state = new_state
            if new_state == '5':
                self.join()
        except Exception as e:
            logging.exception("XMPPServer: Exception: {}".format(e))            

    def _handle_ctl(self, xml, data):
        try:
            ctl = xml[0][0]
            if ctl.get('admin') and self.type == self.BOT:
                logging.debug('XMPPServer: admin username received from bot: {}'.format(ctl.get('admin')))
                XMPPServer.client_id = ctl.get('admin')
                return
            # forward
            for client in XMPPServer.clients:
                if client.address != self.address and client.state == client.READY:
                    if client.type == self.BOT:
                        data = data.decode('utf-8')
                        id_index = data.find('id')
                        if id_index > -1:
                            data = data[:id_index] + 'from="' + XMPPServer.client_id + '" ' + data[id_index:]
                            data = data.encode()
                    client.send(data.decode('utf-8'))
        except Exception as e:
            logging.exception("XMPPServer Exception: {}".format(e))


    def _handle_ping(self, xml, data):
        if(xml.get('to').find('@') == -1):
            # Ping to server - respond
            self.send('<iq type="result" id="{}" from="{}" />'.format(xml.get('id'), xml.get('to')))
        else:
            for client in XMPPServer.clients:
                if client.address != self.address and client.state == client.READY:
                    client.send(data.decode('utf-8'))

    def _handle_result(self, data):
        # forward
        try:
            for client in XMPPServer.clients:
                if client.address != self.address and client.state == client.READY:
                    client.send(data.decode('utf-8'))
        except Exception as e:
            logging.exception("XMPPServer Exception: {}".format(e))            

    def run(self):
        try:
            logging.info('XMPPServer: client connected: {}'.format(self.address))
            self._set_state('CONNECT')
            data = ""
            while True:
                time.sleep(0.2)
                if not self.connection._closed:               
                    data = self.connection.recv(4096)
                if data:
                    logging.debug('XMPPServer: from {}: {}'.format(self.address, data.decode('utf-8')))
                    try:
                        if self.state == self.CONNECT:
                            if data.decode('utf-8').find('jabber:client') > -1:
                                self._set_state('INIT')
                                # ack jabbr:client
                                self.send('<stream:stream xmlns:stream="http://etherx.jabber.org/streams" xmlns="jabber:client" version="1.0" id="1" from="{}">'.format(XMPPServer.server_id))
                                time.sleep(0.5)
                                # session
                                self.send('<stream:features><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"/><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></stream:features>')
                            continue
                        xml = ET.fromstring(data)
                        logging.debug("XMPPXML: {}".format(data))
                        if len(xml):
                            child = self._tag_strip_uri(xml[0].tag)
                        else:
                            child = None
                        if xml.tag == 'iq':
                            res = None
                            if child == 'bind':
                                clientbindxml = xml.getchildren()
                                clientresourcexml = clientbindxml[0].getchildren()
                                self.clientresource = clientresourcexml[0].text
                                self.name = "XMPP Thread {}".format(self.clientresource)
                                logging.info("XMPP Client {} using resource {}".format(self.address, self.clientresource))
                                res = '<iq type="result" id="{}"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"><jid>{}</jid></bind></iq>'.format(xml.get('id'), XMPPServer.bot_id)
                                self._set_state('BIND')
                            elif child == 'session':
                                res = '<iq type="result" id="{}" />'.format(xml.get('id'))
                                self._set_state('READY')
                            elif child == 'query':
                                self._handle_ctl(xml, data)
                            elif child == 'ping':
                                self._handle_ping(xml, data)
                            elif xml.get('type') == 'result':
                                self._handle_result(data)
                            if res:
                                self.send(res)
                        elif xml.tag == 'presence':
                            if len(xml) and xml[0].tag == 'status':
                                # bot announcing arrival
                                self.type = self.BOT
                                logging.debug('XMPPServer: {} type set to BOT (based on presence tag)'.format(self.address))
                                # send a command from an unknown user  - the response will contain the correct admin username
                                self.send('<iq type="set" id="{}" from="{}" to="{}"><query xmlns="com:ctl"><ctl td="GetCleanState" /></query></iq>'.format(uuid.uuid4(), 'unknown@ecouser.net', XMPPServer.bot_id))
                            elif xml.get('type') == 'available':
                                self.type = self.CONTROLLER
                                logging.debug('XMPPServer: {} type set to CONTROLLER (based on presence tag)'.format(self.address))
                    except ET.ParseError as e:
                        logging.debug('error: {}'.format(e))
                    except Exception as e:
                        logging.error('XMPPServer: {}'.format(e))
                        self._set_state('DISCONNECT')
        except OSError as e:
            logging.error('XMPPServer: {}'.format(e))
            self._set_state('DISCONNECT')

        except ConnectionResetError as e:
            logging.error('XMPPServer: {}'.format(e))
            self._set_state('DISCONNECT')
                        
        except Exception as e:
            logging.error('XMPPServer: {}'.format(e))
            self._set_state('DISCONNECT')
                        
        finally:
            self.disconnect()
