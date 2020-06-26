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

    def asdict(self):
        return {
            "class": self.vac_bot_device_class,
            "company": self.company,
            "did": self.did,
            "name": self.name,
            "nick": self.nick,
            "resource": self.resource,
            "mqtt_connection": self.mqtt_connection,
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

    def asdict(self):
        return {
            "userid": self.userid,
            "realm": self.realm,
            "resource": self.resource,
            "mqtt_connection": self.mqtt_connection,
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


# EcoVacs Home Product IOT Map - 2020-01-05
# https://portal-ww.ecouser.net/api/pim/product/getProductIotMap
EcoVacsHomeProducts = [
  {
    "classid": "dl8fht",
    "product": {
      "_id": "5acb0fa87c295c0001876ecf",
      "materialNo": "702-0000-0170",
      "name": "DEEBOT 600 Series",
      "icon": "5acc32067c295c0001876eea",
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
      "icon": "5b1dddc48bc45700014035a1",
      "UILogicId": "D_OZMO_SLIM10",
      "ota": False,
      "supportType": {
        "share": True,
        "tmjl": False,
        "assistant": True,
        "alexa": True
      },
      "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b1dddc48bc45700014035a1"
    }
  },
  {
    "classid": "y79a7u",
    "product": {
      "_id": "5b04c0227ccd1a0001e1f6a8",
      "materialNo": "110-1810-0101",
      "name": "DEEBOT OZMO 900 Series",
      "icon": "5b04c0217ccd1a0001e1f6a7",
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
      "materialNo": "702-0000-0202",
      "name": "DEEBOT 715",
      "icon": "5b7b65f176f7f10001e9a0c2",
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
      "icon": "5c9c7995e9e9270001354ab4",
      "UILogicId": "DX_5G",
      "ota": True,
      "supportType": {
        "share": True,
        "tmjl": False,
        "assistant": True,
        "alexa": True
      },
      "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c9c7995e9e9270001354ab4"
    }
  },
  {
    "classid": "yna5xi",
    "product": {
      "_id": "5c19a91ca1e6ee000178224a",
      "materialNo": "110-1820-0101",
      "name": "DEEBOT OZMO 950 Series",
      "icon": "5caafd7e1285190001685965",
      "UILogicId": "DX_9G",
      "ota": True,
      "supportType": {
        "share": True,
        "tmjl": False,
        "assistant": True,
        "alexa": True
      },
      "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5caafd7e1285190001685965"
    }
  },
  {
    "classid": "gd4uut",
    "product": {
      "_id": "5bc8189d68142800016a6937",
      "materialNo": "110-1803-0101",
      "name": "DEEBOT OZMO 960",
      "icon": "5c7384767b93c700013f12e7",
      "UILogicId": "DR_935G",
      "ota": True,
      "supportType": {
        "share": False,
        "tmjl": False,
        "assistant": True,
        "alexa": True
      },
      "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5c7384767b93c700013f12e7"
    }
  },
  {
    "classid": "m7lqzi",
    "product": {
      "_id": "5c653edf7b93c700013f12cc",
      "materialNo": "113-1708-0001",
      "name": "ATMOBOT Pro",
      "icon": "5d2c63a5ba13eb00013feab7",
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
      "materialNo": "702-0000-0163",
      "name": "DEEBOT 505",
      "icon": "5c932067280fda0001770d7f",
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
      "materialNo": "702-0000-0163",
      "name": "DEEBOT 502",
      "icon": "5c93204b63023c0001e7faa7",
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
      "materialNo": "702-0000-0163",
      "name": "DEEBOT 501",
      "icon": "5c931fef280fda0001770d7e",
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
      "materialNo": "702-0000-0163",
      "name": "DEEBOT N79S/SE",
      "icon": "5cd4ca505b032200015a455d",
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
      "materialNo": "110-1825-0201",
      "name": "DEEBOT OZMO 750",
      "icon": "5d3aa309ba13eb00013feb69",
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
      "materialNo": "702-0000-0202",
      "name": "DEEBOT 711s",
      "icon": "5d157f9f77a3a60001051f69",
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
      "materialNo": "702-0000-0170",
      "name": "DEEBOT 661",
      "icon": "5d280ce3350e7a0001e84c95",
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

