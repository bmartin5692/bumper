#!/usr/bin/env python3

from .confserver import ConfServer
from .mqttserver import MQTTServer
from .mqttserver import MQTTHelperBot
from .xmppserver import XMPPServer
import asyncio
import contextvars
import time
import platform
import os
import logging
from base64 import b64decode, b64encode
from tinydb import TinyDB, Query

bumper_users_var = contextvars.ContextVar("bumper_users", default=[])
bumper_clients_var = contextvars.ContextVar("bumper_clients", default=[])
bumper_bots_var = contextvars.ContextVar("bumper_bots", default=[])

ca_cert = "./certs/CA/cacert.pem"
server_cert = "./certs/cert.pem"
server_key = "./certs/key.pem"

use_auth = False

# Logs
bumperlog = logging.getLogger("bumper")
confserverlog = logging.getLogger("confserver")
# Override the logging level
# confserverlog.setLevel(logging.INFO)
mqttserverlog = logging.getLogger("mqttserver")
# Override the logging level
# mqttserverlog.setLevel(logging.INFO)
helperbotlog = logging.getLogger("helperbot")
# Override the logging level
# helperbotlog.setLevel(logging.INFO)
xmppserverlog = logging.getLogger("xmppserver")
# Override the logging level
# xmppserverlog.setLevel(logging.INFO)


def get_milli_time(timetoconvert):
    return int(round(timetoconvert * 1000))

def db_file():
    if platform.system() == 'Windows':
        return os.path.join(os.getenv('APPDATA'), 'bumper.db')
    else:
        return os.path.expanduser('~/.config/bumper.db')    

def db_get():
    #Will create the database if it doesn't exist
    db = TinyDB(db_file())

    #Will create the tables if they don't exist
    users_table = db.table('users')
    clients_table = db.table('clients')
    bots_table = db.table('bots')

    return db

class BumperUser(object):
    def __init__(self, userid=""):
        self.userid = userid
        self.devices = []
        self.tokens = []
        self.authcodes = []
        self.bots = []

    def asdict(self):
        return {
            "userid": self.userid,
            "devices": self.devices,
            "tokens": self.tokens,
            "authcodes": self.authcodes,
            "bots": self.bots,            
        }        

def user_add(userid):
    newuser = BumperUser()
    newuser.userid = userid    
    
    user = user_get(userid)
    if not user:
        bumperlog.info("Adding new user with userid: {}".format(newuser.userid))
        user_full_upsert(newuser.asdict())

def user_get(userid):
    users = db_get().table('users')
    User = Query()
    return users.get(User.userid == userid)    

def user_full_upsert(user):
    users = db_get().table('users')
    User = Query()        
    users.upsert(user, User.did == user['userid'])

def user_add_device(userid, devid):
    users = db_get().table('users')
    User = Query()        
    user = users.get(User.userid == userid)
    userdevices = list(user['devices'])
    if not devid in userdevices:
        userdevices.append(devid)
    
    users.upsert({'devices': userdevices}, User.userid == userid)

def user_remove_device(userid, devid):
    users = db_get().table('users')
    User = Query()        
    user = users.get(User.userid == userid)
    userdevices = list(user['devices'])
    if devid in userdevices:
        userdevices.remove(devid)
    
    users.upsert({'devices': userdevices}, User.userid == userid)       

def user_add_bot(userid, did):
    users = db_get().table('users')
    User = Query()        
    user = users.get(User.userid == userid)
    userbots = list(user['bots'])
    if not did in userbots:
        userbots.append(did)
    
    users.upsert({'bots': userbots}, User.userid == userid) 

def user_remove_bot(userid, did):
    users = db_get().table('users')
    User = Query()        
    user = users.get(User.userid == userid)
    userbots = list(user['bots'])
    if did in userbots:
        userbots.remove(did)
    
    users.upsert({'bots': userbots}, User.userid == userid)  
   

def user_add_token(userid, token):
    users = db_get().table('users')
    User = Query()        
    user = users.get(User.userid == userid)
    usertokens = list(user['tokens'])
    if not token in usertokens:
        usertokens.append(token)
    
    users.upsert({'tokens': usertokens}, User.userid == userid)  

def user_revoke_token(userid, token):
    users = db_get().table('users')
    User = Query()        
    user = users.get(User.userid == userid)
    usertokens = list(user['tokens'])
    if token in usertokens:
        usertokens.remove(token)
    
    users.upsert({'tokens': usertokens}, User.userid == userid)          

def user_add_authcode(userid, authcode):
    users = db_get().table('users')
    User = Query()        
    user = users.get(User.userid == userid)
    userauthcodes = list(user['authcodes'])
    if not authcode in userauthcodes:
        userauthcodes.append(authcode)
    
    users.upsert({'authcodes': userauthcodes}, User.userid == userid)        

def user_revoke_authcode(userid, authcode):
    users = db_get().table('users')
    User = Query()        
    user = users.get(User.userid == userid)
    userauthcodes = list(user['authcodes'])
    if authcode in userauthcodes:
        userauthcodes.remove(authcode)
    
    users.upsert({'authcodes': userauthcodes}, User.userid == userid)    


class VacBotDevice(object):
    def __init__(
        self,
        did="",
        vac_bot_device_class="",
        resource="",
        name="",
        nick="",
        company="",
    ):
        self.vac_bot_device_class = vac_bot_device_class
        self.company = company
        self.did = did
        self.name = name
        self.nick = nick
        self.resource = resource
        self.mqtt_connection = False
        self.xmpp_connection = False

    def asdict(self):
        return {
            "class": self.vac_bot_device_class,
            "company": self.company,
            "did": self.did,
            "name": self.name,
            "nick": self.nick,
            "resource": self.resource,
            "mqtt_connection": self.mqtt_connection,
            "xmpp_connection": self.xmpp_connection
        }


class VacBotClient(object):
    def __init__(self, userid="", realm="", token=""):
        self.userid = userid
        self.realm = realm
        self.resource = token
        self.mqtt_connection = False
        self.xmpp_connection = False

    def asdict(self):
        return {
            "userid": self.userid,
            "realm": self.realm,
            "resource": self.resource,
            "mqtt_connection": self.mqtt_connection,
            "xmpp_connection": self.xmpp_connection
            }


def check_authcode(uid, authcode):
    users = bumper_users_var.get()
    for user in users:
        if uid == "fuid_{}".format(user.userid) and authcode in user.authcodes:
            return True

    return False


def bot_add(sn, did, devclass, resource, company):
    newbot = VacBotDevice()
    newbot.did = did
    newbot.name = sn
    newbot.vac_bot_device_class = devclass
    newbot.resource = resource
    newbot.company = company
    
    bot = bot_get(did)
    if not bot:
        bumperlog.info("Adding new bot with SN: {} DID: {}".format(newbot.name, newbot.did))
        bot_full_upsert(newbot.asdict())

def bot_remove(did):
    bots = db_get().table('bots')
    bot = bot_get(did)
    bots.remove(doc_ids=[bot.doc_id])
    
def bot_get(did):
    bots = db_get().table('bots')
    Bot = Query()
    return bots.get(Bot.did == did)

def bot_full_upsert(vacbot):
    bots = db_get().table('bots')
    Bot = Query()        
    bots.upsert(vacbot, Bot.did == vacbot['did'])

def bot_set_nick(did, nick):
    bots = db_get().table('bots')
    Bot = Query()        
    bots.upsert({'nick': nick}, Bot.did == did)

def bot_set_mqtt(did, mqtt):
    bots = db_get().table('bots')
    Bot = Query()        
    bots.upsert({'mqtt_connection': mqtt}, Bot.did == did)   

def bot_set_xmpp(did, xmpp):
    bots = db_get().table('bots')
    Bot = Query()        
    bots.upsert({'xmpp_connection': xmpp}, Bot.did == did)        

def client_add(userid, realm, resource):
    newclient = VacBotClient()
    newclient.userid = userid
    newclient.realm = realm
    newclient.resource = resource

    client = client_get(resource)
    if not client:
        bumperlog.info("Adding new client with resource {}".format(newclient.resource))
        client_full_upsert(newclient.asdict())

def client_get(resource):
    clients = db_get().table('clients')
    Client = Query()
    return clients.get(Client.resource == resource)

def client_full_upsert(client):
    clients = db_get().table('clients')
    Client = Query()        
    clients.upsert(client, Client.resource == client['resource'])    

def client_set_mqtt(resource, mqtt):
    clients = db_get().table('clients')
    Client = Query()        
    clients.upsert({'mqtt_connection': mqtt}, Client.resource == resource)   

def client_set_xmpp(resource, xmpp):
    clients = db_get().table('clients')
    Client = Query()        
    clients.upsert({'xmpp_connection': xmpp}, Client.resource == resource)      

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
