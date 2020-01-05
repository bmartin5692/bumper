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

        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

    async def handle_neng_hasUnreadMessage(self, request):  # EcoVacs Home
        try:
            body = {"code": 0, "data": {"hasUnRead": True}}

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))
  
plugin = portal_api_neng()

