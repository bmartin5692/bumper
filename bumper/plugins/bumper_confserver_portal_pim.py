#!/usr/bin/env python3
import logging
import os

from aiohttp import web

from bumper import plugins
from bumper.models import *


class portal_api_pim(plugins.ConfServerApp):

    def __init__(self):
        self.name = "portal_api_pim"
        self.plugin_type = "sub_api"
        self.sub_api = "portal_api"

        self.routes = [
            web.route("*", "/pim/product/getProductIotMap", self.handle_getProductIotMap, name="portal_api_pim_getProductIotMap"),
            web.route("*", "/pim/file/get/{id}", self.handle_pimFile, name="portal_api_pim_file"),
            web.route("*", "/pim/product/getConfignetAll", self.handle_getConfignetAll, name="portal_api_pim_getConfignetAll"),
            web.route("*", "/pim/product/getConfigGroups", self.handle_getConfigGroups, name="portal_api_pim_getConfigGroups"),
            web.route("*", "/pim/dictionary/getErrDetail", self.handle_getErrDetail, name="portal_api_pim_getErrDetail"),
            web.route("*", "/pim/product/software/config/batch", self.handle_product_config_batch, name="portal_api_pim_product_config_batch"),
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

            return web.FileResponse(os.path.join(bumper.bumper_dir, "bumper", "web", "images", "robotvac_image.jpg"))

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_getConfignetAll(self, request):
        try:
            body = confignetAllResponse
            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_getConfigGroups(self, request):
        try:
            body = configGroupsResponse
            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_getErrDetail(self, request):
        try:
            body = {
                "code": -1,
                "data": [],
                "msg": "This errcode's detail is not exists"
            }
            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_product_config_batch(self, request):
        try:
            json_body = json.loads(await request.text())
            data = []
            for pid in json_body["pids"]:
                for productConfig in productConfigBatch:
                    if pid == productConfig["pid"]:
                        data.append(productConfig)
                        continue

                # not found in productConfigBatch
                # some devices don't have any product configuration
                data.append({
                    "cfg": {},
                    "pid": pid
                })

            body = {
                "code": 200,
                "data": data,
                "message": "success"
            }
            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))


plugin = portal_api_pim()

confignetAllResponse = {
  "code": 0,
  "data": [
    {
      "groupId": "5ae147f27ccd1a0001e1f69c",
      "sort": 60,
      "groupName": "DEEBOT OZMO Slim10 Series",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1715-0201",
      "mid": "02uwxm",
      "ota": False,
      "supportVer": {
        "Android": "1.0.0",
        "IOS": "1.0.0"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5b1dddc48bc45700014035a1"
    },
    {
      "groupId": "5ca32b5de9e9270001354b3f",
      "sort": 80,
      "groupName": "DEEBOT OZMO 601",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1629-0203",
      "mid": "159",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d4b7606de51dd0001fee12d"
    },
    {
      "groupId": "5ca32b5de9e9270001354b3f",
      "sort": 80,
      "groupName": "DEEBOT",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1629-0203",
      "mid": "159",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d4b7628de51dd0001fee12f"
    },
    {
      "groupId": "5ca32b5de9e9270001354b3f",
      "sort": 80,
      "groupName": "DEEBOT OZMO 610 Series",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1629-0203",
      "mid": "159",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d4b7640de51dd0001fee131"
    },
    {
      "groupId": "5cae9662e9e9270001354b55",
      "sort": 150,
      "groupName": "DEEBOT M80 Pro",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1638-0102",
      "mid": "125",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c14414d60de0001eaf1f2"
    },
    {
      "groupId": "5bbedcd922d57f00018c13b6",
      "sort": 30,
      "groupName": "DEEBOT OZMO/PRO 930 Series",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "HK_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1803-0101",
      "mid": "115",
      "ota": False,
      "supportVer": {
        "Android": "1.1.8",
        "IOS": "1.1.8"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5cf711aeb0acfc000179ff8a"
    },
    {
      "groupId": "5b6560760506b100015c8867",
      "sort": 130,
      "groupName": "DEEBOT 900 Series",
      "isPopular": False,
      "belongApp": [
        "ecoglobal",
        "ecodeebot"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1711-0201",
      "mid": "ls1ok3",
      "ota": False,
      "supportVer": {
        "Android": "1.0.7",
        "IOS": "1.0.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ba4a2cb6c2f120001c32839"
    },
    {
      "groupId": "5b6560760506b100015c8867",
      "sort": 130,
      "groupName": "DEEBOT 910",
      "isPopular": False,
      "belongApp": [
        "ecoglobal",
        "ecodeebot"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1711-0201",
      "mid": "ls1ok3",
      "ota": False,
      "supportVer": {
        "Android": "1.0.7",
        "IOS": "1.0.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5c778731280fda0001770ba0"
    },
    {
      "groupId": "5cae9793e9e9270001354b57",
      "sort": 160,
      "groupName": "DEEBOT M81 Pro",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1638-0101",
      "mid": "141",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c2aa64d60de0001eaf1f6"
    },
    {
      "groupId": "5c19a835a1e6ee0001782245",
      "sort": 20,
      "groupName": "DEEBOT OZMO 920 Series",
      "isPopular": True,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 1,
      "materialNo": "110-1819-0101",
      "mid": "vi829v",
      "ota": False,
      "supportVer": {
        "Android": "1.1.5",
        "IOS": "1.1.5"
      },
      "smartTypes": [
        "MQ_AP"
      ],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "Briefly press the RESET button for 1 second and then release. You will hear that DEEBOT is ready for network setup.",
          "retryText": "",
          "confirmText": "I've heard the sound",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5c9c7995e9e9270001354ab4"
    },
    {
      "groupId": "5bc8187422d57f00018c13ba",
      "sort": 50,
      "groupName": "DEEBOT OZMO 960",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1803-0101",
      "mid": "gd4uut",
      "ota": False,
      "supportVer": {
        "Android": "1.1.5",
        "IOS": "1.1.5"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5c7384767b93c700013f12e7"
    },
    {
      "groupId": "5b04bf1d7ccd1a0001e1f6a6",
      "sort": 10,
      "groupName": "DEEBOT OZMO 900 Series",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1810-0101",
      "mid": "y79a7u",
      "ota": False,
      "supportVer": {
        "Android": "1.0.0",
        "IOS": "1.0.0"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5b04c0217ccd1a0001e1f6a7"
    },
    {
      "groupId": "5b04bf1d7ccd1a0001e1f6a6",
      "sort": 10,
      "groupName": "DEEBOT OZMO 905",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1810-0101",
      "mid": "y79a7u",
      "ota": False,
      "supportVer": {
        "Android": "1.0.0",
        "IOS": "1.0.0"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d1474632a6bd50001b5b6f3"
    },
    {
      "groupId": "5c763de8280fda0001770b7f",
      "sort": 100,
      "groupName": "DEEBOT 500",
      "isPopular": True,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0163",
      "mid": "vsc5ia",
      "ota": False,
      "supportVer": {
        "Android": "1.1.5",
        "IOS": "1.1.5"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5df9d6b7c783810001d3d06b",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5dfc34d15d21490001700e14",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5c874326280fda0001770d2a"
    },
    {
      "groupId": "5c763de8280fda0001770b7f",
      "sort": 100,
      "groupName": "DEEBOT 501",
      "isPopular": True,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0163",
      "mid": "vsc5ia",
      "ota": False,
      "supportVer": {
        "Android": "1.1.5",
        "IOS": "1.1.5"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5df9d6b7c783810001d3d06b",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5dfc34d15d21490001700e14",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5c931fef280fda0001770d7e"
    },
    {
      "groupId": "5c763de8280fda0001770b7f",
      "sort": 100,
      "groupName": "DEEBOT 502",
      "isPopular": True,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0163",
      "mid": "vsc5ia",
      "ota": False,
      "supportVer": {
        "Android": "1.1.5",
        "IOS": "1.1.5"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5df9d6b7c783810001d3d06b",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5dfc34d15d21490001700e14",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5c93204b63023c0001e7faa7"
    },
    {
      "groupId": "5c763de8280fda0001770b7f",
      "sort": 100,
      "groupName": "DEEBOT 505",
      "isPopular": True,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0163",
      "mid": "vsc5ia",
      "ota": False,
      "supportVer": {
        "Android": "1.1.5",
        "IOS": "1.1.5"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5df9d6b7c783810001d3d06b",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5dfc34d15d21490001700e14",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5c932067280fda0001770d7f"
    },
    {
      "groupId": "5cae9aa5e9e9270001354b5d",
      "sort": 230,
      "groupName": "DEEBOT Slim2 Series",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1639-0102",
      "mid": "123",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c150dba13eb00013feaae"
    },
    {
      "groupId": "5cae9aa5e9e9270001354b5d",
      "sort": 230,
      "groupName": "DEEBOT Slim Neo",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1639-0102",
      "mid": "123",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c152f4d60de0001eaf1f4"
    },
    {
      "groupId": "5c19a8a0ddfc1f0001ede8e0",
      "sort": 40,
      "groupName": "DEEBOT OZMO 950 Series",
      "isPopular": True,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 1,
      "materialNo": "110-1820-0101",
      "mid": "yna5xi",
      "ota": False,
      "supportVer": {
        "Android": "1.1.5",
        "IOS": "1.1.5"
      },
      "smartTypes": [
        "MQ_AP"
      ],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "Briefly press the RESET button for 1 second and then release. You will hear that DEEBOT is ready for network setup.",
          "retryText": "",
          "confirmText": "I've heard the sound",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5caafd7e1285190001685965"
    },
    {
      "groupId": "5ca4711412851900016858cb",
      "sort": 70,
      "groupName": "DEEBOT OZMO 700",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 1,
      "materialNo": "110-1825-0201",
      "mid": "0xyhhr",
      "ota": False,
      "supportVer": {
        "Android": "1.1.5",
        "IOS": "1.1.5"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "Briefly press the RESET button for 1 second and then release. You will hear that DEEBOT is ready for network setup.",
          "retryText": "",
          "confirmText": "I've heard the sound",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d117d4f0ac6ad00012b792d"
    },
    {
      "groupId": "5ca4711412851900016858cb",
      "sort": 70,
      "groupName": "DEEBOT OZMO 750",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 1,
      "materialNo": "110-1825-0201",
      "mid": "0xyhhr",
      "ota": False,
      "supportVer": {
        "Android": "1.1.5",
        "IOS": "1.1.5"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "Briefly press the RESET button for 1 second and then release. You will hear that DEEBOT is ready for network setup.",
          "retryText": "",
          "confirmText": "I've heard the sound",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d3aa309ba13eb00013feb69"
    },
    {
      "groupId": "5acb0f2e7c295c0001876eb4",
      "sort": 110,
      "groupName": "DEEBOT 600 Series",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0170",
      "mid": "dl8fht",
      "ota": False,
      "supportVer": {
        "Android": "1.0.0",
        "IOS": "1.0.0"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8e36591fd5d0001892541",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b8cd75f76f7f10001e9a0de",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5acc32067c295c0001876eea"
    },
    {
      "groupId": "5acb0f2e7c295c0001876eb4",
      "sort": 110,
      "groupName": "DEEBOT 661",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0170",
      "mid": "dl8fht",
      "ota": False,
      "supportVer": {
        "Android": "1.0.0",
        "IOS": "1.0.0"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8e36591fd5d0001892541",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b8cd75f76f7f10001e9a0de",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d280ce3350e7a0001e84c95"
    },
    {
      "groupId": "5ca31ce8e9e9270001354b33",
      "sort": 170,
      "groupName": "DEEBOT M86",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1628-0101",
      "mid": "129",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ca31df112851900016858c0"
    },
    {
      "groupId": "5d2460f244af360001383992",
      "sort": 9,
      "groupName": "DEEBOT U3",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "939393939393",
      "mid": "xb83mv",
      "ota": False,
      "supportVer": {
        "Android": "1.1.8",
        "IOS": "1.1.8"
      },
      "smartTypes": [
        "MQ_AP"
      ],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "Briefly press the RESET button for 1 second and then release. You will hear that DEEBOT is ready for network setup.",
          "retryText": "",
          "confirmText": "I've heard the sound",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d3fe649de51dd0001fee0de"
    },
    {
      "groupId": "5d2460f244af360001383992",
      "sort": 9,
      "groupName": "DEEBOT U3 LINE FRIENDS",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "939393939393",
      "mid": "xb83mv",
      "ota": False,
      "supportVer": {
        "Android": "1.1.8",
        "IOS": "1.1.8"
      },
      "smartTypes": [
        "MQ_AP"
      ],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "Briefly press the RESET button for 1 second and then release. You will hear that DEEBOT is ready for network setup.",
          "retryText": "",
          "confirmText": "I've heard the sound",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5da834a8d66cd10001f58265"
    },
    {
      "groupId": "5ca1c9a3e9e9270001354b2b",
      "sort": 240,
      "groupName": "DEEBOT Mini2",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "110-1640-0101",
      "mid": "142",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ca1ca79e9e9270001354b2d"
    },
    {
      "groupId": "5ca31e8212851900016858c2",
      "sort": 140,
      "groupName": "DEEBOT N79",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0136",
      "mid": "126",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ca32ab2e9e9270001354b3d"
    },
    {
      "groupId": "5ca31e8212851900016858c2",
      "sort": 140,
      "groupName": "DEEBOT N79S/SE",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0136",
      "mid": "126",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5cd4ca505b032200015a455d"
    },
    {
      "groupId": "5ca31e8212851900016858c2",
      "sort": 140,
      "groupName": "DEEBOT N79T/W",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "SPA",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0136",
      "mid": "126",
      "ota": False,
      "supportVer": {
        "Android": "1.1.7",
        "IOS": "1.1.7"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "",
          "guideImageUrl": "",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ca32a1012851900016858c6"
    },
    {
      "groupId": "5ae197be7ccd1a0001e1f6a1",
      "sort": 120,
      "groupName": "DEEBOT 711",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0205",
      "mid": "uv242z",
      "ota": False,
      "supportVer": {
        "Android": "1.0.5",
        "IOS": "1.0.5"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b7fc85976f7f10001e9a0d0",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8e5d5d85b4d0001776484",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4cc8d5a56000111e769"
    },
    {
      "groupId": "5ae197be7ccd1a0001e1f6a1",
      "sort": 120,
      "groupName": "DEEBOT 710",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0205",
      "mid": "uv242z",
      "ota": False,
      "supportVer": {
        "Android": "1.0.5",
        "IOS": "1.0.5"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b7fc85976f7f10001e9a0d0",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8e5d5d85b4d0001776484",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4e45f21100001882bb9"
    },
    {
      "groupId": "5ae197be7ccd1a0001e1f6a1",
      "sort": 120,
      "groupName": "DEEBOT 715",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0205",
      "mid": "uv242z",
      "ota": False,
      "supportVer": {
        "Android": "1.0.5",
        "IOS": "1.0.5"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b7fc85976f7f10001e9a0d0",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8e5d5d85b4d0001776484",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5b7b65f176f7f10001e9a0c2"
    },
    {
      "groupId": "5ae197be7ccd1a0001e1f6a1",
      "sort": 120,
      "groupName": "DEEBOT 711s",
      "isPopular": False,
      "belongApp": [
        "ecoglobal"
      ],
      "smartType": "MQ_AP",
      "failCount": 0,
      "checkTips": 0,
      "materialNo": "702-0000-0205",
      "mid": "uv242z",
      "ota": False,
      "supportVer": {
        "Android": "1.0.5",
        "IOS": "1.0.5"
      },
      "smartTypes": [],
      "steps": [
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b7fc85976f7f10001e9a0d0",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        },
        {
          "guideImageType": "image",
          "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8e5d5d85b4d0001776484",
          "title": "",
          "guideText": "",
          "retryText": "",
          "confirmText": "",
          "btnText": ""
        }
      ],
      "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d157f9f77a3a60001051f69"
    }
  ],
  "msg": "success",
  "configFAQ": {
    "wifiFAQUrl": "https://portal-ww.ecouser.net/api/pim/wififaq.html?lang=en&defaultLang=en",
    "notFoundAPUrl": "https://portal-ww.ecouser.net/api/pim/findWifi.html?lang=en&defaultLang=en",
    "configFailedUrl": "https://portal-ww.ecouser.net/api/pim/configfail.html?lang=en&defaultLang=en",
    "contactUS": "helper"
  }
}

configGroupsResponse = {
  "code": 0,
  "data": [
    {
      "sort": 1,
      "id": "5c19a743e916ba00019a4e32",
      "name": "DEEBOT OZMO",
      "robots": [
        {
          "groupId": "5d2460f244af360001383992",
          "category": "",
          "groupName": "DEEBOT U3",
          "sort": 9,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "MQ_AP",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "939393939393",
          "mid": "xb83mv",
          "ota": False,
          "supportVer": {
            "Android": "1.1.8",
            "IOS": "1.1.8"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "Briefly press the RESET button for 1 second and then release. You will hear that DEEBOT is ready for network setup.",
              "retryText": "",
              "confirmText": "I've heard the sound",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d3fe66cea1a2e0001d2f243",
          "products": [
            "5d246180350e7a0001e84bea",
            "5d78f4e878d8b60001e23edc"
          ],
          "smartTypes": [
            "MQ_AP",
            "MQ_AP"
          ],
          "seriesId": "5c19a743e916ba00019a4e32"
        },
        {
          "groupId": "5b04bf1d7ccd1a0001e1f6a6",
          "category": "",
          "groupName": "DEEBOT OZMO 900 Series",
          "sort": 10,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "MQ_AP",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1810-0101",
          "mid": "y79a7u",
          "ota": False,
          "supportVer": {
            "Android": "1.0.0",
            "IOS": "1.0.0"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d1472a62a6bd50001b5b6f2",
          "products": [
            "5b04c0227ccd1a0001e1f6a8",
            "5d1474630ac6ad00012b7940"
          ],
          "smartTypes": [],
          "seriesId": "5c19a743e916ba00019a4e32"
        },
        {
          "groupId": "5c19a835a1e6ee0001782245",
          "category": "",
          "groupName": "DEEBOT OZMO 920 Series",
          "sort": 20,
          "isPopular": True,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "MQ_AP",
          "failCount": 0,
          "checkTips": 1,
          "materialNo": "110-1819-0101",
          "mid": "vi829v",
          "ota": False,
          "supportVer": {
            "Android": "1.1.5",
            "IOS": "1.1.5"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "Briefly press the RESET button for 1 second and then release. You will hear that DEEBOT is ready for network setup.",
              "retryText": "",
              "confirmText": "I've heard the sound",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5c9c79c1e9e9270001354ab5",
          "products": [
            "5c19a8f3a1e6ee0001782247"
          ],
          "smartTypes": [
            "MQ_AP"
          ],
          "seriesId": "5c19a743e916ba00019a4e32"
        },
        {
          "groupId": "5bbedcd922d57f00018c13b6",
          "category": "",
          "groupName": "DEEBOT OZMO/PRO 930 Series",
          "sort": 30,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "HK_AP",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1803-0101",
          "mid": "115",
          "ota": False,
          "supportVer": {
            "Android": "1.1.8",
            "IOS": "1.1.8"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5cf66652b0acfc000179ff83",
          "products": [
            "5bbedd2822d57f00018c13b7",
            "5cd4dd385b032200015a4561"
          ],
          "smartTypes": [],
          "seriesId": "5c19a743e916ba00019a4e32"
        },
        {
          "groupId": "5c19a8a0ddfc1f0001ede8e0",
          "category": "",
          "groupName": "DEEBOT OZMO 950 Series",
          "sort": 40,
          "isPopular": True,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "MQ_AP",
          "failCount": 0,
          "checkTips": 1,
          "materialNo": "110-1820-0101",
          "mid": "yna5xi",
          "ota": False,
          "supportVer": {
            "Android": "1.1.5",
            "IOS": "1.1.5"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "Briefly press the RESET button for 1 second and then release. You will hear that DEEBOT is ready for network setup.",
              "retryText": "",
              "confirmText": "I've heard the sound",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5caafd981285190001685966",
          "products": [
            "5c19a91ca1e6ee000178224a"
          ],
          "smartTypes": [
            "MQ_AP"
          ],
          "seriesId": "5c19a743e916ba00019a4e32"
        },
        {
          "groupId": "5bc8187422d57f00018c13ba",
          "category": "",
          "groupName": "DEEBOT OZMO 960 Series",
          "sort": 50,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "MQ_AP",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1803-0101",
          "mid": "gd4uut",
          "ota": False,
          "supportVer": {
            "Android": "1.1.5",
            "IOS": "1.1.5"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d0899b00ac6ad00012b78f7",
          "products": [
            "5bc8189d68142800016a6937"
          ],
          "smartTypes": [],
          "seriesId": "5c19a743e916ba00019a4e32"
        },
        {
          "groupId": "5ae147f27ccd1a0001e1f69c",
          "category": "",
          "groupName": "DEEBOT OZMO Slim10 Series",
          "sort": 60,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "MQ_AP",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1715-0201",
          "mid": "02uwxm",
          "ota": False,
          "supportVer": {
            "Android": "1.0.0",
            "IOS": "1.0.0"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5b5ebc34822f0b00013a2e1a",
          "products": [
            "5ae1481e7ccd1a0001e1f69e"
          ],
          "smartTypes": [],
          "seriesId": "5c19a743e916ba00019a4e32"
        },
        {
          "groupId": "5ca4711412851900016858cb",
          "category": "",
          "groupName": "DEEBOT OZMO 700 Series",
          "sort": 70,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "MQ_AP",
          "failCount": 0,
          "checkTips": 1,
          "materialNo": "110-1825-0201",
          "mid": "0xyhhr",
          "ota": False,
          "supportVer": {
            "Android": "1.1.5",
            "IOS": "1.1.5"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "Briefly press the RESET button for 1 second and then release. You will hear that DEEBOT is ready for network setup.",
              "retryText": "",
              "confirmText": "I've heard the sound",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d117d680ac6ad00012b792e",
          "products": [
            "5ca4716312851900016858cd",
            "5ce7870cd85b4d0001775db9"
          ],
          "smartTypes": [],
          "seriesId": "5c19a743e916ba00019a4e32"
        },
        {
          "groupId": "5ca32b5de9e9270001354b3f",
          "category": "",
          "groupName": "DEEBOT OZMO 600 Series",
          "sort": 80,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "SPA",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1629-0203",
          "mid": "159",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d4b75a8ea1a2e0001d2f28e",
          "products": [
            "5ca32bc2e9e9270001354b41",
            "5cbd97b961526a00019799bd",
            "5cae98d01285190001685974"
          ],
          "smartTypes": [],
          "seriesId": "5c19a743e916ba00019a4e32"
        }
      ]
    },
    {
      "sort": 2,
      "id": "5c2599b6a1e6ee0001782328",
      "name": "DEEBOT",
      "robots": [
        {
          "groupId": "5c763de8280fda0001770b7f",
          "category": "",
          "groupName": "DEEBOT 500 Series",
          "sort": 100,
          "isPopular": True,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "MQ_AP",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "702-0000-0163",
          "mid": "vsc5ia",
          "ota": False,
          "supportVer": {
            "Android": "1.1.5",
            "IOS": "1.1.5"
          },
          "steps": [
            {
              "guideImageType": "image",
              "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5df9d6b7c783810001d3d06b",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "image",
              "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5dfc34d15d21490001700e14",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5cf6668bda73e90001dc3b98",
          "products": [
            "5c763eba280fda0001770b81",
            "5c763f35280fda0001770b84",
            "5c763f63280fda0001770b88",
            "5c763f8263023c0001e7f855"
          ],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5acb0f2e7c295c0001876eb4",
          "category": "",
          "groupName": "DEEBOT 600 Series",
          "sort": 110,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "MQ_AP",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "702-0000-0170",
          "mid": "dl8fht",
          "ota": False,
          "supportVer": {
            "Android": "1.0.0",
            "IOS": "1.0.0"
          },
          "steps": [
            {
              "guideImageType": "image",
              "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8e36591fd5d0001892541",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "image",
              "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b8cd75f76f7f10001e9a0de",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5cf6669ab0acfc000179ff85",
          "products": [
            "5acb0fa87c295c0001876ecf",
            "5d280ce344af3600013839ab"
          ],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5ae197be7ccd1a0001e1f6a1",
          "category": "",
          "groupName": "DEEBOT 700 Series",
          "sort": 120,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "MQ_AP",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "702-0000-0205",
          "mid": "uv242z",
          "ota": False,
          "supportVer": {
            "Android": "1.0.5",
            "IOS": "1.0.5"
          },
          "steps": [
            {
              "guideImageType": "image",
              "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b7fc85976f7f10001e9a0d0",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "image",
              "guideImageUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8e5d5d85b4d0001776484",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5b5ec2b1822f0b00013a2e1c",
          "products": [
            "5b43077b8bc457000140363e",
            "5b5149b4ac0b87000148c128",
            "5b7b65f364e1680001a08b54",
            "5ceba1c6d85b4d0001776986"
          ],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5b6560760506b100015c8867",
          "category": "",
          "groupName": "DEEBOT 900 Series",
          "sort": 130,
          "isPopular": False,
          "belongApp": [
            "ecoglobal",
            "ecodeebot"
          ],
          "smartType": "MQ_AP",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1711-0201",
          "mid": "ls1ok3",
          "ota": False,
          "supportVer": {
            "Android": "1.0.7",
            "IOS": "1.0.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d1472b70ac6ad00012b793f",
          "products": [
            "5b6561060506b100015c8868",
            "5bf2596f23244a00013f2f13"
          ],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5ca31e8212851900016858c2",
          "category": "",
          "groupName": "DEEBOT N79 Series",
          "sort": 140,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "SPA",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "702-0000-0136",
          "mid": "126",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5cf666bdda73e90001dc3b9a",
          "products": [
            "5ca32ab212851900016858c7",
            "5cce893813afb7000195d6af",
            "5ca32a11e9e9270001354b39"
          ],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5cae9662e9e9270001354b55",
          "category": "",
          "groupName": "DEEBOT M80 Pro",
          "sort": 150,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "SPA",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1638-0102",
          "mid": "125",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c1000ba13eb00013feaa4",
          "products": [
            "5cae9703128519000168596a"
          ],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5cae9793e9e9270001354b57",
          "category": "",
          "groupName": "DEEBOT M81 Pro",
          "sort": 160,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "SPA",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1638-0101",
          "mid": "141",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c10224d60de0001eaf1ea",
          "products": [
            "5cae97c9128519000168596f"
          ],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5ca31ce8e9e9270001354b33",
          "category": "",
          "groupName": "DEEBOT M86",
          "sort": 170,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "SPA",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1628-0101",
          "mid": "129",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5cf66704da73e90001dc3b9b",
          "products": [
            "5ca31df1e9e9270001354b35"
          ],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5cd4df825b032200015a4567",
          "category": "",
          "groupName": "DEEBOT M87",
          "sort": 180,
          "isPopular": False,
          "belongApp": [
            "ecodeebot"
          ],
          "smartType": "SCM0",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1517-1001",
          "mid": "121",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8ea21d85b4d0001776489",
          "products": [],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5cd4dfc9f542e00001dc2df8",
          "category": "",
          "groupName": "DEEBOT M88",
          "sort": 190,
          "isPopular": False,
          "belongApp": [
            "ecodeebot"
          ],
          "smartType": "SCM0",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1517-0701",
          "mid": "107",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8eaa5d85b4d000177648a",
          "products": [],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5cd4e077f542e00001dc2dfb",
          "category": "",
          "groupName": "DEEBOT R95",
          "sort": 200,
          "isPopular": False,
          "belongApp": [
            "ecodeebot"
          ],
          "smartType": "SCM0",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1412-0001",
          "mid": "113",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8eb7091fd5d000189254a",
          "products": [],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5cd4e0b25b032200015a4569",
          "category": "",
          "groupName": "DEEBOT R96",
          "sort": 210,
          "isPopular": False,
          "belongApp": [
            "ecodeebot"
          ],
          "smartType": "SCM0",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1510-0501",
          "mid": "118",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8ebd791fd5d000189254b",
          "products": [],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5cd4e0e15b032200015a456c",
          "category": "",
          "groupName": "DEEBOT R98",
          "sort": 220,
          "isPopular": False,
          "belongApp": [
            "ecodeebot"
          ],
          "smartType": "SCM0",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1510-0601",
          "mid": "117",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ce8ec13d85b4d000177648b",
          "products": [],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5cae9aa5e9e9270001354b5d",
          "category": "",
          "groupName": "DEEBOT Slim Series",
          "sort": 230,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "SPA",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1639-0102",
          "mid": "123",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c11fa4d60de0001eaf1ef",
          "products": [
            "5cae9b201285190001685977",
            "5cd43b4cf542e00001dc2dec"
          ],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        },
        {
          "groupId": "5ca1c9a3e9e9270001354b2b",
          "category": "",
          "groupName": "DEEBOT Mini2",
          "sort": 240,
          "isPopular": False,
          "belongApp": [
            "ecoglobal"
          ],
          "smartType": "SPA",
          "failCount": 0,
          "checkTips": 0,
          "materialNo": "110-1640-0101",
          "mid": "142",
          "ota": False,
          "supportVer": {
            "Android": "1.1.7",
            "IOS": "1.1.7"
          },
          "steps": [
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            },
            {
              "guideImageType": "",
              "guideImageUrl": "",
              "title": "",
              "guideText": "",
              "retryText": "",
              "confirmText": "",
              "btnText": ""
            }
          ],
          "icon": "https://portal-ww.ecouser.net/api/pim/file/get/5ca1c901e9e9270001354b2a",
          "products": [
            "5ca1ca7a12851900016858bd"
          ],
          "smartTypes": [],
          "seriesId": "5c2599b6a1e6ee0001782328"
        }
      ]
    }
  ],
  "msg": "success",
  "configFAQ": {
    "wifiFAQUrl": "https://portal-ww.ecouser.net/api/pim/wififaq.html?lang=en&defaultLang=en",
    "notFoundAPUrl": "https://portal-ww.ecouser.net/api/pim/findWifi.html?lang=en&defaultLang=en",
    "configFailedUrl": "https://portal-ww.ecouser.net/api/pim/configfail.html?lang=en&defaultLang=en",
    "contactUS": "helper"
  }
}

productConfigBatch = [
    {
        "pid": "5e14196a6e71b80001b60fda",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": False,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5e8e8d8a032edd8457c66bfb",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": False,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5c19a91ca1e6ee000178224a",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": False,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5e8e8d2a032edd3c03c66bf7",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": False,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5de0d86ed88546000195239a",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": True,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5c19a8f3a1e6ee0001782247",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": False,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5e698a6306f6de52c264c61b",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": False,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5e699a4106f6de83ea64c620",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": False,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5edd998afdd6a30008da039b",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": True,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5edd9a4075f2fc000636086c",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": True,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5ed5e4d3a719ea460ec3216c",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": False,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5f88195e6cf8de0008ed7c11",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": False,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5f8819156cf8de0008ed7c0d",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": False,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    },
    {
        "pid": "5fa105c6d16a99000667eb54",
        "cfg": {
            "supported": {
                "tmallstand": False,
                "video": False,
                "battery": True,
                "clean": True,
                "charge": True
            }
        }
    }
]
