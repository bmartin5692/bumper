#!/usr/bin/env python3
import asyncio
from aiohttp import web
from bumper import plugins
import logging
import bumper
from bumper.models import *
from bumper import plugins
from datetime import datetime, timedelta


class portal_api_appsvr(plugins.ConfServerApp):

    def __init__(self):
        self.name = "portal_api_appsvr"
        self.plugin_type = "sub_api"        
        self.sub_api = "portal_api"
        
        self.routes = [
      
            web.route("*", "/appsvr/app.do", self.handle_appsvr_api, name="portal_api_appsvr_app"),

        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

    async def handle_appsvr_api(self, request):
            if not request.method == "GET":  # Skip GET for now
                try:

                    body = {}
                    postbody = {}
                    if request.content_type == "application/x-www-form-urlencoded":
                        postbody = await request.post()

                    else:
                        postbody = json.loads(await request.text())

                    todo = postbody["todo"]

                    if todo == "GetGlobalDeviceList":  # EcoVacs Home
                        bots = bumper.db_get().table("bots").all()
                        botlist = []
                        for bot in bots:
                            if bot["class"] != "":
                                b = bumper.bot_toEcoVacsHome_JSON(bot)
                                if (
                                    not b is None
                                ):  # Happens if the bot isn't on the EcoVacs Home list
                                    botlist.append(json.loads(b))

                        body = {
                            "code": 0,
                            "devices": botlist,
                            "ret": "ok",
                            "todo": "result",
                        }

                    return web.json_response(body)

                except Exception as e:
                    logging.exception("{}".format(e))

            # Return fail for GET
            body = {"result": "fail", "todo": "result"}
            return web.json_response(body)        
  
plugin = portal_api_appsvr()

