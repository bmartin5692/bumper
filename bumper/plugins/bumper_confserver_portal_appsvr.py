#!/usr/bin/env python3
import logging

from aiohttp import web

from bumper import plugins
from bumper.models import *


class portal_api_appsvr(plugins.ConfServerApp):

    def __init__(self):
        self.name = "portal_api_appsvr"
        self.plugin_type = "sub_api"
        self.sub_api = "portal_api"

        self.routes = [
            web.route("*", "/appsvr/app.do", self.handle_appsvr_app, name="portal_api_appsvr_app"),
            web.route("*", "/appsvr/service/list", self.handle_appsvr_service_list, name="portal_api_appsvr_service_list"),
            web.route("*", "/appsvr/oauth_callback", self.handle_appsvr_oauth_callback, name="portal_api_appsvr_oauth_callback"),
        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

    async def handle_appsvr_app(self, request):
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

                    #elif todo == "GetShareDeviceList":
                        # example response
                        # {
                        #     "code": 0,
                        #     "devices": [
                        #         {
                        #         "deviceName": "DEEBOT 900 Series (Cleaner Cleaner)",
                        #         "did": "did",
                        #         "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ba4a2cb6c2f120001c32839",
                        #         "mid": "ls1ok3",
                        #         "ownUsers": {
                        #             "isMe": true,
                        #             "nickname": "user@gmail.com",
                        #             "user": "cg****"
                        #         },
                        #         "resource": "wC3g",
                        #         "share": true,
                        #         "shareUsers": []
                        #         }
                        #     ],
                        #     "ret": "ok",
                        #     "todo": "result"
                        #     }

                        # if shared shareUsers
                        # "shareUsers": [
                        #             {
                        #                 "isMe": false,
                        #                 "nickname": "user@gmail.com",
                        #                 "status": "sharing",
                        #                 "user": "eafg****"
                        #             }
                        #             ]

                    #elif todo == "ShareDevice":
                        # example post
                        # {
                        # "todo": "ShareDevice",
                        # "accountType": "EMAIL",
                        # "auth": {
                        #     "realm": "ecouser.net",
                        #     "resource": "res",
                        #     "token": "token***",
                        #     "userid": "cg***",
                        #     "with": "users"
                        # },
                        # "country": "US",
                        # "did": "did",
                        # "resource": "wC3g",
                        # "username": "email to share to"
                        # }

                        #fail response (no user)
                        # {
                        # "todo": "result",
                        # "code": -3,
                        # "errno": -3,
                        # "ret": "fail"
                        # }

                        #success response
                        #{"ret":"ok","code":0,"todo":"result"}

                    #elif todo == "ShareUnRegisterDevice":
                    # example post
                    #  {
                        # "todo": "ShareUnRegisterDevice",
                        # "account": "email to share to",
                        # "auth": {
                        #     "realm": "ecouser.net",
                        #     "resource": "res",
                        #     "token": "toke",
                        #     "userid": "userid",
                        #     "with": "users"
                        # },
                        # "country": "US",
                        # "did": "did",
                        # "lang": "EN",
                        # "mid": "ls1ok3"
                        # }
                    # example response
                    # {
                        # "todo": "result",
                        # "code": 0,
                        # "data": {
                        #     "mailContent": "<!-- 邮件代码 --><div style=\"position: relative;\"><div style=\"font-size: 14px;font-family: Helvetica;padding: 65px 0;line-height: 150%;\"><p style=\"margin-bottom: 15px;\">Hey there,</p><p style=\"margin-bottom: 15px;\">\n\t\t\tCheck out my new awesome robot vacuum: <a href=\"#\" style=\"color: #1c95ea;text-decoration: none;\">DEEBOT 900 Series</a>!<br/>\n\t\t\tDownload the <strong>ECOVACS HOME</strong> App and sign up with your email: <a href=\"#\" style=\"color: #1c95ea;text-decoration: none;\">brian@bmartin.net</a>, so you and I can control this kick-ass robot together.</p><p style=\"margin-bottom: 15px;\">\n\t\t\tIOS: <span style=\"font-size:15px\"><a href=\"https://itunes.apple.com/us/app/ecovacs-home/id1329458504?l=zh&ls=1&mt=8\">https://itunes.apple.com/us/app/ecovacs-home/id1329458504?l=zh&amp;ls=1&amp;mt=8</a></span><br/>\n\t\t\tAndroid: <span style=\"font-size:15px\"><a href=\"https://play.google.com/store/apps/details?id=com.eco.global.app\">https://play.google.com/store/apps/details?id=com.eco.global.app</a></span></p><p style=\"margin-bottom: 15px;\">\n\t\t\tThis invitation is valid within 7 days.<br/>\n\t\t\tIf I&#39;m sending to the wrong person, please ignore this email.</p><p style=\"margin-bottom: 15px;\">Thank you.</p></div></div><!-- 邮件代码 -->",
                        #     "mailTitle": "I'm sharing my DEEBOT and you're invited!"
                        # },
                        # "ret": "ok"
                        # }


                except Exception as e:
                    logging.exception("{}".format(e))

            # Return fail for GET
            body = {"result": "fail", "todo": "result"}
            return web.json_response(body)

    async def handle_appsvr_service_list(self, request):
        try:
            # original urls comment out as they are sub sub domain, which the current certificate is not valid
            # using url, where the certs is valid
            # data = {
            #     "account": "users-base.dc-eu.ww.ecouser.net",
            #     "jmq": "jmq-ngiot-eu.dc.ww.ecouser.net",
            #     "lb": "lbo.ecouser.net",
            #     "magw": "api-app.dc-eu.ww.ecouser.net",
            #     "msgcloud": "msg-eu.ecouser.net:5223",
            #     "ngiotLb": "jmq-ngiot-eu.area.ww.ecouser.net",
            #     "rop": "api-rop.dc-eu.ww.ecouser.net"
            # }

            data = {
                "account": "users-base.ecouser.net",
                "jmq": "jmq-ngiot-eu.ecouser.net",
                "lb": "lbo.ecouser.net",
                "magw": "api-app.ecouser.net",
                "msgcloud": "msg-eu.ecouser.net:5223",
                "ngiotLb": "jmq-ngiot-eu.ecouser.net",
                "rop": "api-rop.ecouser.net"
            }

            body = {
                "code": 0,
                "data": data,
                "ret": "ok",
                "todo": "result"
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_appsvr_oauth_callback(self, request):
        try:
            token = bumper.token_by_authcode(request.query["code"])
            oauth = bumper.user_add_oauth(token["userid"])
            body = {
                "code": 0,
                "data": oauth.toResponse(),
                "ret": "ok",
                "todo": "result"
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))


plugin = portal_api_appsvr()
