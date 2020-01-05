#!/usr/bin/env python3
import asyncio
from aiohttp import web
from bumper import plugins
import logging
import bumper
from bumper.models import *
from bumper import plugins
from datetime import datetime, timedelta


class v1_private_user(plugins.ConfServerApp):

    def __init__(self):

        self.name = "v1_private_user"
        self.plugin_type = "sub_api"                
        self.sub_api = "api_v1"

        authhandler = bumper.ConfServer.ConfServer_AuthHandler()
        self.routes = [
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/login", authhandler.login, name="v1_user_login"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/checkLogin", authhandler.login, name="v1_user_checkLogin"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/getAuthCode", authhandler.get_AuthCode, name="v1_user_getAuthCode"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/logout", authhandler.logout, name="v1_user_logout"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/checkAgreement", self.handle_checkAgreement,name="v1_user_checkAgreement"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/checkAgreementBatch", self.handle_checkAgreement,name="v1_user_checkAgreementBatch"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/getUserAccountInfo", authhandler.getUserAccountInfo,name="v1_user_getUserAccountInfo"),
       # Direct register from app:
        # /{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/directRegister
    
        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

    async def handle_checkAgreement(self, request):
        try:
            apptype = request.match_info.get("apptype", "")
            if "global_" in apptype:
                body = {
                    "code": bumper.RETURN_API_SUCCESS,
                    "data": [
                        {
                            "force": "N",
                            "id": "20180804040641_7d746faf18b8cb22a50d145598fe4c90",
                            "type": "USER",
                            "url": "https://bumper.ecovacs.com/content/agreement?id=20180804040641_7d746faf18b8cb22a50d145598fe4c90&language=EN",  # "https://gl-us-wap.ecovacs.com/content/agreement?id=20180804040641_7d746faf18b8cb22a50d145598fe4c90&language=EN
                            "version": "1.01",
                        },
                        {
                            "force": "N",
                            "id": "20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac",
                            "type": "PRIVACY",
                            "url": "https://bumper.ecovacs.com/content/agreement?id=20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac&language=EN",  # "https://gl-us-wap.ecovacs.com/content/agreement?id=20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac&language=EN"
                            "version": "1.01",
                        },
                    ],
                    "msg": "操作成功",
                    "success": True,
                    "time": self.get_milli_time(datetime.utcnow().timestamp()),
                }
            else:
                body = {
                    "code": bumper.RETURN_API_SUCCESS,
                    "data": [],
                    "msg": "操作成功",
                    "time": self.get_milli_time(datetime.utcnow().timestamp()),
                }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))        

plugin = v1_private_user()

