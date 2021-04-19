#!/usr/bin/env python3
import json
import logging
import os
from datetime import datetime, timedelta

from tinydb import TinyDB, Query

import bumper
from bumper.models import VacBotClient, VacBotDevice, BumperUser, EcoVacsHomeProducts, OAuth

bumperlog = logging.getLogger("bumper")


def db_file():
    if bumper.db:
        return bumper.db

    return os_db_path()


def os_db_path():  # createdir=True):
    return os.path.join(bumper.data_dir, "bumper.db")


def db_get():
    # Will create the database if it doesn't exist
    db = TinyDB(db_file())

    # Will create the tables if they don't exist
    db.table("users", cache_size=0)
    db.table("clients", cache_size=0)
    db.table("bots", cache_size=0)
    db.table("tokens", cache_size=0)
    db.table("oauth", cache_size=0)

    return db


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
    opendb = db_get()
    with opendb:
        users = opendb.table("users")
        User = Query()
        users.upsert(user, User.did == user["userid"])


def user_add_device(userid, devid):
    opendb = db_get()
    with opendb:
        users = opendb.table("users")
        User = Query()
        user = users.get(User.userid == userid)
        userdevices = list(user["devices"])
        if not devid in userdevices:
            userdevices.append(devid)

        users.upsert({"devices": userdevices}, User.userid == userid)


def user_remove_device(userid, devid):
    opendb = db_get()
    with opendb:
        users = opendb.table("users")
        User = Query()
        user = users.get(User.userid == userid)
        userdevices = list(user["devices"])
        if devid in userdevices:
            userdevices.remove(devid)

        users.upsert({"devices": userdevices}, User.userid == userid)


def user_add_bot(userid, did):
    opendb = db_get()
    with opendb:
        users = opendb.table("users")
        User = Query()
        user = users.get(User.userid == userid)
        userbots = list(user["bots"])
        if not did in userbots:
            userbots.append(did)

        users.upsert({"bots": userbots}, User.userid == userid)


def user_remove_bot(userid, did):
    opendb = db_get()
    with opendb:
        users = opendb.table("users")
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
    opendb = db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
        if not tmptoken:
            bumperlog.debug("Adding token {} for userid {}".format(token, userid))
            tokens.insert(
                {
                    "userid": userid,
                    "token": token,
                    "expiration": "{}".format(
                        datetime.now()
                        + timedelta(seconds=bumper.token_validity_seconds)
                    ),
                }
            )


def user_revoke_all_tokens(userid):
    opendb = db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tsearch = tokens.search(Query().userid == userid)
        for i in tsearch:
            tokens.remove(doc_ids=[i.doc_id])


def user_revoke_expired_tokens(userid):
    opendb = db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tsearch = tokens.search(Query().userid == userid)
        for i in tsearch:
            if datetime.now() >= datetime.fromisoformat(i["expiration"]):
                bumperlog.debug(
                    "Removing token {} due to expiration".format(i["token"])
                )
                tokens.remove(doc_ids=[i.doc_id])


def user_revoke_token(userid, token):
    opendb = db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
        if tmptoken:
            tokens.remove(doc_ids=[tmptoken.doc_id])


def user_add_authcode(userid, token, authcode):
    opendb = db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
        if tmptoken:
            tokens.upsert(
                {"authcode": authcode},
                ((Query().userid == userid) & (Query().token == token)),
            )


def user_revoke_authcode(userid, token, authcode):
    opendb = db_get()
    with opendb:
        tokens = opendb.table("tokens")
        tmptoken = tokens.get((Query().userid == userid) & (Query().token == token))
        if tmptoken:
            tokens.upsert(
                {"authcode": ""},
                ((Query().userid == userid) & (Query().token == token)),
            )


def revoke_expired_oauths():
    opendb = db_get()
    with opendb:
        table = opendb.table("oauth")
        entries = table.all()

        for i in entries:
            oauth = OAuth(**i)
            if datetime.now() >= datetime.fromisoformat(oauth.expire_at):
                bumperlog.debug(
                    "Removing oauth {} due to expiration".format(oauth.access_token)
                )
                table.remove(doc_ids=[i.doc_id])


def user_revoke_expired_oauths(userid):
    opendb = db_get()
    with opendb:
        table = opendb.table("oauth")
        search = table.search(Query().userid == userid)
        for i in search:
            oauth = OAuth(**i)
            if datetime.now() >= datetime.fromisoformat(oauth.expire_at):
                bumperlog.debug(
                    "Removing oauth {} due to expiration".format(oauth.access_token)
                )
                table.remove(doc_ids=[i.doc_id])


def user_add_oauth(userid) -> OAuth:
    user_revoke_expired_oauths(userid)
    opendb = db_get()
    with opendb:
        table = opendb.table("oauth")
        entry = table.get(Query().userid == userid)
        if entry:
            return OAuth(**entry)
        else:
            oauth = OAuth.create_new(userid)
            bumperlog.debug("Adding oauth {} for userid {}".format(oauth.access_token, userid))
            table.insert(oauth.toDB())
            return oauth


def token_by_authcode(authcode):
    tokens = db_get().table("tokens")
    return tokens.get(Query().authcode == authcode)


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
    if bot:
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
            bot["model"] = botprod["product"]["model"]
            bot["pip"] = botprod["product"]["_id"]
            bot["deviceName"] = botprod["product"]["name"]
            bot["materialNo"] = botprod["product"]["materialNo"]
            bot["product_category"] = "DEEBOT" if botprod["product"]["name"].startswith("DEEBOT") else "UNKNOWN"
            # bot["updateInfo"] = {
            #     "changeLog": "",
            #     "needUpdate": False
            # }
            # bot["service"] = {
            #     "jmq": "jmq-ngiot-eu.dc.ww.ecouser.net",
            #     "mqs": "api-ngiot.dc-as.ww.ecouser.net"
            # }
            bot["status"] = 1 if bot["mqtt_connection"] or bot["xmpp_connection"] else 0

            return json.dumps(
                bot, default=lambda o: o.__dict__, sort_keys=False
            )  # , indent=4)


def bot_full_upsert(vacbot):
    bots = db_get().table("bots")
    Bot = Query()
    if "did" in vacbot:
        bots.upsert(vacbot, Bot.did == vacbot["did"])
    else:
        bumperlog.error("No DID in vacbot: {}".format(vacbot))


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


def client_remove(resource):
    clients = db_get().table("clients")
    client = client_get(resource)
    if client:
        clients.remove(doc_ids=[client.doc_id])


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
