#!/usr/bin/env python3
import asyncio
from aiohttp import web
from bumper import plugins
import logging
import bumper
from bumper.models import *
from bumper import plugins
from datetime import datetime, timedelta


class v1_private_shop(plugins.ConfServerApp):

    def __init__(self):
        self.name = "v1_private_shop"
        self.plugin_type = "sub_api"        
        self.sub_api = "api_v1"
        
        self.routes = [
              
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/shop/getCnWapShopConfig", self.handle_getCnWapShopConfig, name="v1_shop_getCnWapShopConfig"),

        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
   
    async def handle_getCnWapShopConfig(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "myShopShowFlag": "N",
                    "myShopUrl": "",
                    "shopIndexShowFlag": "N",
                    "shopIndexUrl": "",
                },
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e)) 

plugin = v1_private_shop()

