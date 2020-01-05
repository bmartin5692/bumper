#!/usr/bin/env python3
import asyncio
from aiohttp import web
from bumper import plugins
import logging
import bumper
from bumper.models import *
from bumper import plugins
from datetime import datetime, timedelta


class v1_global_auth(plugins.ConfServerApp):

    def __init__(self):
        self.name = "v1_global_auth"
        self.plugin_type = "sub_api"
        self.sub_api = "api_v1"
        
        authhandler = bumper.ConfServer.ConfServer_AuthHandler()
        self.routes = [
            web.route("*", "/global/auth/getAuthCode", authhandler.get_AuthCode, name="v1_global_auth_getAuthCode"),            
        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time


plugin = v1_global_auth()

