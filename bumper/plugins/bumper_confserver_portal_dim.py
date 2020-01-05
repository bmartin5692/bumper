#!/usr/bin/env python3
import asyncio
from aiohttp import web
from bumper import plugins
import logging
import bumper
from bumper.models import *
from bumper import plugins
from datetime import datetime, timedelta
import string
import random


class portal_api_dim(plugins.ConfServerApp):

    def __init__(self):
        self.name = "portal_api_dimr"
        self.plugin_type = "sub_api"        
        self.sub_api = "portal_api"
        
        self.routes = [

            web.route("*", "/dim/devmanager.do", self.handle_dim_devmanager, name="portal_api_dim_devmanager"),

        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

    async def handle_dim_devmanager(self, request):  # Used in EcoVacs Home App
        try:
            json_body = json.loads(await request.text())

            randomid = "".join(random.sample(string.ascii_letters, 6))
            did = ""
            if "toId" in json_body:  # Its a command
                did = json_body["toId"]

            if did != "":
                bot = bumper.bot_get(did)
                if bot["company"] == "eco-ng" and bot["mqtt_connection"] == True:
                    retcmd = await bumper.mqtt_helperbot.send_command(
                        json_body, randomid
                    )
                    body = retcmd
                    logging.debug("Send Bot - {}".format(json_body))
                    logging.debug("Bot Response - {}".format(body))
                    return web.json_response(body)
                else:
                    # No response, send error back
                    logging.error(
                        "No bots with DID: {} connected to MQTT".format(
                            json_body["toId"]
                        )
                    )
                    body = {"id": randomid, "errno": bumper.ERR_COMMON, "ret": "fail"}
                    return web.json_response(body)

            else:
                if "td" in json_body:  # Seen when doing initial wifi config
                    if json_body["td"] == "PollSCResult":
                        body = {"ret": "ok"}
                        return web.json_response(body)

                    if json_body["td"] == "HasUnreadMsg":  # EcoVacs Home
                        body = {"ret": "ok", "unRead": False}
                        return web.json_response(body)

                    if json_body["td"] == "ReceiveShareDevice":  # EcoVacs Home
                        body = {"ret":"ok"}
                        return web.json_response(body)                        

        except Exception as e:
            logging.exception("{}".format(e))  

plugin = portal_api_dim()

