#!/usr/bin/env python3
import json
import uuid
from datetime import datetime, timedelta

import bumper


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


class OAuth:
    access_token = ""
    expire_at = ""
    refresh_token = ""
    userId = ""

    def __init__(self, **entries):
        self.__dict__.update(entries)

    @classmethod
    def create_new(cls, userId: str):
        oauth = OAuth()
        oauth.userId = userId
        oauth.access_token = uuid.uuid4().hex
        oauth.expire_at = "{}".format(datetime.utcnow() + timedelta(days=bumper.oauth_validity_days))
        oauth.refresh_token = uuid.uuid4().hex
        return oauth

    def toDB(self):
        return self.__dict__

    def toResponse(self):
        data = self.__dict__
        data["expire_at"] = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time(
            datetime.fromisoformat(self.expire_at).timestamp())
        return data


# EcoVacs Home Product IOT Map - 2022-03-20
# https://portal-ww.ecouser.net/api/pim/product/getProductIotMap
EcoVacsHomeProducts = [
    {
        "classid": "dl8fht",
        "product": {
            "_id": "5acb0fa87c295c0001876ecf",
            "materialNo": "702-0000-0170",
            "name": "DEEBOT 600 Series",
            "icon": "5acc32067c295c0001876eea",
            "model": "D600",
            "UILogicId": "D_600",
            "ota": False,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5acc32067c295c0001876eea"
        }
    },
    {
        "classid": "02uwxm",
        "product": {
            "_id": "5ae1481e7ccd1a0001e1f69e",
            "materialNo": "110-1715-0201",
            "name": "DEEBOT OZMO Slim10 Series",
            "icon": "60810dddd18cbd0008e2fd27",
            "model": "SLIM10",
            "UILogicId": "D_OZMO_SLIM10",
            "ota": False,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60810dddd18cbd0008e2fd27"
        }
    },
    {
        "classid": "y79a7u",
        "product": {
            "_id": "5b04c0227ccd1a0001e1f6a8",
            "materialNo": "110-1810-0101",
            "name": "DEEBOT OZMO 900 Series",
            "icon": "5b04c0217ccd1a0001e1f6a7",
            "model": "DN5G",
            "UILogicId": "D_OZMO_900",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b04c0217ccd1a0001e1f6a7"
        }
    },
    {
        "classid": "jr3pqa",
        "product": {
            "_id": "5b43077b8bc457000140363e",
            "materialNo": "702-0000-0202",
            "name": "DEEBOT 711",
            "icon": "5b5ac4cc8d5a56000111e769",
            "model": "D711",
            "UILogicId": "D_700",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4cc8d5a56000111e769"
        }
    },
    {
        "classid": "uv242z",
        "product": {
            "_id": "5b5149b4ac0b87000148c128",
            "materialNo": "702-0000-0205",
            "name": "DEEBOT 710",
            "icon": "5b5ac4e45f21100001882bb9",
            "model": "D700",
            "UILogicId": "D_700",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4e45f21100001882bb9"
        }
    },
    {
        "classid": "ls1ok3",
        "product": {
            "_id": "5b6561060506b100015c8868",
            "materialNo": "110-1711-0201",
            "name": "DEEBOT 900 Series",
            "icon": "5ba4a2cb6c2f120001c32839",
            "model": "DN5G",
            "UILogicId": "D_900",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ba4a2cb6c2f120001c32839"
        }
    },
    {
        "classid": "eyi9jv",
        "product": {
            "_id": "5b7b65f364e1680001a08b54",
            "materialNo": "702-0000-0203",
            "name": "DEEBOT 715",
            "icon": "5b7b65f176f7f10001e9a0c2",
            "model": "DV3G",
            "UILogicId": "D_700",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b7b65f176f7f10001e9a0c2"
        }
    },
    {
        "classid": "4zfacv",
        "product": {
            "_id": "5bf2596f23244a00013f2f13",
            "materialNo": "910",
            "name": "DEEBOT 910",
            "icon": "5c778731280fda0001770ba0",
            "model": "DN2_INTL",
            "UILogicId": "DN_2G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c778731280fda0001770ba0"
        }
    },
    {
        "classid": "115",
        "product": {
            "_id": "5bbedd2822d57f00018c13b7",
            "materialNo": "110-1602-0101",
            "name": "DEEBOT OZMO/PRO 930 Series",
            "icon": "5cf711aeb0acfc000179ff8a",
            "model": "DR930",
            "UILogicId": "DR_930G",
            "ota": True,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5cf711aeb0acfc000179ff8a"
        }
    },
    {
        "classid": "vi829v",
        "product": {
            "_id": "5c19a8f3a1e6ee0001782247",
            "materialNo": "110-1819-0101",
            "name": "DEEBOT OZMO 920 Series",
            "icon": "606278d3fc527c00087fdb08",
            "model": "DX5G",
            "UILogicId": "DX_5G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606278d3fc527c00087fdb08"
        }
    },
    {
        "classid": "yna5xi",
        "product": {
            "_id": "5c19a91ca1e6ee000178224a",
            "materialNo": "110-1820-0101",
            "name": "DEEBOT OZMO 950 Series",
            "icon": "606278df4a84d700082b39f1",
            "model": "DX9G",
            "UILogicId": "DX_9G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606278df4a84d700082b39f1"
        }
    },
    {
        "classid": "gd4uut",
        "product": {
            "_id": "5bc8189d68142800016a6937",
            "materialNo": "110-1803-0101",
            "name": "DEEBOT OZMO 960",
            "icon": "5e8da019032edd9008c66bf0",
            "model": "DG7G",
            "UILogicId": "DR_935G",
            "ota": True,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5e8da019032edd9008c66bf0"
        }
    },
    {
        "classid": "m7lqzi",
        "product": {
            "_id": "5c653edf7b93c700013f12cc",
            "materialNo": "113-1708-0001",
            "name": "ATMOBOT Pro",
            "icon": "5d2c63a5ba13eb00013feab7",
            "model": "AA30G",
            "UILogicId": "AA_30G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c63a5ba13eb00013feab7"
        }
    },
    {
        "classid": "9akc61",
        "product": {
            "_id": "5c763f8263023c0001e7f855",
            "materialNo": "20200115005",
            "name": "DEEBOT 505",
            "icon": "5c932067280fda0001770d7f",
            "model": "D505",
            "UILogicId": "D_500",
            "ota": False,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c932067280fda0001770d7f"
        }
    },
    {
        "classid": "r8ead0",
        "product": {
            "_id": "5c763f63280fda0001770b88",
            "materialNo": "702-0000-0161",
            "name": "DEEBOT 502",
            "icon": "5c93204b63023c0001e7faa7",
            "model": "D502",
            "UILogicId": "D_500",
            "ota": False,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c93204b63023c0001e7faa7"
        }
    },
    {
        "classid": "emzppx",
        "product": {
            "_id": "5c763f35280fda0001770b84",
            "materialNo": "702-0000-0169",
            "name": "DEEBOT 501",
            "icon": "5c931fef280fda0001770d7e",
            "model": "D501",
            "UILogicId": "D_500",
            "ota": False,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c931fef280fda0001770d7e"
        }
    },
    {
        "classid": "vsc5ia",
        "product": {
            "_id": "5c763eba280fda0001770b81",
            "materialNo": "702-0000-0163",
            "name": "DEEBOT 500",
            "icon": "5c874326280fda0001770d2a",
            "model": "D500",
            "UILogicId": "D_500",
            "ota": False,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c874326280fda0001770d2a"
        }
    },
    {
        "classid": "142",
        "product": {
            "_id": "5ca1ca7a12851900016858bd",
            "materialNo": "110-1640-0101",
            "name": "DEEBOT Mini2",
            "icon": "5ca1ca79e9e9270001354b2d",
            "model": "Mini2",
            "UILogicId": "ECO_INTL_142",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ca1ca79e9e9270001354b2d"
        }
    },
    {
        "classid": "129",
        "product": {
            "_id": "5ca31df1e9e9270001354b35",
            "materialNo": "110-1628-0101",
            "name": "DEEBOT M86",
            "icon": "5ca31df112851900016858c0",
            "model": "M86",
            "UILogicId": "ECO_INTL_129",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ca31df112851900016858c0"
        }
    },
    {
        "classid": "165",
        "product": {
            "_id": "5ca32a11e9e9270001354b39",
            "materialNo": "702-0000-0189",
            "name": "DEEBOT N79T/W",
            "icon": "5ca32a1012851900016858c6",
            "model": "N79T",
            "UILogicId": "ECO_INTL_165",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ca32a1012851900016858c6"
        }
    },
    {
        "classid": "126",
        "product": {
            "_id": "5ca32ab212851900016858c7",
            "materialNo": "702-0000-0136",
            "name": "DEEBOT N79",
            "icon": "5ca32ab2e9e9270001354b3d",
            "model": "N79",
            "UILogicId": "ECO_INTL_126",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ca32ab2e9e9270001354b3d"
        }
    },
    {
        "classid": "159",
        "product": {
            "_id": "5ca32bc2e9e9270001354b41",
            "materialNo": "110-1629-0203",
            "name": "DEEBOT OZMO 601",
            "icon": "5d4b7606de51dd0001fee12d",
            "model": "159",
            "UILogicId": "ECO_INTL_159",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d4b7606de51dd0001fee12d"
        }
    },
    {
        "classid": "0xyhhr",
        "product": {
            "_id": "5ca4716312851900016858cd",
            "materialNo": "110-1825-0201",
            "name": "DEEBOT OZMO 700",
            "icon": "5d117d4f0ac6ad00012b792d",
            "model": "DV5G",
            "UILogicId": "DV_5G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d117d4f0ac6ad00012b792d"
        }
    },
    {
        "classid": "125",
        "product": {
            "_id": "5cae9703128519000168596a",
            "materialNo": "110-1638-0102",
            "name": "DEEBOT M80 Pro",
            "icon": "5d2c14414d60de0001eaf1f2",
            "model": "M80",
            "UILogicId": "ECO_INTL_125",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c14414d60de0001eaf1f2"
        }
    },
    {
        "classid": "141",
        "product": {
            "_id": "5cae97c9128519000168596f",
            "materialNo": "110-1638-0101",
            "name": "DEEBOT M81 Pro",
            "icon": "5d2c2aa64d60de0001eaf1f6",
            "model": "M81",
            "UILogicId": "ECO_INTL_141",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c2aa64d60de0001eaf1f6"
        }
    },
    {
        "classid": "130",
        "product": {
            "_id": "5cae98d01285190001685974",
            "materialNo": "110-1629-0201",
            "name": "DEEBOT OZMO 610 Series",
            "icon": "5d4b7640de51dd0001fee131",
            "model": "OZMO600",
            "UILogicId": "ECO_INTL_130",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d4b7640de51dd0001fee131"
        }
    },
    {
        "classid": "123",
        "product": {
            "_id": "5cae9b201285190001685977",
            "materialNo": "110-1639-0102",
            "name": "DEEBOT Slim2 Series",
            "icon": "5d2c150dba13eb00013feaae",
            "model": "Slim2",
            "UILogicId": "ECO_INTL_123",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c150dba13eb00013feaae"
        }
    },
    {
        "classid": "aqdd5p",
        "product": {
            "_id": "5cb7cfba179839000114d762",
            "materialNo": "110-1711-0001",
            "name": "DEEBOT DE55",
            "icon": "5cb7cfbab72c4d00010e5fc7",
            "model": "DE5G",
            "UILogicId": "D_900",
            "ota": True,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5cb7cfbab72c4d00010e5fc7"
        }
    },
    {
        "classid": "152",
        "product": {
            "_id": "5cbd97b961526a00019799bd",
            "materialNo": "110-1628-0302",
            "name": "DEEBOT",
            "icon": "5d4b7628de51dd0001fee12f",
            "model": "D600",
            "UILogicId": "ECO_INTL_152",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d4b7628de51dd0001fee12f"
        }
    },
    {
        "classid": "155",
        "product": {
            "_id": "5cce893813afb7000195d6af",
            "materialNo": "702-0000-0164",
            "name": "DEEBOT N79S/SE",
            "icon": "5cd4ca505b032200015a455d",
            "model": "DN622",
            "UILogicId": "ECO_INTL_155",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5cd4ca505b032200015a455d"
        }
    },
    {
        "classid": "jjccwk",
        "product": {
            "_id": "5ce7870cd85b4d0001775db9",
            "materialNo": "20200115004",
            "name": "DEEBOT OZMO 750",
            "icon": "5d3aa309ba13eb00013feb69",
            "model": "DV6G",
            "UILogicId": "DV_6G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d3aa309ba13eb00013feb69"
        }
    },
    {
        "classid": "d0cnel",
        "product": {
            "_id": "5ceba1c6d85b4d0001776986",
            "materialNo": "702-0000-0204",
            "name": "DEEBOT 711s",
            "icon": "5d157f9f77a3a60001051f69",
            "model": "D711S",
            "UILogicId": "D_700",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d157f9f77a3a60001051f69"
        }
    },
    {
        "classid": "140",
        "product": {
            "_id": "5cd43b4cf542e00001dc2dec",
            "materialNo": "110-1639-0011",
            "name": "DEEBOT Slim Neo",
            "icon": "5d2c152f4d60de0001eaf1f4",
            "model": "SlimNeo",
            "UILogicId": "ECO_INTL_140",
            "ota": False,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d2c152f4d60de0001eaf1f4"
        }
    },
    {
        "classid": "2pv572",
        "product": {
            "_id": "5d1474630ac6ad00012b7940",
            "materialNo": "110-1810-0107",
            "name": "DEEBOT OZMO 905",
            "icon": "5d1474632a6bd50001b5b6f3",
            "model": "OZMO905",
            "UILogicId": "D_OZMO_900",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d1474632a6bd50001b5b6f3"
        }
    },
    {
        "classid": "xb83mv",
        "product": {
            "_id": "5d246180350e7a0001e84bea",
            "materialNo": "88393939393",
            "name": "DEEBOT U3",
            "icon": "5d3fe649de51dd0001fee0de",
            "model": "SLIM4_INTL",
            "UILogicId": "DK_4G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d3fe649de51dd0001fee0de"
        }
    },
    {
        "classid": "4f0c4e",
        "product": {
            "_id": "5d2c5fcd4d60de0001eaf2a5",
            "materialNo": "70200000227",
            "name": "AT01",
            "icon": "5d2d996c4d60de0001eaf2b5",
            "model": "AT01",
            "UILogicId": "AT_01G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d2d996c4d60de0001eaf2b5"
        }
    },
    {
        "classid": "q1v5dn",
        "product": {
            "_id": "5d312ae18d8d430001817002",
            "materialNo": "70200000228",
            "name": "AT01",
            "icon": "5d83375f6b6a570001569e26",
            "model": "AT01",
            "UILogicId": "AT_01G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d83375f6b6a570001569e26"
        }
    },
    {
        "classid": "16wdph",
        "product": {
            "_id": "5d280ce344af3600013839ab",
            "materialNo": "702-0000-0171",
            "name": "DEEBOT 661",
            "icon": "5d280ce3350e7a0001e84c95",
            "model": "D661",
            "UILogicId": "D_661",
            "ota": False,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5d280ce3350e7a0001e84c95"
        }
    },
    {
        "classid": "zi1uwd",
        "product": {
            "_id": "5d78f4e878d8b60001e23edc",
            "materialNo": "3",
            "name": "DEEBOT U3 LINE FRIENDS",
            "icon": "5da834a8d66cd10001f58265",
            "model": "DK4G.11",
            "UILogicId": "DK_4GLINE",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5da834a8d66cd10001f58265"
        }
    },
    {
        "classid": "x5d34r",
        "product": {
            "_id": "5de0d86ed88546000195239a",
            "materialNo": "110-1913-0101",
            "name": "DEEBOT OZMO T8 AIVI",
            "icon": "605053e7fc527c00087fda1e",
            "model": "DXAI_INTL",
            "UILogicId": "DX_AIG",
            "ota": True,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/605053e7fc527c00087fda1e"
        }
    },
    {
        "classid": "1qdu4z",
        "product": {
            "_id": "5de9b7f50136c00001cb1f96",
            "materialNo": "117-1923-0101",
            "name": "Aaron",
            "icon": "5e71c7df298f0d9cabfef86f",
            "model": "AT80K",
            "UILogicId": "AT80",
            "ota": False,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5e71c7df298f0d9cabfef86f"
        }
    },
    {
        "classid": "jh3ry2",
        "product": {
            "_id": "5de9b77f0136c00001cb1f8e",
            "materialNo": "113-1931-0003",
            "name": "AVA",
            "icon": "6049b34d1269020008a95aef",
            "model": "AVA",
            "UILogicId": "ATMOBOT_AVA",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6049b34d1269020008a95aef"
        }
    },
    {
        "classid": "hsgwhi",
        "product": {
            "_id": "5de9b6fb787cdf0001ef98ac",
            "materialNo": "113-1931-0001",
            "name": "ANDY",
            "icon": "5e731a4a06f6de700464c69d",
            "model": "ANDY",
            "UILogicId": "ATMOBOT_ANDY",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5e731a4a06f6de700464c69d"
        }
    },
    {
        "classid": "9rft3c",
        "product": {
            "_id": "5e14196a6e71b80001b60fda",
            "materialNo": "191165",
            "name": "DEEBOT OZMO T5",
            "icon": "6062795ad18cbd0008e2fce8",
            "model": "DX9G_T5",
            "UILogicId": "DX_9G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6062795ad18cbd0008e2fce8"
        }
    },
    {
        "classid": "jffnlf",
        "product": {
            "_id": "5e53208426be716edf4b55cf",
            "materialNo": "130-6311-1702",
            "name": "DEEBOT N3 MAX",
            "icon": "5e53207a26be71596c4b55cd",
            "model": "DU3G",
            "UILogicId": "DU_6G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5e53207a26be71596c4b55cd"
        }
    },
    {
        "classid": "ar5bjb",
        "product": {
            "_id": "5e58a73d36e8f3cab08f031f",
            "materialNo": "130-6211-0610",
            "name": "DEEBOT 665",
            "icon": "5e58a2df36e8f39e318f031d",
            "model": "D665",
            "UILogicId": "D_661",
            "ota": False,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5e58a2df36e8f39e318f031d"
        }
    },
    {
        "classid": "55aiho",
        "product": {
            "_id": "5e698a6306f6de52c264c61b",
            "materialNo": "110-1921-1101",
            "name": "DEEBOT OZMO T8+",
            "icon": "605be27250928b0007c13264",
            "model": "T8+",
            "UILogicId": "DT_8G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/605be27250928b0007c13264"
        }
    },
    {
        "classid": "b742vd",
        "product": {
            "_id": "5e699a4106f6de83ea64c620",
            "materialNo": "110-1921-0301",
            "name": "DEEBOT OZMO T8",
            "icon": "5e8e93a7032edd3f5ec66d4a",
            "model": "T8G",
            "UILogicId": "DT_8G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5e8e93a7032edd3f5ec66d4a"
        }
    },
    {
        "classid": "nq9yhl",
        "product": {
            "_id": "5e8597b0032edd333ac66bbf",
            "materialNo": "110-1919-0601",
            "name": "DEEBOT U2 PRO",
            "icon": "606426ebb0a931000860fad4",
            "model": "U2_AH",
            "UILogicId": "U2_HIGH_MODE_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606426ebb0a931000860fad4"
        }
    },
    {
        "classid": "rvo6ev",
        "product": {
            "_id": "5e859780648255c8bf530e14",
            "materialNo": "110-1919-1001",
            "name": "DEEBOT U2",
            "icon": "606426feb0a931000860fad5",
            "model": "U2_AL",
            "UILogicId": "U2_HIGH_MODE_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606426feb0a931000860fad5"
        }
    },
    {
        "classid": "fqxoiu",
        "product": {
            "_id": "5e8e8d8a032edd8457c66bfb",
            "materialNo": "110-1921-1100",
            "name": "DEEBOT OZMO T8+",
            "icon": "605b059217c95b0008ff20d4",
            "model": "OT8+",
            "UILogicId": "DT_8G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/605b059217c95b0008ff20d4"
        }
    },
    {
        "classid": "h18jkh",
        "product": {
            "_id": "5e8e8d2a032edd3c03c66bf7",
            "materialNo": "110-1921-0400",
            "name": "DEEBOT OZMO T8",
            "icon": "5e8e8d146482551d72530e47",
            "model": "OT8G",
            "UILogicId": "DT_8G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5e8e8d146482551d72530e47"
        }
    },
    {
        "classid": "ipzjy0",
        "product": {
            "_id": "5e9923878c92c7676b835555",
            "materialNo": "110-1919-0702",
            "name": "DEEBOT U2",
            "icon": "606426c64a84d700082b39fa",
            "model": "U2_EL1",
            "UILogicId": "U2_HIGH_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606426c64a84d700082b39fa"
        }
    },
    {
        "classid": "wlqdkp",
        "product": {
            "_id": "5e9924018c92c7c480835559",
            "materialNo": "110-1919-0701",
            "name": "DEEBOT U2",
            "icon": "6064263ad18cbd0008e2fcf4",
            "model": "U2_EL2",
            "UILogicId": "U2_HIGH_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6064263ad18cbd0008e2fcf4"
        }
    },
    {
        "classid": "d4v1pm",
        "product": {
            "_id": "5e9924416a299dddac06d656",
            "materialNo": "110-1919-0802",
            "name": "DEEBOT U2 PRO",
            "icon": "606426254a84d700082b39f9",
            "model": "U2_EH1",
            "UILogicId": "U2_HIGH_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606426254a84d700082b39f9"
        }
    },
    {
        "classid": "7j1tu6",
        "product": {
            "_id": "5e993e566a299d449a06d65a",
            "materialNo": "110-1919-0801",
            "name": "DEEBOT U2 PRO",
            "icon": "6064260545505e0008e5cb49",
            "model": "U2_EH2",
            "UILogicId": "U2_HIGH_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6064260545505e0008e5cb49"
        }
    },
    {
        "classid": "ts2ofl",
        "product": {
            "_id": "5e993e8b8c92c753dd83555f",
            "materialNo": "110-1919-0901",
            "name": "DEEBOT U2",
            "icon": "606425dfd18cbd0008e2fcf3",
            "model": "U2_AUL",
            "UILogicId": "U2_HIGH_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606425dfd18cbd0008e2fcf3"
        }
    },
    {
        "classid": "u4h1uk",
        "product": {
            "_id": "5e993eba8c92c71489835564",
            "materialNo": "110-1919-1101",
            "name": "DEEBOT U2 PRO",
            "icon": "606425bed18cbd0008e2fcf2",
            "model": "U2_JP",
            "UILogicId": "U2_HIGH_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606425bed18cbd0008e2fcf2"
        }
    },
    {
        "classid": "c0lwyn",
        "product": {
            "_id": "5e993eef6a299d7e4a06d660",
            "materialNo": "110-1919-1301",
            "name": "DEEBOT U2 PRO",
            "icon": "606425ab4a84d700082b39f7",
            "model": "U2_AUH",
            "UILogicId": "U2_HIGH_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606425ab4a84d700082b39f7"
        }
    },
    {
        "classid": "u6eqoa",
        "product": {
            "_id": "5e993f2f6a299d0bd506d665",
            "materialNo": "110-1919-1401",
            "name": "DEEBOT U2 PRO",
            "icon": "606425a11269020008a9627d",
            "model": "U2_APAC",
            "UILogicId": "U2_HIGH_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606425a11269020008a9627d"
        }
    },
    {
        "classid": "09m4bu",
        "product": {
            "_id": "5e9d340b8c92c777ab83557f",
            "materialNo": "130-6225-0605",
            "name": "K650",
            "icon": "5ef31b8cee3c1200075b6f67",
            "model": "K651G",
            "UILogicId": "K650_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ef31b8cee3c1200075b6f67"
        }
    },
    {
        "classid": "3ab24g",
        "product": {
            "_id": "5e9d34418c92c717e9835583",
            "materialNo": "130-6225-0302",
            "name": "K650",
            "icon": "5ef31b80f5dcdf000767cf4d",
            "model": "K652G",
            "UILogicId": "K650_RANDOM_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ef31b80f5dcdf000767cf4d"
        }
    },
    {
        "classid": "y2qy3m",
        "product": {
            "_id": "5ea8d28922838d15795ed88d",
            "materialNo": "110-1919-1701",
            "name": "DEEBOT U2 PRO",
            "icon": "606425784a84d700082b39f6",
            "model": "U2_APAC3",
            "UILogicId": "U2_HIGH_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606425784a84d700082b39f6"
        }
    },
    {
        "classid": "12baap",
        "product": {
            "_id": "5ea8d1fe73193e3bef67c551",
            "materialNo": "110-1919-1801",
            "name": "DEEBOT U2 PRO",
            "icon": "606425981269020008a9627b",
            "model": "U2_APAC2",
            "UILogicId": "U2_HIGH_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606425981269020008a9627b"
        }
    },
    {
        "classid": "34vhpm",
        "product": {
            "_id": "5edd998afdd6a30008da039b",
            "materialNo": "110-1913-0501",
            "name": "DEEBOT T8 AIVI +",
            "icon": "605050031269020008a95af9",
            "model": "DXAIS_TW",
            "UILogicId": "DX_AIG",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/605050031269020008a95af9"
        }
    },
    {
        "classid": "tpnwyu",
        "product": {
            "_id": "5edd9a4075f2fc000636086c",
            "materialNo": "110-1913-0401",
            "name": "DEEBOT T8 AIVI +",
            "icon": "6050503e1269020008a95afa",
            "model": "DXAIS_HK",
            "UILogicId": "DX_AIG",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6050503e1269020008a95afa"
        }
    },
    {
        "classid": "wgxm70",
        "product": {
            "_id": "5ed5e4d3a719ea460ec3216c",
            "materialNo": "110-1921-0012",
            "name": "DEEBOT T8",
            "icon": "5edf2bbedb28cc00062f8bd7",
            "model": "T8GC",
            "UILogicId": "DT_8G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5edf2bbedb28cc00062f8bd7"
        }
    },
    {
        "classid": "1zqysa",
        "product": {
            "_id": "5ee85c64fdd6a30008da0af4",
            "materialNo": "110-1919-2201",
            "name": "DEEBOT U2 POWER",
            "icon": "6064258d1269020008a9627a",
            "model": "U2_HK",
            "UILogicId": "U2_HIGH_NOMAG_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6064258d1269020008a9627a"
        }
    },
    {
        "classid": "chmi0g",
        "product": {
            "_id": "5ee85cabfdd6a30008da0af8",
            "materialNo": "110-1919-2301",
            "name": "DEEBOT U2 POWER",
            "icon": "606425821269020008a96279",
            "model": "U2_TW",
            "UILogicId": "U2_HIGH_NOMAG_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606425821269020008a96279"
        }
    },
    {
        "classid": "p5nx9u",
        "product": {
            "_id": "5f0d45404a3cbe00073d17db",
            "materialNo": "110-2022-0001",
            "name": "yeedi 2 hybrid",
            "icon": "5f59e774c0f03a0008ee72e0",
            "model": "K750",
            "UILogicId": "DK_750",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5f59e774c0f03a0008ee72e0"
        }
    },
    {
        "classid": "n6cwdb",
        "product": {
            "_id": "5f729454a541bd000881cc7b",
            "materialNo": "110-2009-0900",
            "name": "DEEBOT N8",
            "icon": "60627a92fc527c00087fdb0a",
            "model": "N8_LDS_WHITE_N",
            "UILogicId": "T5_SE_G_DTOF",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60627a92fc527c00087fdb0a"
        }
    },
    {
        "classid": "lhbd50",
        "product": {
            "_id": "5f88195e6cf8de0008ed7c11",
            "materialNo": "110-2010-1001",
            "name": "DEEBOT T9+",
            "icon": "603f51243b03f50007b6c2ca",
            "model": "DEEBOT_OZMO_T9PLUS",
            "UILogicId": "T9_PRO_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/603f51243b03f50007b6c2ca"
        }
    },
    {
        "classid": "ucn2xe",
        "product": {
            "_id": "5f8819156cf8de0008ed7c0d",
            "materialNo": "110-2010-0301",
            "name": "DEEBOT T9",
            "icon": "603f510e3b03f50007b6c2c9",
            "model": "DEEBOT_OZMO_T9",
            "UILogicId": "T9_PRO_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/603f510e3b03f50007b6c2c9"
        }
    },
    {
        "classid": "0bdtzz",
        "product": {
            "_id": "5fa105c6d16a99000667eb54",
            "materialNo": "110-1921-0404",
            "name": "DEEBOT OZMO T8 PURE",
            "icon": "5fa105bbd16a99000667eb52",
            "model": "OT8_PURE",
            "UILogicId": "DT_8G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5fa105bbd16a99000667eb52"
        }
    },
    {
        "classid": "r5zxjr",
        "product": {
            "_id": "5fa2441169320300086ff812",
            "materialNo": "110-2009-0101",
            "name": "DEEBOT N7",
            "icon": "60627c09b0a931000860facd",
            "model": "N7_LDS",
            "UILogicId": "T5_SE_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60627c09b0a931000860facd"
        }
    },
    {
        "classid": "r5y7re",
        "product": {
            "_id": "5fa4b1f8c7260e000858584b",
            "materialNo": "110-2009-0902",
            "name": "DEEBOT N8",
            "icon": "60627a9cb0a931000860fac7",
            "model": "N8_DTOF_TW",
            "UILogicId": "T5_SE_G_DTOF",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60627a9cb0a931000860fac7"
        }
    },
    {
        "classid": "snxbvc",
        "product": {
            "_id": "5fa4e31dd16a99000667eb94",
            "materialNo": "110-2008-0102",
            "name": "DEEBOT N8 PRO",
            "icon": "60627bbfb0a931000860fac9",
            "model": "N8_PRO_WHITE",
            "UILogicId": "DT_8SE_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60627bbfb0a931000860fac9"
        }
    },
    {
        "classid": "7bryc5",
        "product": {
            "_id": "5fa4e248c7260e0008585850",
            "materialNo": "110-2029-0001",
            "name": "DEEBOT N8+",
            "icon": "5fb474d4d16a99000667edd9",
            "model": "N8_PLUS_WHITE",
            "UILogicId": "N8_PLUS",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5fb474d4d16a99000667edd9"
        }
    },
    {
        "classid": "b2jqs4",
        "product": {
            "_id": "5fbc7cc69601440008b24469",
            "materialNo": "110-2029-0002",
            "name": "DEEBOT N8+",
            "icon": "5feaeb27d4cb3a0006679047",
            "model": "N8_PLUS_BLACK",
            "UILogicId": "N8_PLUS",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5feaeb27d4cb3a0006679047"
        }
    },
    {
        "classid": "yu362x",
        "product": {
            "_id": "5fbc7da39601440008b2446d",
            "materialNo": "110-2008-0103",
            "name": "DEEBOT N8 PRO",
            "icon": "60627bde50928b0007c13273",
            "model": "N8_PRO_BLACK",
            "UILogicId": "DT_8SE_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60627bde50928b0007c13273"
        }
    },
    {
        "classid": "ifbw08",
        "product": {
            "_id": "5fbc7e18c7260e0008585c8f",
            "materialNo": "110-2008-0901",
            "name": "DEEBOT N8 PRO+",
            "icon": "61318e07e37c4686071aee67",
            "model": "N8_PRO_PLUS_WHITE",
            "UILogicId": "DT_8SE_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/61318e07e37c4686071aee67"
        }
    },
    {
        "classid": "85as7h",
        "product": {
            "_id": "5fbc7f5069320300086ffa5e",
            "materialNo": "110-2008-0902",
            "name": "DEEBOT N8 PRO+",
            "icon": "5feaeb585f437d0008e0e00c",
            "model": "N8_PRO_PLUS_BLACK",
            "UILogicId": "DT_8SE_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5feaeb585f437d0008e0e00c"
        }
    },
    {
        "classid": "ty84oi",
        "product": {
            "_id": "5fbcac79c7260e0008585c94",
            "materialNo": "110-2029-1201",
            "name": "DEEBOT N8",
            "icon": "60627bcafc527c00087fdb0c",
            "model": "N8_WHITE",
            "UILogicId": "N8_PLUS",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60627bcafc527c00087fdb0c"
        }
    },
    {
        "classid": "36xnxf",
        "product": {
            "_id": "5fbcacf369320300086ffa63",
            "materialNo": "110-2029-0701",
            "name": "DEEBOT N8",
            "icon": "60627bd517c95b0008ff20ec",
            "model": "N8_BLACK\t",
            "UILogicId": "N8_PLUS",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60627bd517c95b0008ff20ec"
        }
    },
    {
        "classid": "f32i67",
        "product": {
            "_id": "5fc49656d16a99000667f11b",
            "materialNo": "113-1929-0101",
            "name": "AVA",
            "icon": "6049b32ad18cbd0008e2f812",
            "model": "AVA_TW",
            "UILogicId": "ATMOBOT_AVA",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6049b32ad18cbd0008e2f812"
        }
    },
    {
        "classid": "kckkso",
        "product": {
            "_id": "5fcda34ae3a1890008c04afc",
            "materialNo": "117-1923-0200",
            "name": "Aaron",
            "icon": "6010c6be4d8cf90006292d1e",
            "model": "AT80_TW",
            "UILogicId": "AT80",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6010c6be4d8cf90006292d1e"
        }
    },
    {
        "classid": "2pj946",
        "product": {
            "_id": "5fd1e362bbf4b30006cd9255",
            "materialNo": "111-2005-0301",
            "name": "WINBOT 920",
            "icon": "6049b3631269020008a95af0",
            "model": "W920_INT",
            "UILogicId": "winbot_g",
            "ota": True,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6049b3631269020008a95af0"
        }
    },
    {
        "classid": "mnx7f4",
        "product": {
            "_id": "5fdc0afa5f437d0008e0dfa0",
            "materialNo": "110-2025-0101",
            "name": "yeedi vac station",
            "icon": "606e960b45505e0008e5cb55",
            "model": "K781_PLUS",
            "UILogicId": "DK_781_PLUS",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/606e960b45505e0008e5cb55"
        }
    },
    {
        "classid": "04z443",
        "product": {
            "_id": "5fdc0a375f437d0008e0df9b",
            "materialNo": "110-2025-0001",
            "name": "yeedi vac max",
            "icon": "60a201729fe5580009c6d769",
            "model": "K781",
            "UILogicId": "DK_781_PLUS",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60a201729fe5580009c6d769"
        }
    },
    {
        "classid": "vthpeg",
        "product": {
            "_id": "5fe54a90bbf4b30006cd94bf",
            "materialNo": "110-2028-0201",
            "name": "yeedi mop station",
            "icon": "60700a7e1269020008a96293",
            "model": "K850_PLUS",
            "UILogicId": "DK_850",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60700a7e1269020008a96293"
        }
    },
    {
        "classid": "zjna8m",
        "product": {
            "_id": "5ff6a194ac51bf0008d98390",
            "materialNo": "130-6225-0303",
            "name": "DEEBOT U2 SE",
            "icon": "6064256ed18cbd0008e2fcee",
            "model": "U2_SE",
            "UILogicId": "U2_HIGH_MODE_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6064256ed18cbd0008e2fcee"
        }
    },
    {
        "classid": "659yh8",
        "product": {
            "_id": "60361d6134bf63000719d2e1",
            "materialNo": "110-2011-0101",
            "name": "DEEBOT T9 AIVI",
            "icon": "603f5147c8115100083364bc",
            "model": "T9_AIVI_INT",
            "UILogicId": "T9_AF_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/603f5147c8115100083364bc"
        }
    },
    {
        "classid": "w16crm",
        "product": {
            "_id": "604083d91da61a00082303c4",
            "materialNo": "110-1913-0701",
            "name": "DEEBOT OZMO T8 AIVI+",
            "icon": "605053f7d18cbd0008e2f814",
            "model": "DXAIS_US",
            "UILogicId": "DX_AIG",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/605053f7d18cbd0008e2f814"
        }
    },
    {
        "classid": "c2of2s",
        "product": {
            "_id": "6045c070c8115100083364d7",
            "materialNo": "130-6224-1306",
            "name": "DEEBOT N9+",
            "icon": "61318dbc1d27796ece1d1baa",
            "model": "N9_PLUS_TW",
            "UILogicId": "DK_850",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/61318dbc1d27796ece1d1baa"
        }
    },
    {
        "classid": "um2ywg",
        "product": {
            "_id": "608b9981fc527c00087fddf1",
            "materialNo": "110-2010-1102",
            "name": "DEEBOT T9+",
            "icon": "608b997e17c95b0008ff221f",
            "model": "T9_PLUS_ECO_INT",
            "UILogicId": "T9_PRO_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/608b997e17c95b0008ff221f"
        }
    },
    {
        "classid": "ipohi5",
        "product": {
            "_id": "608b98c9d18cbd0008e2fd72",
            "materialNo": "110-2010-0402",
            "name": "DEEBOT T9",
            "icon": "608b98c51269020008a962db",
            "model": "T9_ECO_INT",
            "UILogicId": "T9_PRO_G",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/608b98c51269020008a962db"
        }
    },
    {
        "classid": "u5vcmk",
        "product": {
            "_id": "609383dcd18cbd0008e2fd7f",
            "materialNo": "110-2025-0701",
            "name": "yeedi vac",
            "icon": "60a2017babb8be0008b6ad16",
            "model": "K760_US",
            "UILogicId": "DK_781_PLUS",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60a2017babb8be0008b6ad16"
        }
    },
    {
        "classid": "h041es",
        "product": {
            "_id": "609384184a84d700082b3ab4",
            "materialNo": "110-2025-0801",
            "name": "yeedi vac hybrid",
            "icon": "60a201829fe5580009c6d76a",
            "model": "K760_EU",
            "UILogicId": "DK_781_PLUS",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60a201829fe5580009c6d76a"
        }
    },
    {
        "classid": "l01kak",
        "product": {
            "_id": "60d59457c89066000866a441",
            "materialNo": "113-1931-0005",
            "name": "AVA",
            "icon": "60ece97ed4fc6e0008e4aaa5",
            "model": "AVA_INA",
            "UILogicId": "ATMOBOT_AVA_IN",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60ece97ed4fc6e0008e4aaa5"
        }
    },
    {
        "classid": "5089oy",
        "product": {
            "_id": "60dd6db7d4fc6e0008e4aa92",
            "materialNo": "110-1913-0502",
            "name": "DEEBOT T8 AIVI",
            "icon": "60dd6db3038a38000888bd5b",
            "model": "DXAI_TW",
            "UILogicId": "DX_AIG",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60dd6db3038a38000888bd5b"
        }
    },
    {
        "classid": "yu7oqr",
        "product": {
            "_id": "60fa62b779330100089a7ce2",
            "materialNo": "111-2005-0202",
            "name": "WINBOT 920",
            "icon": "60fa62b079330100089a7ce0",
            "model": "W920_INT_GD",
            "UILogicId": "winbot_g",
            "ota": True,
            "supportType": {
                "share": False,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/60fa62b079330100089a7ce0"
        }
    },
    {
        "classid": "uzhlnc",
        "product": {
            "_id": "6111dae95a2dff000a243361",
            "materialNo": "117-1923-0004",
            "name": "Aaron",
            "icon": "6111dafd5a2dff000a243364",
            "model": "AT80_INA",
            "UILogicId": "AT80",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": False,
                "alexa": False
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6111dafd5a2dff000a243364"
        }
    },
    {
        "classid": "zwvyi2",
        "product": {
            "_id": "616cc8326bb5143b3610a9c2",
            "materialNo": "110-2030-0101",
            "name": "yeedi mop station pro",
            "icon": "61cd6ea0258755faa61c832d",
            "model": "K850_PLUS_NEW_INT",
            "UILogicId": "k850_ww_h_k850",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/61cd6ea0258755faa61c832d"
        }
    },
    {
        "classid": "aaxesz",
        "product": {
            "_id": "616d08d06bb5142d1c10a9c7",
            "materialNo": "110-2120-0000",
            "name": "yeedi vac 2 pro",
            "icon": "61b0498272e305141cc11624",
            "model": "K950_INT",
            "UILogicId": "k950_ww_h_k950",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/61b0498272e305141cc11624"
        }
    },
    {
        "classid": "n4gstt",
        "product": {
            "_id": "616d2125b0011d60087a18f2",
            "materialNo": "110-2115-0201",
            "name": "DEEBOT X1 PLUS",
            "icon": "61c422316de01220a2adb91d",
            "model": "NEWTON_AES_INT",
            "UILogicId": "t10_ww_n_newtonaes",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/61c422316de01220a2adb91d"
        }
    },
    {
        "classid": "9t30w8",
        "product": {
            "_id": "6180a06b9a411f259e2c41ef",
            "materialNo": "110-2120-0700",
            "name": "yeedi vac 2",
            "icon": "61b0497b658e844efac7848d",
            "model": "K950L",
            "UILogicId": "k950_ww_h_k950",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/61b0497b658e844efac7848d"
        }
    },
    {
        "classid": "1vxt52",
        "product": {
            "_id": "6185e29610683da4d6a7a9cd",
            "materialNo": "110-2102-0300",
            "name": "DEEBOT X1 OMNI",
            "icon": "6225bd1c2af2127804f540e5",
            "model": "EINSTEIN_INT",
            "UILogicId": "t10_ww_n_omni",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6225bd1c2af2127804f540e5"
        }
    },
    {
        "classid": "2o4lnm",
        "product": {
            "_id": "6185e87035d0b97c64df03d8",
            "materialNo": "110-2102-0601",
            "name": "DEEBOT X1 TURBO",
            "icon": "6225bd3b7604e551a50e46ac",
            "model": "TURING_ACS_INT",
            "UILogicId": "t10_ww_n_turingacs",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/6225bd3b7604e551a50e46ac"
        }
    },
    {
        "classid": "1b23du",
        "product": {
            "_id": "619765fbcfdd5e320a1f61f6",
            "materialNo": "110-2102-0302",
            "name": "DEEBOT X1 OMNI",
            "icon": "61c58ddc75bfe17354e4804e",
            "model": "EINSTEIN_WHITE_INT",
            "UILogicId": "t10_ww_n_omniwhite",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/61c58ddc75bfe17354e4804e"
        }
    },
    {
        "classid": "rss8xk",
        "product": {
            "_id": "61a577a89bc93f5dca07b15f",
            "materialNo": "110-2113-0500",
            "name": "DEEBOT T10 PLUS",
            "icon": "61e90bbbfe80232316d12ea7",
            "model": "CURIE_AES_INT",
            "UILogicId": "t10_ww_n_curieaesnoyiko",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/61e90bbbfe80232316d12ea7"
        }
    },
    {
        "classid": "z0gd1j",
        "product": {
            "_id": "61a7126ed3028324ec98df93",
            "materialNo": "110-2029-1002",
            "name": "DEEBOT Neo",
            "icon": "61a712dbd540b3fc0684cdd6",
            "model": "N8_NEO",
            "UILogicId": "N8_PLUS",
            "ota": True,
            "supportType": {
                "share": True,
                "tmjl": False,
                "assistant": True,
                "alexa": True
            },
            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/61a712dbd540b3fc0684cdd6"
        }
    }
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
