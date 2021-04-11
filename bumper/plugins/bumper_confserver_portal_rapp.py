#!/usr/bin/env python3
from aiohttp import web
import logging
from bumper.models import *
from bumper import plugins


class api_rapp(plugins.ConfServerApp):

    def __init__(self):
        self.name = "api_rapp"
        self.plugin_type = "sub_api"
        self.sub_api = "portal_api"

        self.routes = [
            web.route("*", "/rapp/sds/user/data/map/get", self.handle_map_get, name="api_rapp"),
        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

    async def handle_map_get(self, request):
        try:
            body = {
                "code": 0,
                "data": {
                    "data": {
                        "name": "My Home"
                    },
                    "tag": None
                },
                "message": "success"
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

plugin = api_rapp()
