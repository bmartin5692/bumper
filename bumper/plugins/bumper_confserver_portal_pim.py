#!/usr/bin/env python3
import asyncio
from aiohttp import web
from bumper import plugins
import logging
import bumper
from bumper.models import *
from bumper import plugins
from datetime import datetime, timedelta
import os

class portal_api_pim(plugins.ConfServerApp):

    def __init__(self):
        self.name = "portal_api_pim"
        self.plugin_type = "sub_api"        
        self.sub_api = "portal_api"
        
        self.routes = [
                          
            web.route("*", "/pim/product/getProductIotMap", self.handle_getProductIotMap, name="portal_api_pim_getProductIotMap"),
            web.route("*", "/pim/file/get/{id}", self.handle_pimFile, name="portal_api_pim_file"),

        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

    async def handle_getProductIotMap(self, request):
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": EcoVacsHomeProducts,
            }
            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_pimFile(self, request):
        try:
            fileID = request.match_info.get("id", "")

            return web.FileResponse(os.path.join(bumper.data_dir,"web","robotvac_image.jpg"))
            
        except Exception as e:
            logging.exception("{}".format(e))            
  
plugin = portal_api_pim()

