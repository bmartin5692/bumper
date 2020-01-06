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

class upload_global(plugins.ConfServerApp):

    def __init__(self):
        self.name = "upload_global"
        self.plugin_type = "sub_api"        
        self.sub_api = "upload_api"
        
        self.routes = [
                          
            web.route("*", "/global/{year}/{month}/{day}/{fileid}", self.handle_upload_global_file, name="upload_global_getFile"),          

        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

 

    async def handle_upload_global_file(self, request):
        try:
            fileID = request.match_info.get("id", "")

            return web.FileResponse(os.path.join(bumper.bumper_dir,"bumper","web","images","robotvac_image.jpg"))
            
        except Exception as e:
            logging.exception("{}".format(e))          

                               
  
plugin = upload_global()
