#!/usr/bin/env python3
import asyncio
from aiohttp import web
from bumper import plugins
import logging
import bumper
from bumper.models import *
from bumper import plugins
from datetime import datetime, timedelta


class v1_private_campaign(plugins.ConfServerApp):

    def __init__(self):
        self.name = "v1_private_campaign"
        self.plugin_type = "sub_api"        
        self.sub_api = "api_v1"
        
        self.routes = [

            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/campaign/homePageAlert", self.handle_homePageAlert, name="v1_campaign_homePageAlert"),

        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
   
    async def handle_homePageAlert(self, request):
        try:
            nextAlert = self.get_milli_time(
                (datetime.now() + timedelta(hours=12)).timestamp()
            )

            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "clickSchemeUrl": None,
                    "clickWebUrl": None,
                    "hasCampaign": "N",
                    "imageUrl": None,
                    "nextAlertTime": nextAlert,
                    "serverTime": self.get_milli_time(datetime.utcnow().timestamp()),
                },
                "msg": "操作成功",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))   
  

plugin = v1_private_campaign()

