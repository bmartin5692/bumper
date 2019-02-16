#!/usr/bin/env python3

from .confserver import ConfServer
from .mqttserver import MQTTServer
from .mqttserver import MQTTHelperBot
from .xmppserver import XMPPServer
import asyncio
import contextvars
import time
import logging

bumper_clients_var = contextvars.ContextVar('bumper_clients', default=[])
bumper_bots_var = contextvars.ContextVar('bumper_bots', default=[])
bumper_removeclients_var = contextvars.ContextVar('bumper_removeclients', default=[])
ca_cert = './certs/CA/cacert.pem'
server_cert = './certs/cert.pem'
server_key = './certs/key.pem'

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


class VacBotDevice(object):
    def __init__(self,did="", vac_bot_device_class="",resource="" , name="", nick="", company="eco-ng"):        
        self.vac_bot_device_class = vac_bot_device_class
        self.company = company
        self.did = did
        self.name = name
        self.nick = nick
        self.resource = resource

    def asdict(self):
        return {"class": self.vac_bot_device_class, "company": self.company,
            "did": self.did, "name": self.name, "nick": self.nick, "resource": self.resource}

class VacBotUser(object):
    def __init__(self,userid="",realm="",token=""):
        self.userid = userid
        self.realm = realm
        self.resource = token


    def asdict(self):
        return {"userid": self.userid,"realm": self.realm,"resource": self.resource}
