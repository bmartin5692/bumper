#!/usr/bin/env python3
from aiohttp import web
import logging
import bumper
from bumper import plugins
from datetime import datetime


class v1_private_userSetting(plugins.ConfServerApp):

    def __init__(self):

        self.name = "v1_private_userSetting"
        self.plugin_type = "sub_api"                
        self.sub_api = "api_v1"

        self.routes = [
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/userSetting/getSuggestionSetting", self.handle_getSuggestionSetting,name="v1_userSetting_getSuggestionSetting"),
        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

    async def handle_getSuggestionSetting(self, request):
        try:

            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "acceptSuggestion": "Y",
                    "itemList": [
                        {
                            "name": "Aktionen/Angebote/Ereignisse",
                            "settingKey": "MARKETING",
                            "val": "Y"
                        },
                        {
                            "name": "Benutzerbefragung",
                            "settingKey": "QUESTIONNAIRE",
                            "val": "Y"
                        },
                        {
                            "name": "Produkt-Upgrade/Hilfe für Benutzer",
                            "settingKey": "INTRODUCTION",
                            "val": "Y"
                        }
                    ]
                },
                "msg": "操作成功",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))        


plugin = v1_private_userSetting()
