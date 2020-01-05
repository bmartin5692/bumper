#!/usr/bin/env python3
import asyncio
from aiohttp import web
from bumper import plugins
import logging
import bumper
from bumper.models import *
from bumper import plugins
from datetime import datetime, timedelta


class portal_api_neng(plugins.ConfServerApp):

    def __init__(self):
        self.name = "portal_api_neng"
        self.plugin_type = "sub_api"        
        self.sub_api = "portal_api"
        
        self.routes = [
                
            web.route("*", "/neng/message/hasUnreadMsg", self.handle_neng_hasUnreadMessage, name="portal_api_neng_hasUnreadMessage"),
            web.route("*", "/neng/message/getShareMsgs", self.handle_neng_getShareMsgs, name="portal_api_neng_getShareMsgs"),
            web.route("*", "/neng/message/getlist", self.handle_neng_getlist, name="portal_api_neng_getlist"),

        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

    async def handle_neng_hasUnreadMessage(self, request):  # EcoVacs Home
        try:
            body = {"code": 0, "data": {"hasUnRead": True}}

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_neng_getShareMsgs(self, request):  # EcoVacs Home
        try:
            body = {"code":0,"data":{"hasNext":False,"msgs":[]}}

            # share msg response
            # {
            #     "code": 0,
            #     "data": {
            #         "hasNext": False,
            #         "msgs": [
            #         {
            #             "action": "shareDevice",
            #             "deviceName": "DEEBOT 900 Series",
            #             "did": "DID",
            #             "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ba4a2cb6c2f120001c32839",
            #             "id": "0154d03a-294e-4b99-a6df-fc2dbf4146d5",
            #             "isRead": False,
            #             "message": "User user@gmail.com sent you the sharing invitation of DEEBOT 900 Series.",
            #             "mid": "ls1ok3",
            #             "resource": "grU0",
            #             "shareStatus": "sharing",
            #             "ts": 1578206187412
            #         }
            #         ]
            #     }
            #     }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))       

    async def handle_neng_getlist(self, request):  # EcoVacs Home
        try:
            body = {"code":0,"data":{"hasNext":False,"msgs":[]}}

            #Sample Message
        #     {
        # "id": "5da0ac9d636aec5107627ac4", 
        # "ts": 1570811036877,
        # "did": "bot did",
        # "cid": "ls1ok3",
        # "name": "DEEBOT 900 Series",
        # "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ba4a2cb6c2f120001c32839",
        # "eventTypeId": "5aab824bb62ce30001f9a702",
        # "title": "DEEBOT is off the floor.",
        # "body": "DEEBOT is off the floor. Please put it back.",
        # "read": false,
        # "UILogicId": "D_900",
        # "type": "web",
        # "url": "https://portal-ww.ecouser.net/api/pim/eventdetail.html?id=5ba21e44aed83800015b9ca8" # Off the floor instructions
        # }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))                     
  
plugin = portal_api_neng()

