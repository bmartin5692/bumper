#!/usr/bin/env python3
import asyncio
from aiohttp import web
from bumper import plugins
import logging
import bumper
from bumper.models import *
from bumper import plugins
from datetime import datetime, timedelta


class v1_private_common(plugins.ConfServerApp):

    def __init__(self):
        self.name = "v1_private_common"
        self.plugin_type = "sub_api"        
        self.sub_api = "api_v1"
        
        self.routes = [
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/checkAPPVersion", self.handle_checkAPPVersion, name="v1_common_checkAppVersion"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/checkVersion", self.handle_checkVersion, name="v1_common_checkVersion"),            
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/uploadDeviceInfo", self.handle_uploadDeviceInfo, name="v1_common_uploadDeviceInfo"),            
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getSystemReminder", self.handle_getSystemReminder, name="v1_common_getSystemReminder"),            

        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

    async def handle_checkVersion(self, request):
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "c": None,
                    "img": None,
                    "r": 0,
                    "t": None,
                    "u": None,
                    "ut": 0,
                    "v": None,
                },
                "msg": "操作成功",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_checkAPPVersion(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "c": None,
                    "downPageUrl": None,
                    "img": None,
                    "nextAlertTime": None,
                    "r": 0,
                    "t": None,
                    "u": None,
                    "ut": 0,
                    "v": None,
                },
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))      

    async def handle_uploadDeviceInfo(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": None,
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))      

    async def handle_getSystemReminder(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "iosGradeTime": {"iodGradeFlag": "N"},
                    "openNotification": {
                        "openNotificationContent": None,
                        "openNotificationFlag": "N",
                        "openNotificationTitle": None,
                    },
                },
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))                        


plugin = v1_private_common()

