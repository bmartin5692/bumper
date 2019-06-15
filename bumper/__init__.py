#!/usr/bin/env python3

from bumper.confserver import ConfServer
from bumper.mqttserver import MQTTServer, MQTTHelperBot
from bumper.xmppserver import XMPPServer
import asyncio
import json
from datetime import datetime, timedelta
import os
import logging
from logging.handlers import RotatingFileHandler
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
import socket
import sys


def strtobool(strbool):
    if str(strbool).lower() in ["true", "1", "t", "y", "on", "yes"]:
        return True
    else:
        return False


# os.environ['PYTHONASYNCIODEBUG'] = '1' # Uncomment to enable ASYNCIODEBUG
bumper_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# Set defaults from environment variables first
print(bumper_dir)
# Folders
logs_dir = os.environ.get("BUMPER_LOGS") or os.path.join(bumper_dir, "logs")
os.makedirs(logs_dir, exist_ok=True)  # Ensure logs directory exists or create
print(logs_dir)
data_dir = os.environ.get("BUMPER_DATA") or os.path.join(bumper_dir, "data")
os.makedirs(data_dir, exist_ok=True)  # Ensure data directory exists or create
print(data_dir)
certs_dir = os.environ.get("BUMPER_CERTS") or os.path.join(bumper_dir, "certs")
os.makedirs(certs_dir, exist_ok=True)  # Ensure data directory exists or create
print(certs_dir)


# Certs
ca_cert = os.environ.get("BUMPER_CA") or os.path.join(certs_dir, "ca.crt")
print(ca_cert)
server_cert = os.environ.get("BUMPER_CERT") or os.path.join(certs_dir, "bumper.crt")
print(server_cert)
server_key = os.environ.get("BUMPER_KEY") or os.path.join(certs_dir, "bumper.key")
print(server_key)

# Listeners
bumper_listen = os.environ.get("BUMPER_LISTEN") or socket.gethostbyname(
    socket.gethostname()
)


bumper_announce_ip = os.environ.get("BUMPER_ANNOUNCE_IP") or bumper_listen

# Other
bumper_debug = strtobool(os.environ.get("BUMPER_DEBUG")) or False
use_auth = False
token_validity_seconds = 3600  # 1 hour
db = None

mqtt_server = None
mqtt_helperbot = None
conf_server = None
conf_server_2 = None
xmpp_server = None

shutting_down = False

# Set format for all logs
logformat = logging.Formatter(
    "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)d :: %(message)s"
)

bumperlog = logging.getLogger("bumper")
bumper_rotate = RotatingFileHandler("logs/bumper.log", maxBytes=5000000, backupCount=5)
bumper_rotate.setFormatter(logformat)
bumperlog.addHandler(bumper_rotate)
# Override the logging level
# bumperlog.setLevel(logging.INFO)

confserverlog = logging.getLogger("confserver")
conf_rotate = RotatingFileHandler(
    "logs/confserver.log", maxBytes=5000000, backupCount=5
)
conf_rotate.setFormatter(logformat)
confserverlog.addHandler(conf_rotate)
# Override the logging level
# confserverlog.setLevel(logging.INFO)

mqttserverlog = logging.getLogger("mqttserver")
mqtt_rotate = RotatingFileHandler(
    "logs/mqttserver.log", maxBytes=5000000, backupCount=5
)
mqtt_rotate.setFormatter(logformat)
mqttserverlog.addHandler(mqtt_rotate)
# Override the logging level
# mqttserverlog.setLevel(logging.INFO)

helperbotlog = logging.getLogger("helperbot")
helperbot_rotate = RotatingFileHandler(
    "logs/helperbot.log", maxBytes=5000000, backupCount=5
)
helperbot_rotate.setFormatter(logformat)
helperbotlog.addHandler(helperbot_rotate)
# Override the logging level
# helperbotlog.setLevel(logging.INFO)

xmppserverlog = logging.getLogger("xmppserver")
xmpp_rotate = RotatingFileHandler(
    "logs/xmppserver.log", maxBytes=5000000, backupCount=5
)
xmpp_rotate.setFormatter(logformat)
xmppserverlog.addHandler(xmpp_rotate)
# Override the logging level
# xmppserverlog.setLevel(logging.INFO)

logging.getLogger("asyncio").setLevel(logging.CRITICAL + 1)  # Ignore this logger


mqtt_listen_port = 8883
conf1_listen_port = 443
conf2_listen_port = 8007
xmpp_listen_port = 5223


async def start():

    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()

    if bumper_debug:
        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)d :: %(message)s",
        )
        loop.set_debug(True)  # Set asyncio loop to debug
        # logging.getLogger("asyncio").setLevel(logging.DEBUG)  # Show debug asyncio logs (disabled in init, uncomment for debugging asyncio)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s",
        )

    if not bumper_listen:
        logging.log(logging.FATAL, "No listen address configured")
        return

    if not (
        os.path.exists(ca_cert)
        and os.path.exists(server_cert)
        and os.path.exists(server_key)
    ):
        logging.log(logging.FATAL, "Certificate(s) don't exist at paths specified")
        return

    bumperlog.info("Starting Bumper")
    global mqtt_server
    mqtt_server = MQTTServer((bumper_listen, mqtt_listen_port))
    global mqtt_helperbot
    mqtt_helperbot = MQTTHelperBot((bumper_listen, mqtt_listen_port))
    global conf_server
    conf_server = ConfServer(
        (bumper_listen, conf1_listen_port), usessl=True, helperbot=mqtt_helperbot
    )
    global conf_server_2
    conf_server_2 = ConfServer(
        (bumper_listen, conf2_listen_port), usessl=False, helperbot=mqtt_helperbot
    )    
    global xmpp_server
    xmpp_server = XMPPServer((bumper_listen, xmpp_listen_port))

    # Start web servers
    conf_server.confserver_app()
    asyncio.create_task(conf_server.start_server())

    conf_server_2.confserver_app()
    asyncio.create_task(conf_server_2.start_server())

    # Start MQTT Server
    asyncio.create_task(mqtt_server.broker_coro())

    # Start MQTT Helperbot
    asyncio.create_task(mqtt_helperbot.start_helper_bot())

    # Start XMPP Server
    asyncio.create_task(xmpp_server.start_async_server())

    # Start maintenance
    while not shutting_down:
        asyncio.create_task(maintenance())
        await asyncio.sleep(5)


async def maintenance():
    revoke_expired_tokens()


async def shutdown():
    try:
        bumperlog.info("Shutting down")

        await conf_server.stop_server()
        await conf_server_2.stop_server()
        if mqtt_server.broker.transitions.state == "started":
            await mqtt_server.broker.shutdown()
        elif mqtt_server.broker.transitions.state == "starting":
            while mqtt_server.broker.transitions.state == "starting":
                await asyncio.sleep(0.1)
            if mqtt_server.broker.transitions.state == "started":
                await mqtt_server.broker.shutdown()
                await mqtt_helperbot.Client.disconnect()
        if xmpp_server.server:
            if xmpp_server.server._serving:
                xmpp_server.server.close()
            await xmpp_server.server.wait_closed()
        global shutting_down
        shutting_down = True

    except asyncio.CancelledError:
        bumperlog.info("Coroutine canceled")

    except Exception as e:
        bumperlog.info("Exception: {}".format(e))

    finally:
        bumperlog.info("Shutdown complete")


def get_milli_time(timetoconvert):
    return int(round(timetoconvert * 1000))


def db_file():
    if db:
        return db

    return os_db_path()


def os_db_path():  # createdir=True):
    return os.path.join(data_dir, "bumper.db")


def db_get():
    try:
        # Will create the database if it doesn't exist
        db = TinyDB(db_file())

        # Will create the tables if they don't exist
        db.table("users", cache_size=0)
        db.table("clients", cache_size=0)
        db.table("bots", cache_size=0)
        db.table("tokens", cache_size=0)

        return db

    except json.decoder.JSONDecodeError as jerr:
        bumperlog.error("JsonErr: {} - Doc: {}".format(jerr.msg, jerr.doc))

    except Exception as ex:
        bumperlog.error(ex)


class BumperUser(object):
    def __init__(self, userid=""):
        self.userid = userid
        self.devices = []
        self.bots = []

    def asdict(self):
        return {"userid": self.userid, "devices": self.devices, "bots": self.bots}


def user_add(userid):
    newuser = BumperUser()
    newuser.userid = userid

    user = user_get(userid)
    if not user:
        bumperlog.info("Adding new user with userid: {}".format(newuser.userid))
        user_full_upsert(newuser.asdict())


def user_get(userid):
    users = db_get().table("users")
    User = Query()
    return users.get(User.userid == userid)


def user_by_deviceid(deviceid):
    users = db_get().table("users")
    User = Query()
    return users.get(User.devices.any([deviceid]))


def user_full_upsert(user):
    users = db_get().table("users")
    User = Query()
    users.upsert(user, User.did == user["userid"])


def user_add_device(userid, devid):
    users = db_get().table("users")
    User = Query()
    user = users.get(User.userid == userid)
    userdevices = list(user["devices"])
    if not devid in userdevices:
        userdevices.append(devid)

    users.upsert({"devices": userdevices}, User.userid == userid)


def user_remove_device(userid, devid):
    users = db_get().table("users")
    User = Query()
    user = users.get(User.userid == userid)
    userdevices = list(user["devices"])
    if devid in userdevices:
        userdevices.remove(devid)

    users.upsert({"devices": userdevices}, User.userid == userid)


def user_add_bot(userid, did):
    users = db_get().table("users")
    User = Query()
    user = users.get(User.userid == userid)
    userbots = list(user["bots"])
    if not did in userbots:
        userbots.append(did)

    users.upsert({"bots": userbots}, User.userid == userid)


def user_remove_bot(userid, did):
    users = db_get().table("users")
    User = Query()
    user = users.get(User.userid == userid)
    userbots = list(user["bots"])
    if did in userbots:
        userbots.remove(did)

    users.upsert({"bots": userbots}, User.userid == userid)


def user_get_tokens(userid):
    tokens = db_get().table("tokens")
    return tokens.search((Query().userid == userid))


def user_get_token(userid, token):
    tokens = db_get().table("tokens")
    return tokens.get((Query().userid == userid) & (Query().token == token))


def user_add_token(userid, token):
    tokens = db_get().table("tokens")
    tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
    if not tmptoken:
        bumperlog.debug("Adding token {} for userid {}".format(token, userid))
        tokens.insert(
            {
                "userid": userid,
                "token": token,
                "expiration": "{}".format(
                    datetime.now() + timedelta(seconds=token_validity_seconds)
                ),
            }
        )


def user_revoke_all_tokens(userid):
    tokens = db_get().table("tokens")
    tsearch = tokens.search(Query().userid == userid)
    for i in tsearch:
        tokens.remove(doc_ids=[i.doc_id])


def user_revoke_expired_tokens(userid):
    tokens = db_get().table("tokens")
    tsearch = tokens.search(Query().userid == userid)
    for i in tsearch:
        if datetime.now() >= datetime.fromisoformat(i["expiration"]):
            bumperlog.debug("Removing token {} due to expiration".format(i["token"]))
            tokens.remove(doc_ids=[i.doc_id])


def user_revoke_token(userid, token):
    tokens = db_get().table("tokens")
    tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
    if tmptoken:
        tokens.remove(doc_ids=[tmptoken.doc_id])


def user_add_authcode(userid, token, authcode):
    tokens = db_get().table("tokens")
    tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
    if tmptoken:
        tokens.upsert(
            {"authcode": authcode},
            ((Query().userid == userid) & (Query().token == token)),
        )


def user_revoke_authcode(userid, token, authcode):
    tokens = db_get().table("tokens")
    tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
    if tmptoken:
        tokens.upsert(
            {"authcode": ""}, ((Query().userid == userid) & (Query().token == token))
        )


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


class GlobalVacBotDevice(VacBotDevice):  # EcoVacs Home
    UILogicId = ""
    ota = True
    updateInfo = {"changeLog": "", "needUpdate": False}
    icon = ""
    deviceName = ""


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


def get_disconnected_xmpp_clients():
    clients = db_get().table("clients")
    Client = Query()
    return clients.search(Client.xmpp_connection == False)


def check_authcode(uid, authcode):
    bumperlog.debug("Checking for authcode: {}".format(authcode))
    tokens = db_get().table("tokens")
    tmpauth = tokens.get(
        (Query().authcode == authcode)
        & (  # Match authcode
            (Query().userid == uid.replace("fuid_", ""))
            | (Query().userid == "fuid_{}".format(uid))
        )  # Userid with or without fuid_
    )
    if tmpauth:
        return True

    return False


def loginByItToken(authcode):
    bumperlog.debug("Checking for authcode: {}".format(authcode))
    tokens = db_get().table("tokens")
    tmpauth = tokens.get(
        (Query().authcode == authcode)
        # & (  # Match authcode
        #    (Query().userid == uid.replace("fuid_", ""))
        #    | (Query().userid == "fuid_{}".format(uid))
        # )  # Userid with or without fuid_
    )
    if tmpauth:
        return {"token": tmpauth["token"], "userid": tmpauth["userid"]}

    return {}


def check_token(uid, token):
    bumperlog.debug("Checking for token: {}".format(token))
    tokens = db_get().table("tokens")
    tmpauth = tokens.get(
        (Query().token == token)
        & (  # Match token
            (Query().userid == uid.replace("fuid_", ""))
            | (Query().userid == "fuid_{}".format(uid))
        )  # Userid with or without fuid_
    )
    if tmpauth:
        return True

    return False


def revoke_expired_tokens():
    tokens = db_get().table("tokens").all()
    for i in tokens:
        if datetime.now() >= datetime.fromisoformat(i["expiration"]):
            bumperlog.debug("Removing token {} due to expiration".format(i["token"]))
            db_get().table("tokens").remove(doc_ids=[i.doc_id])


def bot_add(sn, did, devclass, resource, company):
    newbot = VacBotDevice()
    newbot.did = did
    newbot.name = sn
    newbot.vac_bot_device_class = devclass
    newbot.resource = resource
    newbot.company = company

    bot = bot_get(did)
    if not bot:  # Not existing bot in database
        if (
            not devclass == "" or "@" not in sn or "tmp" not in sn
        ):  # try to prevent bad additions to the bot list
            bumperlog.info(
                "Adding new bot with SN: {} DID: {}".format(newbot.name, newbot.did)
            )
            bot_full_upsert(newbot.asdict())


def bot_remove(did):
    bots = db_get().table("bots")
    bot = bot_get(did)
    bots.remove(doc_ids=[bot.doc_id])


def bot_get(did):
    bots = db_get().table("bots")
    Bot = Query()
    return bots.get(Bot.did == did)


def bot_toEcoVacsHome_JSON(bot):  # EcoVacs Home
    for botprod in EcoVacsHomeProducts:
        if botprod["classid"] == bot["class"]:
            bot["UILogicId"] = botprod["product"]["UILogicId"]
            bot["ota"] = botprod["product"]["ota"]
            bot["icon"] = botprod["product"]["iconUrl"]
            return json.dumps(
                bot, default=lambda o: o.__dict__, sort_keys=False
            )  # , indent=4)


def bot_full_upsert(vacbot):
    bots = db_get().table("bots")
    Bot = Query()
    bots.upsert(vacbot, Bot.did == vacbot["did"])


def bot_set_nick(did, nick):
    bots = db_get().table("bots")
    Bot = Query()
    bots.upsert({"nick": nick}, Bot.did == did)


def bot_set_mqtt(did, mqtt):
    bots = db_get().table("bots")
    Bot = Query()
    bots.upsert({"mqtt_connection": mqtt}, Bot.did == did)


def bot_set_xmpp(did, xmpp):
    bots = db_get().table("bots")
    Bot = Query()
    bots.upsert({"xmpp_connection": xmpp}, Bot.did == did)


def client_add(userid, realm, resource):
    newclient = VacBotClient()
    newclient.userid = userid
    newclient.realm = realm
    newclient.resource = resource

    client = client_get(resource)
    if not client:
        bumperlog.info("Adding new client with resource {}".format(newclient.resource))
        client_full_upsert(newclient.asdict())


def client_get(resource):
    clients = db_get().table("clients")
    Client = Query()
    return clients.get(Client.resource == resource)


def client_full_upsert(client):
    clients = db_get().table("clients")
    Client = Query()
    clients.upsert(client, Client.resource == client["resource"])


def client_set_mqtt(resource, mqtt):
    clients = db_get().table("clients")
    Client = Query()
    clients.upsert({"mqtt_connection": mqtt}, Client.resource == resource)


def client_set_xmpp(resource, xmpp):
    clients = db_get().table("clients")
    Client = Query()
    clients.upsert({"xmpp_connection": xmpp}, Client.resource == resource)


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


def create_certs():
    import platform
    import os
    import subprocess
    import sys

    path = os.path.dirname(sys.modules[__name__].__file__)
    path = os.path.join(path, "..")
    sys.path.insert(0, path)

    print("Creating certificates")
    odir = os.path.realpath(os.curdir)
    os.chdir("certs")
    if str(platform.system()).lower() == "windows":
        # run for win
        subprocess.run([os.path.join("..", "create_certs", "create_certs_windows.exe")])
    elif str(platform.system()).lower() == "darwin":
        # run on mac
        subprocess.run([os.path.join("..", "create_certs", "create_certs_osx")])
    elif str(platform.system()).lower() == "linux":
        if "arm" in platform.machine().lower():
            # run for pi
            subprocess.run([os.path.join("..", "create_certs", "create_certs_rpi")])
        else:
            # run for linux
            subprocess.run([os.path.join("..", "create_certs", "create_certs_linux")])

    else:
        os.chdir(odir)
        logging.log(
            logging.FATAL,
            "Can't determine platform. Create certs manually and try again.",
        )
        return

    print("Certificates created")
    os.chdir(odir)
    print(os.path.realpath(os.curdir))
    if "__main__.py" in sys.argv[0]:
        os.execv(
            sys.executable, ["python", "-m", "bumper"] + sys.argv[1:]
        )  # Start again

    else:
        os.execv(sys.executable, ["python"] + sys.argv)  # Start again


def first_run():
    create_certs()

def main(argv=None):
    import argparse

    global bumper_debug
    global bumper_listen
    global bumper_announce_ip
    if not argv:
        argv = sys.argv[1:]  # Set argv to argv[1:] if not passed into main
    try:

        if not (
            os.path.exists(ca_cert)
            and os.path.exists(server_cert)
            and os.path.exists(server_key)
        ):
            first_run()
            return

        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--listen", type=str, default=None, help="start serving on address"
        )
        parser.add_argument(
            "--announce",
            type=str,
            default=None,
            help="announce address to bots on checkin",
        )
        parser.add_argument("--debug", action="store_true", help="enable debug logs")

        args = parser.parse_args(args=argv)

        if args.debug:
            bumper_debug = True

        if args.listen:
            bumper_listen = args.listen

        if args.announce:
            bumper_announce_ip = args.announce

        asyncio.run(start())

    except KeyboardInterrupt:
        bumperlog.info("Keyboard Interrupt!")
        pass

    except Exception as e:
        bumperlog.exception(e)
        pass

    finally:
        asyncio.run(shutdown())

