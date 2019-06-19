#!/usr/bin/env python3
import json


class VacBotDevice(object):
    def __init__(
        self, did="", vac_bot_device_class="", resource="", name="", nick="", company=""
    ):
        self.vac_bot_device_class = vac_bot_device_class
        self.company = company
        self.did = did
        self.name = name
        self.nick = nick
        self.resource = resource
        self.mqtt_connection = False
        self.xmpp_connection = False

    def asdict(self):
        return {
            "class": self.vac_bot_device_class,
            "company": self.company,
            "did": self.did,
            "name": self.name,
            "nick": self.nick,
            "resource": self.resource,
            "mqtt_connection": self.mqtt_connection,
            "xmpp_connection": self.xmpp_connection,
        }


class BumperUser(object):
    def __init__(self, userid=""):
        self.userid = userid
        self.devices = []
        self.bots = []

    def asdict(self):
        return {"userid": self.userid, "devices": self.devices, "bots": self.bots}


class GlobalVacBotDevice(VacBotDevice):  # EcoVacs Home
    UILogicId = ""
    ota = True
    updateInfo = {"changeLog": "", "needUpdate": False}
    icon = ""
    deviceName = ""


class VacBotClient(object):
    def __init__(self, userid="", realm="", token=""):
        self.userid = userid
        self.realm = realm
        self.resource = token
        self.mqtt_connection = False
        self.xmpp_connection = False

    def asdict(self):
        return {
            "userid": self.userid,
            "realm": self.realm,
            "resource": self.resource,
            "mqtt_connection": self.mqtt_connection,
            "xmpp_connection": self.xmpp_connection,
        }


class EcoVacs_Login:
    accessToken = ""
    country = ""
    email = ""
    uid = ""
    username = ""

    def toJSON(self):
        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=False
        )  # , indent=4)


class EcoVacsHome_Login(EcoVacs_Login):
    loginName = ""
    mobile = ""
    ucUid = ""


# EcoVacs Home Product IOT Map - 2019-05-20
# https://portal-ww.ecouser.net/api/pim/product/getProductIotMap
EcoVacsHomeProducts = [
    {
        "classid": "dl8fht",
        "product": {
            "UILogicId": "D_600",
            "_id": "5acb0fa87c295c0001876ecf",
            "icon": "5acc32067c295c0001876eea",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5acc32067c295c0001876eea",
            "materialNo": "702-0000-0170",
            "name": "DEEBOT 600 Series",
            "ota": False,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "02uwxm",
        "product": {
            "UILogicId": "D_OZMO_SLIM10",
            "_id": "5ae1481e7ccd1a0001e1f69e",
            "icon": "5b1dddc48bc45700014035a1",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b1dddc48bc45700014035a1",
            "materialNo": "110-1715-0201",
            "name": "DEEBOT OZMO Slim10 Series",
            "ota": False,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "y79a7u",
        "product": {
            "UILogicId": "D_OZMO_900",
            "_id": "5b04c0227ccd1a0001e1f6a8",
            "icon": "5b04c0217ccd1a0001e1f6a7",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b04c0217ccd1a0001e1f6a7",
            "materialNo": "110-1810-0101",
            "name": "DEEBOT OZMO 900 Series",
            "ota": True,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "jr3pqa",
        "product": {
            "UILogicId": "D_700",
            "_id": "5b43077b8bc457000140363e",
            "icon": "5b5ac4cc8d5a56000111e769",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4cc8d5a56000111e769",
            "materialNo": "702-0000-0202",
            "name": "DEEBOT 711",
            "ota": True,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "uv242z",
        "product": {
            "UILogicId": "D_700",
            "_id": "5b5149b4ac0b87000148c128",
            "icon": "5b5ac4e45f21100001882bb9",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4e45f21100001882bb9",
            "materialNo": "702-0000-0205",
            "name": "DEEBOT 710",
            "ota": True,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "ls1ok3",
        "product": {
            "UILogicId": "D_900",
            "_id": "5b6561060506b100015c8868",
            "icon": "5ba4a2cb6c2f120001c32839",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ba4a2cb6c2f120001c32839",
            "materialNo": "110-1711-0201",
            "name": "DEEBOT 900 Series",
            "ota": True,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "eyi9jv",
        "product": {
            "UILogicId": "D_700",
            "_id": "5b7b65f364e1680001a08b54",
            "icon": "5b7b65f176f7f10001e9a0c2",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b7b65f176f7f10001e9a0c2",
            "materialNo": "715",
            "name": "DEEBOT 715",
            "ota": True,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "4zfacv",
        "product": {
            "UILogicId": "DN_2G",
            "_id": "5bf2596f23244a00013f2f13",
            "icon": "5c778731280fda0001770ba0",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c778731280fda0001770ba0",
            "materialNo": "910",
            "name": "DEEBOT 910",
            "ota": True,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "vi829v",
        "product": {
            "UILogicId": "DX_5G",
            "_id": "5c19a8f3a1e6ee0001782247",
            "icon": "5c9c7995e9e9270001354ab4",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c9c7995e9e9270001354ab4",
            "materialNo": "920",
            "name": "DEEBOT OZMO 920 Series",
            "ota": True,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "gd4uut",
        "product": {
            "UILogicId": "DR_935G",
            "_id": "5bc8189d68142800016a6937",
            "icon": "5c7384767b93c700013f12e7",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c7384767b93c700013f12e7",
            "materialNo": "960",
            "name": "DEEBOT OZMO 960",
            "ota": True,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": False,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "9akc61",
        "product": {
            "UILogicId": "D_500",
            "_id": "5c763f8263023c0001e7f855",
            "icon": "5c932067280fda0001770d7f",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c932067280fda0001770d7f",
            "materialNo": "D505",
            "name": "DEEBOT 505",
            "ota": False,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "r8ead0",
        "product": {
            "UILogicId": "D_500",
            "_id": "5c763f63280fda0001770b88",
            "icon": "5c93204b63023c0001e7faa7",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c93204b63023c0001e7faa7",
            "materialNo": "D502",
            "name": "DEEBOT 502",
            "ota": False,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "emzppx",
        "product": {
            "UILogicId": "D_500",
            "_id": "5c763f35280fda0001770b84",
            "icon": "5c931fef280fda0001770d7e",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c931fef280fda0001770d7e",
            "materialNo": "D501",
            "name": "DEEBOT 501",
            "ota": False,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "vsc5ia",
        "product": {
            "UILogicId": "D_500",
            "_id": "5c763eba280fda0001770b81",
            "icon": "5c874326280fda0001770d2a",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c874326280fda0001770d2a",
            "materialNo": "D500",
            "name": "DEEBOT 500",
            "ota": False,
            "supportType": {
                "alexa": True,
                "assistant": True,
                "share": True,
                "tmjl": False,
            },
        },
    },
    {
        "classid": "aqdd5p",
        "product": {
            "UILogicId": "D_900",
            "_id": "5cb7cfba179839000114d762",
            "icon": "5cb7cfbab72c4d00010e5fc7",
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5cb7cfbab72c4d00010e5fc7",
            "materialNo": "110-1711-0001",
            "name": "DEEBOT DE55",
            "ota": True,
            "supportType": {
                "alexa": False,
                "assistant": False,
                "share": False,
                "tmjl": False,
            },
        },
    },
]


RETURN_API_SUCCESS = "0000"
ERR_ACTIVATE_TOKEN_TIMEOUT = "1006"
ERR_COMMON = "0001"
ERR_DEFAULT = "9000"
ERR_EMAIL_NON_EXIST = "1002"
ERR_EMAIL_SEND_TIME_LIMIT = "1011"
ERR_EMAIL_USED = "1001"
ERR_INTERFACE_AUTH = "0002"
ERR_PARAM_INVALID = "0003"
ERR_PWD_WRONG = "1005"
ERR_RESET_PWD_TOKEN_TIMEOUT = "1007"
ERR_TIMESTAMP_INVALID = "0005"
ERR_TOKEN_INVALID = "0004"
ERR_USER_DISABLE = "1004"
ERR_USER_NOT_ACTIVATED = "1003"
ERR_WRONG_COMFIRM_PWD = "10010"
ERR_WRONG_EMAIL_ADDRESS = "1008"
ERR_WRONG_PWD_FROMATE = "1009"

API_ERRORS = {
    RETURN_API_SUCCESS: "0000",
    ERR_ACTIVATE_TOKEN_TIMEOUT: "1006",
    ERR_COMMON: "0001",
    ERR_DEFAULT: "9000",
    ERR_EMAIL_NON_EXIST: "1002",
    ERR_EMAIL_SEND_TIME_LIMIT: "1011",
    ERR_EMAIL_USED: "1001",
    ERR_INTERFACE_AUTH: "0002",
    ERR_PARAM_INVALID: "0003",
    ERR_PWD_WRONG: "1005",
    ERR_RESET_PWD_TOKEN_TIMEOUT: "1007",
    ERR_TIMESTAMP_INVALID: "0005",
    ERR_TOKEN_INVALID: "0004",
    ERR_USER_DISABLE: "1004",
    ERR_USER_NOT_ACTIVATED: "1003",
    ERR_WRONG_COMFIRM_PWD: "10010",
    ERR_WRONG_EMAIL_ADDRESS: "1008",
    ERR_WRONG_PWD_FROMATE: "1009",
}

