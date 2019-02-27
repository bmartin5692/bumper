#!/usr/bin/env python3

from threading import Thread
import sys, socket, threading, re, time, logging, uuid, xml.etree.ElementTree as ET
import base64
import ssl
import contextvars
import bumper

xmppserverlog = logging.getLogger("xmppserver")


class XMPPServer:
    server_id = "ecouser.net"
    client_id = None
    clients = []
    exit_flag = False

    def __init__(
        self,
        address,
        bumper_users=contextvars.ContextVar,
        bumper_bots=contextvars.ContextVar,
        bumper_clients=contextvars.ContextVar,
    ):
        # Initialize bot server
        self.address = address
        self.bumper_users = bumper_users
        self.bumper_bots = bumper_bots
        self.bumper_clients = bumper_clients

    def run(self, run_async=False):
        if run_async:
            xmppserverlog.debug("Starting XMPPServer Thread: 1")
            self.xmppthread = Thread(name="XMPPServer_Thread", target=self.run_server)
            self.xmppthread.setDaemon(True)
            self.xmppthread.start()

        else:
            try:
                self.run_server()
            except KeyboardInterrupt:
                self.disconnect()

    def run_server(self):
        logging.info("Starting XMPP Server at {}".format(self.address))
        print("Starting XMPP Server at {}".format(self.address))

        # xmppserverlog.setLevel(logging.DEBUG)

        # Set SSL Context
        self.ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        self.ssl_ctx.load_cert_chain(
            certfile=bumper.server_cert, keyfile=bumper.server_key
        )

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket.bind(self.address)
            self.socket.listen(5)

            xmppserverlog.debug(
                "listening on {}:{}".format(self.address[0], self.address[1])
            )
            while not self.exit_flag:
                connection, client_address = self.socket.accept()

                # disconnect any clients with this ip
                for client in self.clients:
                    if client.address == client_address[0]:
                        xmppserverlog.debug(
                            "disconnecting existing client {} with resource {}".format(
                                client.address, client.clientresource
                            )
                        )
                        client._disconnect()
                        self.remove_client_byip(client.address)

                xmppserverlog.debug(
                    "starting new client with ip {}".format(client_address[0])
                )
                thread_id = uuid.uuid4()
                client = Client(
                    thread_id,
                    connection,
                    client_address,
                    self.bumper_users,
                    self.bumper_bots,
                    self.bumper_clients,
                )
                client.setDaemon(True)
                client.start()
                self.clients.append(client)

        except PermissionError as e:
            if "bind" in e.strerror:
                xmppserverlog.exception(
                    "Error binding XMPPServer, exiting. Try using a different hostname or IP - {}".format(
                        e
                    )
                )
                exit(1)

        except Exception as e:
            xmppserverlog.exception("{}".format(e))
            exit(1)

        except KeyboardInterrupt as e:
            xmppserverlog.exception("{}".format(e))

        finally:
            connection.shutdown(socket.SHUT_RDWR)
            connection.close()
            self.disconnect()
            xmppserverlog.info("disconnecting")

        self.socket.close()

    def disconnect(self):
        try:
            xmppserverlog.debug("waiting for all client threads to exit")
            for client in self.clients:
                client._disconnect()

            self.exit_flag = True
            xmppserverlog.debug("shutting down")

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def remove_client_byip(self, ip):
        for client in self.clients:
            if client.address == ip:
                xmppserverlog.debug(
                    "removing client from client list with ip {} and resource {}".format(
                        client.address, client.clientresource
                    )
                )
                client._disconnect()
                self.clients.remove(client)

    def remove_client_byresource(self, resource):
        for client in self.clients:
            if str(client.clientresource).lower() == str(resource).lower():
                xmppserverlog.debug(
                    "removing client from client list with ip {} and resource {}".format(
                        client.address, client.clientresource
                    )
                )
                client._disconnect()
                self.clients.remove(client)

    def remove_client_byuid(self, uid):
        for client in self.clients:
            if str(client.uid).lower() == str(uid).lower():
                xmppserverlog.debug(
                    "removing client from client list with ip {} and resource {}".format(
                        client.address, client.clientresource
                    )
                )
                client._disconnect()
                self.clients.remove(client)


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

    def __init__(
        self,
        thread_id,
        connection,
        client_address,
        bumper_users=contextvars.ContextVar,
        bumper_bots=contextvars.ContextVar,
        bumper_clients=contextvars.ContextVar,
    ):
        threading.Thread.__init__(self)
        self.id = thread_id
        self.name = "XMPP_Client_{}".format(client_address[0])
        self.type = self.UNKNOWN
        self.state = self.IDLE
        self.connection = connection
        self.address = client_address[0]
        self.clientresource = ""
        self.devclass = ""
        self.bumper_jid = ""
        self.uid = ""
        self.log_sent_message = False  # Set to true to log sends
        self.log_incoming_data = True  # Set to true to log sends
        self.bumper_users = bumper_users
        self.bumper_bots = bumper_bots
        self.bumper_clients = bumper_clients

        xmppserverlog.debug(
            "new client thread init for client with ip {}".format(self.address)
        )

    def send(self, command):
        try:
            if not self.connection._closed:
                if self.log_sent_message:
                    xmppserverlog.debug("send {} - {}".format(self.address, command))
                self.connection.send(command.encode())

        except OSError as e:
            xmppserverlog.error("{}".format(e))

        except BrokenPipeError as e:
            xmppserverlog.error("{}".format(e))
            self._set_state('DISCONNECT')

        except ConnectionResetError as e:
            xmppserverlog.error("{}".format(e))
            # self._set_state('DISCONNECT')

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _disconnect(self):
        try:
            bumper_bots = self.bumper_bots.get()
            bumper_clients = self.bumper_clients.get()
            for bot in bumper_bots:
                if self.uid == bot.did:
                    bot.xmpp_connection = False
                    # xmppserverlog.info("bot disconnected {}".format(bot.did))

            self.bumper_bots.set(bumper_bots)

            for client in bumper_clients:
                if self.uid == client.userid and client.userid != "helper1":
                    client.xmpp_connection = False
                    # xmppserverlog.info("client disconnected {}".format(client.userid))

            self.bumper_clients.set(bumper_clients)
            # xmppserverlog.debug('client {} with resource {} disconnecting'.format(self.address, self.clientresource))
            self.connection.close()

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _tag_strip_uri(self, tag):
        try:
            if tag[0] == "{":
                uri, ignore, tag = tag[1:].partition("}")
            return tag

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _set_state(self, state):
        try:
            new_state = getattr(Client, state)
            if self.state > new_state:
                raise Exception(
                    "{} illegal state change {}->{}".format(
                        self.address, self.state, new_state
                    )
                )

            xmppserverlog.debug("{} state: {}".format(self.address, state))

            self.state = new_state

            if new_state == 5:
                self._disconnect()

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _handle_ctl(self, xml, data):
        try:

            if "roster" in data:
                # Return not-implemented for roster
                self.send(
                    '<iq type="error" id="{}"><error type="cancel" code="501"><feature-not-implemented xmlns="urn:ietf:params:xml:ns:xmpp-stanzas"/></error></iq>'.format(
                        xml.get("id")
                    )
                )
                return

            if xml.get("type") == "set":
                if (
                    "com:sf" in data
                    and xml.get("to") == "rl.ecorobot.net"
                ):  # Android bind? Not sure what this does yet.
                    self.send(
                        '<iq id="{}" to="{}@{}/{}" from="rl.ecorobot.net" type="result"/>'.format(
                            xml.get("id"),
                            self.uid,
                            XMPPServer.server_id,
                            self.clientresource,
                        )
                    )

            if xml[0][0]:
                ctl = xml[0][0]
                if ctl.get("admin") and self.type == self.BOT:
                    xmppserverlog.debug(
                        "admin username received from bot: {}".format(ctl.get("admin"))
                    )
                    XMPPServer.client_id = ctl.get("admin")
                    return

            # forward
            for client in XMPPServer.clients:
                if client.bumper_jid != self.bumper_jid and client.state == client.READY:                
                    ctl_to = xml.get("to")                    
                    xml.attrib["from"] = "{}".format(self.bumper_jid)
                    rxmlstring = ET.tostring(xml).decode("utf-8")
                    #clean up string to remove namespaces added by ET
                    rxmlstring = rxmlstring.replace("xmlns:ns0=", "xmlns=")
                    rxmlstring = rxmlstring.replace("ns0:", "")
                    rxmlstring = rxmlstring.replace('iq xmlns="com:ctl"', "iq")
                    rxmlstring = rxmlstring.replace('<query','<query xmlns="com:ctl"')
                    
                    if client.type == self.BOT:
                        if client.uid.lower() in ctl_to.lower():
                            xmppserverlog.info("Sending ctl to bot: {}".format(rxmlstring))
                            client.send(rxmlstring)


        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _handle_ping(self, xml, data):
        try:
            if xml.get("to").find("@") == -1: #No to address
                # Ping to server - respond
                pingresp = '<iq type="result" id="{}" from="{}" />'.format(
                        xml.get("id"), xml.get("to")
                    )
                #xmppserverlog.debug("Server Ping resp: {}".format(pingresp))
                self.send(pingresp)                

            else:
                pingto = xml.get("to")
                pingfrom = self.bumper_jid
                
                xml.attrib["from"] = pingfrom
                pingstring = ET.tostring(xml).decode("utf-8")
                #clean up string to remove namespaces added by ET
                pingstring = pingstring.replace("xmlns:ns0=", "xmlns=")
                pingstring = pingstring.replace("ns0:", "")
                pingstring = pingstring.replace('iq xmlns="com:ctl"', "iq")
                pingstring = pingstring.replace('<query','<query xmlns="com:ctl"')

                for client in XMPPServer.clients:
                    if client.bumper_jid != self.bumper_jid and client.state == client.READY:                    
                        if pingto.lower() in client.bumper_jid.lower():                            
                            pingsend = '<iq type="result" id="{}" from="{}" to="{}" />'.format(
                                xml.get("id"), pingfrom, pingto
                            )
                            xmppserverlog.debug("ping from {} to {}".format(pingfrom, pingto))
                            client.send(pingstring)                       

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _handle_result(self, xml, data):
        try:
            ctl_to = xml.get("to")
            xml.attrib["from"] = self.bumper_jid
            if "errno='103' error='permission denied," in data: #No permissions, usually if bot was last on Ecovac network                
                if self.type == self.BOT:                                                          
                    xquery = xml.getchildren()
                    ctl = xquery[0].getchildren()
                    ctlerr = ctl[0].attrib["error"]
                    adminuser = ctlerr.replace("permission denied, please contact ","")
                    adminuser = adminuser.replace(" ","")
                    if not (adminuser.startswith("fuid_") or bumper.use_auth): #if not fuid_ then its ecovacs OR ignore bumper auth
                        #TODO: Implement auth later, should this user have access to bot?
                        
                        #Add user jid to bot
                        newuser = ctl_to.split("/")[0]
                        adduser = '<iq type="set" id="{}" from="{}" to="{}"><query xmlns="com:ctl"><ctl td="AddUser" id="0000" jid="{}" /></query></iq>'.format(
                                uuid.uuid4(), adminuser, self.bumper_jid, newuser)
                        xmppserverlog.debug("Add User: {}".format(adduser))
                        self.send(adduser)
                        
                        #Add user ACs - Manage users, settings, and clean (full access)
                        adduseracs = '<iq type="set" id="{}" from="{}" to="{}"><query xmlns="com:ctl"><ctl td="SetAC" id="1111" jid="{}"><acs><ac name="userman" allow="1"/><ac name="setting" allow="1"/><ac name="clean" allow="1"/></acs></ctl></query></iq>'.format(
                                uuid.uuid4(), adminuser, self.bumper_jid, newuser)
                        xmppserverlog.debug("Add User ACs: {}".format(adduseracs))
                        self.send(adduseracs)

                        #GetUserInfo - Just to confirm it set correctly                                                            
                        self.send(          
                            '<iq type="set" id="{}" from="{}" to="{}"><query xmlns="com:ctl"><ctl td="GetUserInfo" id="4444" /><UserInfos/></query></iq>'.format(
                                uuid.uuid4(), adminuser, self.bumper_jid)
                        )
                                                        
            else:   
                rxmlstring = ET.tostring(xml).decode("utf-8")
                #clean up string to remove namespaces added by ET
                rxmlstring = rxmlstring.replace("xmlns:ns0=", "xmlns=")
                rxmlstring = rxmlstring.replace("ns0:", "")
                rxmlstring = rxmlstring.replace('iq xmlns="com:ctl"', "iq")
                rxmlstring = rxmlstring.replace('<query','<query xmlns="com:ctl"')
                if self.type == self.BOT:
                    if ctl_to == "de.ecorobot.net": #Send to all clients
                        xmppserverlog.debug("Sending to all clients because of de: {}".format(rxmlstring))
                        for client in XMPPServer.clients:
                            client.send(rxmlstring)                   
                
                if xml.get("to").find("@") == -1: #No to address
                    ctl_to = xml.get("to")
                else:
                    ctl_to = "{}@ecouser.net".format(ctl_to.split("@")[0])                
                
                for client in XMPPServer.clients:
                    if client.bumper_jid != self.bumper_jid and client.state == client.READY:
                        if not "@" in ctl_to: #No user@, send to all clients?
                            #TODO: Revisit later, this may be wrong
                            client.send(rxmlstring) 

                        elif client.uid.lower() in ctl_to.lower(): #If client matches TO=
                            xmppserverlog.debug("Sending from {} to client {}: {}".format(self.uid, client.uid, rxmlstring))
                            client.send(rxmlstring)                        

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _handle_connect(self, data, xml=None):
        try:

            if self.state == self.CONNECT:
                if xml == None:
                    # Client first connecting, send our features
                    if data.decode("utf-8").find("jabber:client") > -1:
                        sc = data.decode("utf-8").find("to=")
                        ec = data.decode("utf-8").find(".ecorobot.net")
                        if ec > -1:                    
                            self.devclass = data.decode("utf-8")[sc+4:ec]
                        # ack jabbr:client
                        # no STARTTLS
                        self.send(
                            '<stream:stream xmlns:stream="http://etherx.jabber.org/streams" xmlns="jabber:client" version="1.0" id="1" from="{}">'.format(
                                XMPPServer.server_id
                            )
                        )
                        # with STARTTLS
                        # self.send('<stream:stream xmlns:stream="http://etherx.jabber.org/streams" xmlns:tls="http://www.ietf.org/rfc/rfc2595.txt" xmlns="jabber:client" version="1.0" id="1" from="{}">'.format(XMPPServer.server_id))
                        time.sleep(0.25)
                        # send authentication support for iq-auth (fallback) and SASL
                        self.send(
                            '<stream:features><auth xmlns="http://jabber.org/features/iq-auth"/><mechanisms xmlns="urn:ietf:params:xml:ns:xmpp-sasl"><mechanism>PLAIN</mechanism></mechanisms></stream:features>'
                        )
                        # self.send('<stream:features><auth xmlns="http://jabber.org/features/iq-auth"/></stream:features>')

                    else:
                        self.send("</stream>")
                
                else:
                    if "jabber:iq:auth" in xml.tag: # Handle iq-auth                
                        self._handle_iq_auth(xml)
                    elif "urn:ietf:params:xml:ns:xmpp-sasl" in xml.tag: #Handle SASL Auth
                        self._handle_sasl_auth(xml)          
                    else:
                        xmppserverlog.error("Couldn't handle: {}".format(xml))

            elif self.state == self.INIT:
                if xml == None:
                    # Client getting session after authentication
                    if data.decode("utf-8").find("jabber:client") > -1:
                        # ack jabbr:client
                        self.send(
                            '<stream:stream xmlns:stream="http://etherx.jabber.org/streams" xmlns="jabber:client" version="1.0" id="1" from="{}">'.format(
                                XMPPServer.server_id
                            )
                        )
                        time.sleep(0.25)
                        # session
                        self.send(
                            '<stream:features><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"/><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></stream:features>'
                        )

                else:  # Handle init bind        
                    if len(xml):
                        child = self._tag_strip_uri(xml[0].tag)   
                    else:
                        child = None

                    if xml.tag == "iq":
                        if child == "bind":
                            self._handle_bind(xml)                                                
                    else:
                        xmppserverlog.error("Couldn't handle: {}".format(xml))
                    
                            

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _handle_iq_auth(self, data):
        try:
            xml = ET.fromstring(data.decode("utf-8"))
            ctl = xml[0][0]
            xmppserverlog.info("IQ AUTH XML: {}".format(xml))
            # Received username and auth tag, send username/password requirement
            if (
                xml.get("type") == "get"
                and "auth}username" in ctl.tag
                and self.type == self.UNKNOWN
            ):
                self.send(
                    '<iq type="result" id="{}"><query xmlns="jabber:iq:auth"><username/><password/></query></iq>'.format(
                        xml.get("id")
                    )
                )

            # Received username, password, resource - Handle auth here and return pass or fail
            if (
                xml.get("type") == "set"
                and "auth}username" in ctl.tag
                and self.type == self.UNKNOWN
            ):
                xmlauth = xml[0].getchildren()
                uid = ""
                password = ""
                resource = ""
                for aitem in xmlauth:
                    if "username" in aitem.tag:
                        self.uid = aitem.text

                    elif "password" in aitem.tag:
                        password = aitem.text.split("/")[2]
                        authcode = password

                    elif "resource" in aitem.tag:
                        self.clientresource = aitem.text
                        resource = self.clientresource

                if not self.uid.startswith("fuid"):

                    # Need sample data to see details here
                    bumper.add_bot("", self.uid, "", resource)
                    xmppserverlog.info("bot authenticated {}".format(self.uid))

                    # Client authenticated, move to next state
                    self._set_state("INIT")

                    # Successful auth
                    self.send('<iq type="result" id="{}"/>'.format(xml.get("id")))

                else:
                    auth = False
                    if bumper.check_authcode(self.uid, authcode):
                        auth = True
                    elif bumper.use_auth == False:
                        auth = True

                    if auth:
                        bumper.add_client(self.uid, "bumper", self.clientresource)
                        xmppserverlog.debug("client authenticated {}".format(self.uid))

                        # Client authenticated, move to next state
                        self._set_state("INIT")

                        # Successful auth
                        self.send('<iq type="result" id="{}"/>'.format(xml.get("id")))

                    else:
                        # Failed auth
                        self.send(
                            '<iq type="error" id="{}"><error code="401" type="auth"><not-authorized xmlns="urn:ietf:params:xml:ns:xmpp-stanzas"/></error></iq>'.format(
                                xml.get("id")
                            )
                        )

        except ET.ParseError as e:
            if "no element found" in e.msg:
                xmppserverlog.debug(
                    "xml parse error - {} - {}".format(
                        data.decode("utf-8"), e
                    )
                )
            elif "not well-formed (invalid token)" in e.msg:
                xmppserverlog.debug(
                    "xml parse error - {} - {}".format(data.decode("utf-8"), e)
                )
            else:
                xmppserverlog.debug(
                    "xml parse error - {} - {}".format(data.decode("utf-8"), e)
                )

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _handle_sasl_auth(self, xml):
        try:            
            
            saslauth = base64.b64decode(xml.text).decode("utf-8").split("/") 
            username = saslauth[0]
            username = saslauth[0].split("\x00")[1]
            self.uid = username
            if len(saslauth) > 1:
                resource = saslauth[1]
                self.clientresource = resource
            elif len(saslauth[0].split("\x00")) > 2:
                resource = saslauth[0].split("\x00")[2]
                self.clientresource = resource
            
            if len(saslauth) > 2:
                authcode = saslauth[2]

            if not self.uid.startswith("fuid"):
                # Need sample data to see details here
                bumper.add_bot(self.uid, self.uid, self.devclass, "atom","eco-legacy")
                self.type = self.BOT
                xmppserverlog.info("bot authenticated {}".format(self.uid))
                # Send response
                self.send(
                    '<success xmlns="urn:ietf:params:xml:ns:xmpp-sasl"/>'
                )  # Success

                # Client authenticated, move to next state
                self._set_state("INIT")

            else:
                auth = False
                if bumper.check_authcode(self.uid, authcode):
                    auth = True
                elif bumper.use_auth == False:
                    auth = True

                if auth:
                    self.type = self.CONTROLLER
                    bumper.add_client(self.uid, "bumper", self.clientresource)
                    xmppserverlog.debug("client authenticated {}".format(self.uid))

                    # Client authenticated, move to next state
                    self._set_state("INIT")

                    # Send response
                    self.send(
                        '<success xmlns="urn:ietf:params:xml:ns:xmpp-sasl"/>'
                    )  # Success

                else:
                    # Failed to authenticate
                    self.send(
                        '<response xmlns="urn:ietf:params:xml:ns:xmpp-sasl"/>'
                    )  # Fail

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _handle_bind(self, xml):
        try:
            bumper_bots = self.bumper_bots.get()
            bumper_clients = self.bumper_clients.get()

            for bot in bumper_bots:
                if self.uid == bot.did:
                    bot.xmpp_connection = True
                    # xmppserverlog.info("bot connected {}".format(bot.did))
                    self.bumper_bots.set(bumper_bots)

            for client in bumper_clients:
                if self.uid == client.userid:
                    client.xmpp_connection = True
                    # xmppserverlog.info("client connected {}".format(client.userid))
                    self.bumper_clients.set(bumper_clients)

            clientbindxml = xml.getchildren()
            clientresourcexml = clientbindxml[0].getchildren()
            if self.devclass: #its a bot
                self.name = "XMPP_Client_{}_{}".format(self.uid,self.devclass)
                self.bumper_jid = "{}@{}.ecorobot.net/atom".format(self.uid, self.devclass)                    
                xmppserverlog.debug("new bot {}".format(self.uid))
                res = '<iq type="result" id="{}"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"><jid>{}</jid></bind></iq>'.format(
                    xml.get("id"), self.bumper_jid
                )
            elif len(clientresourcexml) > 0:
                self.clientresource = clientresourcexml[0].text
                self.name = "XMPP_Client_{}".format(self.clientresource)
                self.bumper_jid = "{}@{}/{}".format(self.uid, XMPPServer.server_id, self.clientresource)
                xmppserverlog.debug(
                    "new client {} using resource {}".format(
                        self.uid, self.clientresource
                    )
                )
                res = '<iq type="result" id="{}"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"><jid>{}</jid></bind></iq>'.format(
                    xml.get("id"), self.bumper_jid
                )
            else:                            
                self.name = "XMPP_Client_{}_{}".format(self.uid,self.address)
                self.bumper_jid = "{}@{}".format(self.uid, XMPPServer.server_id)
                xmppserverlog.debug("new client {}".format(self.uid))
                res = '<iq type="result" id="{}"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"><jid>{}</jid></bind></iq>'.format(
                    xml.get("id"), self.bumper_jid
                )

            self._set_state("BIND")
            self.send(res)

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _handle_session(self, xml):
        try:
            res = '<iq type="result" id="{}" />'.format(xml.get("id"))
            self._set_state("READY")
            self.send(res)

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _handle_presence(self, xml):
        try:
           
            if len(xml) and xml[0].tag == "status":
                xmppserverlog.debug(
                "bot presence {} ".format(ET.tostring(xml, encoding="utf-8"))
                )
                #Most likely a bot, possibly hello world in text
                
                #Send dummy return
                self.send(
                    '<presence to="{}"> dummy </presence>'.format(
                        self.bumper_jid
                    )
                )

                #If it is a BOT, send extras
                if self.type == self.BOT:
                    #get device info                    
                    self.send(
                        '<iq type="set" id="14" to="{}" from="{}"><query xmlns="com:ctl"><ctl td="GetDeviceInfo"/></query></iq>'.format(
                            self.bumper_jid, XMPPServer.server_id
                        )
                    )                                                           

            else:  
                xmppserverlog.debug(
                        "client presence - {} ".format(ET.tostring(xml, encoding="utf-8"))
                )                              
                
                if xml.get("type") == "available":
                    xmppserverlog.debug(
                        "client presence available - {} ".format(ET.tostring(xml, encoding="utf-8"))
                    )
                   #Send dummy return
                    self.send(
                        '<presence to="{}"> dummy </presence>'.format(
                            self.bumper_jid
                        )
                    )
                elif xml.get("type") == "unavailable":
                    xmppserverlog.debug(
                        "client presence unavailable (DISCONNECT) - {} ".format(ET.tostring(xml, encoding="utf-8"))
                    )
                    
                    self._set_state("DISCONNECT")
                else:
                    #Sometimes the android app sends these
                    xmppserverlog.debug(
                        "client presence (UNKNOWN) - {} ".format(ET.tostring(xml, encoding="utf-8"))
                    )
                    #Send dummy return
                    self.send(
                        '<presence to="{}"> dummy </presence>'.format(
                            self.bumper_jid
                        )
                    )
                

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _parse_data(self, data):        

    
        if data.decode("utf-8").startswith("<?xml"): #Strip <?xml and add artificial root 
            newdata = re.sub(r"(<\?xml[^>]+\?>)", r"<root>",data.decode("utf-8")) + "</root>"            
            
        else:
            newdata = "<root>{}</root>".format(data.decode("utf-8")) #Add artificial root                                                                                                                          
        
        try:            
            root = ET.fromstring(newdata)
            for item in root.iter():
                if item.tag != "root":
                    if item.tag == "iq":
                        if self.log_incoming_data:
                            xmppserverlog.debug(
                                "from {} - {}".format(self.address, str(ET.tostring(item, encoding="utf-8").decode("utf-8")).replace("ns0:",""))
                            ) 
                        self._handle_iq(item, newdata)
                        item.clear()

                    elif "auth" in item.tag:
                        if "urn:ietf:params:xml:ns:xmpp-sasl" in item.tag: #SASL Auth                            
                            self._handle_sasl_auth(item)
                            item.clear()

                    elif "presence" in item.tag:
                        self._handle_presence(item)   
                        item.clear()

                    else:                    
                        if self.log_incoming_data:
                                xmppserverlog.debug(
                                    "Unparsed Item - {}".format(str(ET.tostring(item, encoding="utf-8").decode("utf-8")).replace("ns0:",""))
                        )                                                     
                        print("e")                                               
                               
        except ET.ParseError as e:
            if (
                "no element found" in e.msg
            ):  # Element not closed or not all bytes received
                # Happens wth connect stream often
                if "<stream:stream " in newdata:
                    if self.state == self.CONNECT or self.state == self.INIT:
                        self._handle_connect(newdata.encode("utf-8"))
                else:
                    if not (newdata == "" or newdata == " "):
                        xmppserverlog.error(
                            "xml parse error - {} - {}".format(newdata, e)
                        )

            elif "not well-formed (invalid token)" in e.msg:
                # If a lone </stream:stream> - client is signalling end of session/disconnect
                if not "</stream:stream>" in newdata:
                    xmppserverlog.error(
                        "xml parse error - {} - {}".format(newdata, e)
                    )
                else:
                    self.send("</stream:stream>")  # Close stream
    
            else:
                if "<stream:stream" in newdata: #Handle start stream and connect
                    if self.state == self.CONNECT or self.state == self.INIT:
                        xmppserverlog.debug(
                            "Handling connect data - {}".format(newdata)
                        )
                        self._handle_connect(newdata.encode("utf-8"))
                else:
                    if not "</stream:stream>" in newdata:
                        xmppserverlog.error(
                        "xml parse error - {} - {}".format(newdata, e)
                    )
                    else:                        
                        self.send("</stream:stream>")  # Close stream
                        self._set_state("DISCONNECT")
                   

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def _handle_iq(self, xml, data):
        try:
            if len(xml):
                child = self._tag_strip_uri(xml[0].tag)
            else:
                child = None

            if xml.tag == "iq":
                if child == "bind":
                    self._handle_bind(xml)
                elif child == "session":
                    self._handle_session(xml)
                elif child == "ping":
                    self._handle_ping(xml, data)
                elif child == "query":                    
                    if self.type == self.BOT:  
                        self._handle_result(xml, data)
                    else:
                        self._handle_ctl(xml, data)
                elif xml.get("type") == "result":
                    if self.type == self.BOT:  
                        self._handle_result(xml, data)       
                    else:
                        self._handle_result(xml, data)       
                elif xml.get("type") == "set":                                 
                    if self.type == self.BOT:  
                        self._handle_result(xml, data)       
                    else:
                        self._handle_result(xml, data)                                                       

        except Exception as e:
            xmppserverlog.exception("{}".format(e))

    def run(self):
        # xmppserverlog.info('client connected - {}'.format(self.address))
        self._set_state("CONNECT")
        while not self.state == self.DISCONNECT and not self.connection._closed:
            data = b""
            time.sleep(0.1)
            if not self.connection._closed:
                try:
                    data = self.connection.recv(4096)            
                    if data != b"":                
                        self._parse_data(data)
                except ConnectionResetError as e:
                    xmppserverlog.error("{}".format(e))
                except OSError as e:
                    xmppserverlog.error("{}".format(e))
                except Exception as e:
                    xmppserverlog.exception("{}".format(e))

            
                
