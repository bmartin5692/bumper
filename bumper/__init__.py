#!/usr/bin/env python3

from .confserver import ConfServer
from .mqttserver import MQTTServer
from .mqttserver import MQTTHelperBot
from .xmppserver import XMPPServer
import asyncio
import contextvars

bumper_clients_var = contextvars.ContextVar('bumper_clients', default=[])

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
