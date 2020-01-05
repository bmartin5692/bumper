#!/usr/bin/env python3
import asyncio
from aiohttp import web
from bumper import plugins
import logging
import bumper
from bumper.models import *
from bumper import plugins
from datetime import datetime, timedelta


class portal_api_users(plugins.ConfServerApp):

    def __init__(self):
        self.name = "portal_api_users"
        self.plugin_type = "sub_api"        
        self.sub_api = "portal_api"
        
        self.routes = [

            web.route("*", "/users/user.do", self.handle_usersapi, name="portal_api_users_user"),

        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
  
    async def handle_usersapi(self, request):
        if not request.method == "GET":  # Skip GET for now
            try:

                body = {}
                postbody = {}
                if request.content_type == "application/x-www-form-urlencoded":
                    postbody = await request.post()

                else:
                    postbody = json.loads(await request.text())

                todo = postbody["todo"]
                if todo == "FindBest":
                    service = postbody["service"]
                    if service == "EcoMsgNew":
                        srvip = bumper.bumper_announce_ip
                        srvport = 5223
                        logging.info(
                            "Announcing EcoMsgNew Server to bot as: {}:{}".format(
                                srvip, srvport
                            )
                        )
                        msgserver = {"ip": srvip, "port": srvport, "result": "ok"}
                        msgserver = json.dumps(msgserver)
                        msgserver = msgserver.replace(
                            " ", ""
                        )  # bot seems to be very picky about having no spaces, only way was with text

                        return web.json_response(text=msgserver)

                    elif service == "EcoUpdate":
                        srvip = "47.88.66.164"  # EcoVacs Server
                        srvport = 8005
                        logging.info(
                            "Announcing EcoUpdate Server to bot as: {}:{}".format(
                                srvip, srvport
                            )
                        )
                        body = {"result": "ok", "ip": srvip, "port": srvport}

                elif todo == "loginByItToken":
                    if "userId" in postbody:
                        if bumper.check_authcode(postbody["userId"], postbody["token"]):
                            body = {
                                "resource": postbody["resource"],
                                "result": "ok",
                                "todo": "result",
                                "token": postbody["token"],
                                "userId": postbody["userId"],
                            }
                    else:  # EcoVacs Home LoginByITToken
                        loginToken = bumper.loginByItToken(postbody["token"])
                        if not loginToken == {}:
                            body = {
                                "resource": postbody["resource"],
                                "result": "ok",
                                "todo": "result",
                                "token": loginToken["token"],
                                "userId": loginToken["userid"],
                            }
                        else:
                            body = {"result": "fail", "todo": "result"}

                elif todo == "GetDeviceList":
                    body = {
                        "devices": bumper.db_get().table("bots").all(),
                        "result": "ok",
                        "todo": "result",
                    }

                elif todo == "SetDeviceNick":
                    bumper.bot_set_nick(postbody["did"], postbody["nick"])
                    body = {"result": "ok", "todo": "result"}

                elif todo == "AddOneDevice":
                    bumper.bot_set_nick(postbody["did"], postbody["nick"])
                    body = {"result": "ok", "todo": "result"}

                elif todo == "DeleteOneDevice":
                    bumper.bot_remove(postbody["did"])
                    body = {"result": "ok", "todo": "result"}

                return web.json_response(body)

            except Exception as e:
                logging.exception("{}".format(e))

        # Return fail for GET
        body = {"result": "fail", "todo": "result"}
        return web.json_response(body)

plugin = portal_api_users()

