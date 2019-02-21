#!/usr/bin/env python3

from .confserver import ConfServer
from .mqttserver import MQTTServer
from .mqttserver import MQTTHelperBot
from .xmppserver import XMPPServer
import asyncio
import contextvars
import time
import logging
from base64 import b64decode, b64encode

bumper_users_var = contextvars.ContextVar('bumper_users', default=[])
bumper_clients_var = contextvars.ContextVar('bumper_clients', default=[])
bumper_bots_var = contextvars.ContextVar('bumper_bots', default=[])

ca_cert = './certs/CA/cacert.pem'
server_cert = './certs/cert.pem'
server_key = './certs/key.pem'

use_auth = False

#Logs
bumperlog = logging.getLogger("bumper")
confserverlog = logging.getLogger("confserver")
#Override the logging level
#confserverlog.setLevel(logging.INFO) 
mqttserverlog = logging.getLogger("mqttserver")
#Override the logging level
#mqttserverlog.setLevel(logging.INFO)
helperbotlog = logging.getLogger("helperbot")
#Override the logging level
#helperbotlog.setLevel(logging.INFO)
xmppserverlog = logging.getLogger("xmppserver")
#Override the logging level
#xmppserverlog.setLevel(logging.INFO)

def get_milli_time(timetoconvert):
    return int(round(timetoconvert * 1000))


class BumperUser(object):
    def __init__(self,userid=""):
        self.userid = userid
        self.devices = []        
        self.tokens = []
        self.authcodes = []
        self.bots = []

    def add_device(self, devid):
        if not devid in self.devices:
            self.devices.append(devid)

    def remove_device(self, devid):
        if devid in self.devices:
            self.devices.remove(devid)


    def add_token(self, token):
        if not token in self.tokens:
            self.tokens.append(token)

    def revoke_token(self, token):
        if token in self.tokens:
            self.tokens.remove(token)

    def add_authcode(self, authcode):
        if not authcode in self.authcodes:
            self.authcodes.append(authcode)

    def revoke_authcode(self, authcode):
        if authcode in self.authcodes:
            self.authcodes.remove(authcode)

    def add_bot(self, botdid):
        if not botdid in self.bots:
            self.bots.append(botdid)

    def remove_bot(self, botdid):
        if botdid in self.bots:
            self.bots.remove(botdid)

class VacBotDevice(object):
    def __init__(self,did="", vac_bot_device_class="",resource="" , name="", nick="", company="eco-ng"):        
        self.vac_bot_device_class = vac_bot_device_class
        self.company = company
        self.did = did
        self.name = name
        self.nick = nick
        self.resource = resource
        self.mqtt_connection = False
        self.xmpp_connection = False

    def asdict(self):
        return {"class": self.vac_bot_device_class, "company": self.company,
            "did": self.did, "name": self.name, "nick": self.nick, "resource": self.resource}

class VacBotClient(object):
    def __init__(self,userid="",realm="",token=""):
        self.userid = userid
        self.realm = realm
        self.resource = token
        self.mqtt_connection = False
        self.xmpp_connection = False

    def asdict(self):
        return {"userid": self.userid,"realm": self.realm,"resource": self.resource}

def check_authcode(uid, authcode):
    users = bumper_users_var.get()
    for user in users:
        if uid == "fuid_{}".format(user.userid) and authcode in user.authcodes: 
            return True

    return False 

def add_bot(sn, did, devclass, resource):
    
    newbot = VacBotDevice()
    newbot.did = did   
    newbot.name = sn
    newbot.vac_bot_device_class = devclass
    newbot.resource = resource    

    bots = bumper_bots_var.get()
    existingbot = False
    for bot in bots:
        if bot.did == newbot.did:
            existingbot = True

    if existingbot == False:    
        bots.append(newbot)
        bumperlog.info("new bot added SN: {} DID: {}".format(newbot.name, newbot.did))
        bumper_bots_var.set(bots)

def add_client(userid, realm, resource):
    
    newclient = VacBotClient()
    newclient.userid = userid
    newclient.realm = realm
    newclient.resource = resource      

    clients = bumper_clients_var.get()           
    
    existingclient = False
    for client in clients:
        if client.userid == newclient.userid:
            existingclient = True

    if existingclient == False:  
        clients.append(newclient)
        bumperlog.info("new client added {}".format(newclient.userid))
        bumper_clients_var.set(clients)


RETURN_API_SUCCESS = "0000"
ERR_ACTIVATE_TOKEN_TIMEOUT = "1006"
ERR_COMMON = "0001"
ERR_DEFAULT = "9000"
ERR_EMAIL_NON_EXIST = "1002"
ERR_EMAIL_SEND_TIME_LIMIT = "1011"
ERR_EMAIL_USED = "1001"
ERR_INTERFACE_AUTH = "0002"
ERR_PARAM_INVALID = "0003"
ERR_PWD_WRONG = "1005"
ERR_RESET_PWD_TOKEN_TIMEOUT = "1007"
ERR_TIMESTAMP_INVALID = "0005"
ERR_TOKEN_INVALID = "0004"
ERR_USER_DISABLE = "1004"
ERR_USER_NOT_ACTIVATED = "1003"
ERR_WRONG_COMFIRM_PWD = "10010"
ERR_WRONG_EMAIL_ADDRESS = "1008"
ERR_WRONG_PWD_FROMATE = "1009"

API_ERRORS = {
    RETURN_API_SUCCESS: "0000",
    ERR_ACTIVATE_TOKEN_TIMEOUT: "1006",
    ERR_COMMON: "0001",
    ERR_DEFAULT: "9000",
    ERR_EMAIL_NON_EXIST: "1002",
    ERR_EMAIL_SEND_TIME_LIMIT: "1011",
    ERR_EMAIL_USED: "1001",
    ERR_INTERFACE_AUTH: "0002",
    ERR_PARAM_INVALID: "0003",
    ERR_PWD_WRONG: "1005",
    ERR_RESET_PWD_TOKEN_TIMEOUT: "1007",
    ERR_TIMESTAMP_INVALID: "0005",
    ERR_TOKEN_INVALID: "0004",
    ERR_USER_DISABLE: "1004",
    ERR_USER_NOT_ACTIVATED: "1003",
    ERR_WRONG_COMFIRM_PWD: "10010",
    ERR_WRONG_EMAIL_ADDRESS: "1008",
    ERR_WRONG_PWD_FROMATE: "1009",
}
