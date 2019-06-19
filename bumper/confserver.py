#!/usr/bin/env python3

import json
import logging
import ssl
import string
import random
import bumper
from bumper.models import *
from datetime import datetime, timedelta
import asyncio
from aiohttp import web
import uuid
import xml.etree.ElementTree as ET


class aiohttp_filter(logging.Filter):
    def filter(self, record):
        if (
            record.name == "aiohttp.access" and record.levelno == 20
        ):  # Filters aiohttp.access log to switch it from INFO to DEBUG
            record.levelno = 10
            record.levelname = "DEBUG"

        if (
            record.levelno == 10
            and logging.getLogger("confserver").getEffectiveLevel() == 10
        ):
            return True
        else:
            return False


confserverlog = logging.getLogger("confserver")
logging.getLogger("aiohttp.access").addFilter(
    aiohttp_filter()
)  # Add logging filter above to aiohttp.access


class ConfServer:
    def __init__(self, address, usessl=False, helperbot=None):
        self.helperbot = helperbot
        self.usessl = usessl
        self.address = address
        self.confthread = None
        self.run_async = False
        self.app = None
        self.site = None
        self.runner = None

    def get_milli_time(self, timetoconvert):
        return int(round(timetoconvert * 1000))

    def confserver_app(self):
        self.app = web.Application(loop=asyncio.get_event_loop())

        self.app.add_routes(
            [
                web.get("", self.handle_base),
                web.get(
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/login",
                    self.handle_login,
                ),
                web.get(
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/checkLogin",
                    self.handle_login,
                ),
                web.get(  # EcoVacs Home GetUserAccountInfo
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/getUserAccountInfo",
                    self.handle_getUserAccountInfo,
                ),
                web.get(
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/logout",
                    self.handle_logout,
                ),
                web.get(
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/getAuthCode",
                    self.handle_getAuthCode,
                ),
                web.get(  # EcoVacs Home GetAuthCode
                    "/{apiversion}/{apptype}/auth/getAuthCode", self.handle_getAuthCode
                ),
                web.get(
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/checkAgreement",
                    self.handle_checkAgreement,
                ),
                web.get(  # EcoVacs Home CheckAgreement
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/checkAgreementBatch",
                    self.handle_checkAgreement,
                ),
                web.get(
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/checkVersion",
                    self.handle_checkVersion,
                ),
                web.get(  # EcoVacs Home CheckAPPVersion
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/checkAPPVersion",
                    self.handle_checkAPPVersion,
                ),
                web.get(  # EcoVacs Home Upload Device Info
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/uploadDeviceInfo",
                    self.handle_uploadDeviceInfo,
                ),
                web.get(  # EcoVacs Home GetAdByPositionType
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/ad/getAdByPositionType",
                    self.handle_getAdByPositionType,
                ),
                web.get(  # EcoVacs Home Get Boot Screen
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/ad/getBootScreen",
                    self.handle_getBootScreen,
                ),
                web.get(  # EcoVacs Home message hasUnreadMsg
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/message/hasUnreadMsg",
                    self.handle_hasUnreadMessage,
                ),
                web.post(  # EcoVacs Home neng message hasUnreadMsg
                    "/api/neng/message/hasUnreadMsg", self.handle_neng_hasUnreadMessage
                ),
                web.get(  # EcoVacs Home message getMsgList
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/message/getMsgList",
                    self.handle_getMsgList,
                ),
                web.get(  # EcoVacs Home common getSystemReminder
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getSystemReminder",
                    self.handle_getSystemReminder,
                ),
                web.get(  # EcoVacs Home shop getCnWapShopConfig
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/shop/getCnWapShopConfig",
                    self.handle_getCnWapShopConfig,
                ),
                web.get(
                    "/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/campaign/homePageAlert",
                    self.handle_homePageAlert,
                ),
                web.post("/api/users/user.do", self.handle_usersapi),
                web.get("/api/users/user.do", self.handle_usersapi),
                web.post("/api/appsvr/app.do", self.handle_appsvr_api),  # EcoVacs Home
                web.get("/api/appsvr/app.do", self.handle_appsvr_api),  # EcoVacs Home
                web.post(
                    "/api/pim/product/getProductIotMap", self.handle_getProductIotMap
                ),
                web.post("/api/lg/log.do", self.handle_lg_log),  # EcoVacs Home
                web.post("/api/iot/devmanager.do", self.handle_devmanager_botcommand),
                web.post(
                    "/api/dim/devmanager.do", self.handle_dim_devmanager
                ),  # EcoVacs Home
                web.post("/lookup.do", self.handle_lookup),
            ]
        )
        # Direct register from app:
        # /{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/directRegister

    async def start_server(self):
        try:
            confserverlog.info(
                "Starting ConfServer at {}:{}".format(self.address[0], self.address[1])
            )
            self.runner = web.AppRunner(self.app)
            await self.runner.setup()

            if self.usessl:
                ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_ctx.load_cert_chain(bumper.server_cert, bumper.server_key)
                self.site = web.TCPSite(
                    self.runner,
                    host=self.address[0],
                    port=self.address[1],
                    ssl_context=ssl_ctx,
                )

            else:
                self.site = web.TCPSite(
                    self.runner, host=self.address[0], port=self.address[1]
                )

            await self.site.start()

        except PermissionError as e:
            confserverlog.error(e.strerror)
            asyncio.create_task(bumper.shutdown())

        except asyncio.CancelledError:
            pass

        except Exception as e:
            confserverlog.exception("{}".format(e))
            asyncio.create_task(bumper.shutdown())

    async def stop_server(self):
        try:
            await self.runner.shutdown()

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_base(self, request):
        try:
            # TODO - API Options here for viewing clients, tokens, restarting the server, etc.
            # text = "Bumper!"
            bots = bumper.db_get().table("bots").all()
            clients = bumper.db_get().table("clients").all()
            helperbot = self.helperbot.Client.session.transitions.state
            all = {
                "bots": bots,
                "clients": clients,
                "helperbot": [{"state": helperbot}],
            }

            return web.json_response(all)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_login(self, request):
        try:
            user_devid = request.match_info.get("devid", "")
            countrycode = request.match_info.get("country", "us")
            apptype = request.match_info.get("apptype", "")
            confserverlog.info(
                "client with devid {} attempting login".format(user_devid)
            )
            if bumper.use_auth:
                if (
                    not user_devid == ""
                ):  # Performing basic "auth" using devid, super insecure
                    user = bumper.user_by_deviceid(user_devid)
                    if "checkLogin" in request.path:
                        self.check_token(
                            apptype, countrycode, user, request.query["accessToken"]
                        )
                    else:
                        if "global_" in apptype:  # EcoVacs Home
                            login_details = EcoVacsHome_Login()
                            login_details.ucUid = "fuid_{}".format(user["userid"])
                            login_details.loginName = "fusername_{}".format(
                                user["userid"]
                            )
                            login_details.mobile = None

                        else:
                            login_details = EcoVacs_Login()

                        # Deactivate old tokens and authcodes
                        bumper.user_revoke_expired_tokens(user["userid"])

                        login_details.accessToken = self.generate_token(user)
                        login_details.uid = "fuid_{}".format(user["userid"])
                        login_details.username = "fusername_{}".format(user["userid"])
                        login_details.country = countrycode
                        login_details.email = "null@null.com"

                        body = {
                            "code": API_ERRORS[RETURN_API_SUCCESS],
                            "data": json.loads(login_details.toJSON()),
                            # {
                            #    "accessToken": self.generate_token(tmpuser),  # Generate a token
                            #    "country": countrycode,
                            #    "email": "null@null.com",
                            #    "uid": "fuid_{}".format(tmpuser["userid"]),
                            #    "username": "fusername_{}".format(tmpuser["userid"]),
                            # },
                            "msg": "操作成功",
                            "time": self.self.get_milli_time(
                                datetime.utcnow().timestamp()
                            ),
                        }

                        return web.json_response(body)

                body = {
                    "code": bumper.ERR_USER_NOT_ACTIVATED,
                    "data": None,
                    "msg": "当前密码错误",
                    "time": self.get_milli_time(datetime.utcnow().timestamp()),
                }

                return web.json_response(body)

            else:
                return web.json_response(
                    self._auth_any(user_devid, apptype, countrycode, request)
                )

        except Exception as e:
            confserverlog.exception("{}".format(e))

    def handle_getUserAccountInfo(self, request):
        try:
            user_devid = request.match_info.get("devid", "")
            countrycode = request.match_info.get("country", "us")
            apptype = request.match_info.get("apptype", "")
            user = bumper.user_by_deviceid(user_devid)

            if "global_" in apptype:  # EcoVacs Home
                login_details = EcoVacsHome_Login()
                login_details.ucUid = "fuid_{}".format(user["userid"])
                login_details.loginName = "fusername_{}".format(user["userid"])
                login_details.mobile = None
            else:
                login_details = EcoVacs_Login()

            login_details.uid = "fuid_{}".format(user["userid"])
            login_details.username = "fusername_{}".format(user["userid"])
            login_details.country = countrycode
            login_details.email = "null@null.com"

            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "email": login_details.email,
                    "hasMobile": "N",
                    "hasPassword": "Y",
                    "uid": login_details.uid,
                    "userName": login_details.username,
                    "obfuscatedMobile": None,
                    "mobile": None,
                    "loginName": login_details.loginName,
                },
                "msg": "操作成功",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }
            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    def check_token(self, apptype, countrycode, user, token):
        try:
            if bumper.check_token(user["userid"], token):

                if "global_" in apptype:  # EcoVacs Home
                    login_details = EcoVacsHome_Login()
                    login_details.ucUid = "fuid_{}".format(user["userid"])
                    login_details.loginName = "fusername_{}".format(user["userid"])
                    login_details.mobile = None
                else:
                    login_details = EcoVacs_Login()

                login_details.accessToken = token
                login_details.uid = "fuid_{}".format(user["userid"])
                login_details.username = "fusername_{}".format(user["userid"])
                login_details.country = countrycode
                login_details.email = "null@null.com"

                body = {
                    "code": bumper.RETURN_API_SUCCESS,
                    "data": json.loads(login_details.toJSON()),
                    # {
                    #    "accessToken": self.generate_token(tmpuser),  # Generate a token
                    #    "country": countrycode,
                    #    "email": "null@null.com",
                    #    "uid": "fuid_{}".format(tmpuser["userid"]),
                    #    "username": "fusername_{}".format(tmpuser["userid"]),
                    # },
                    "msg": "操作成功",
                    "time": self.get_milli_time(datetime.utcnow().timestamp()),
                }
                return web.json_response(body)

            else:
                body = {
                    "code": bumper.ERR_TOKEN_INVALID,
                    "data": None,
                    "msg": "当前密码错误",
                    "time": self.get_milli_time(datetime.utcnow().timestamp()),
                }
                return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    def generate_token(self, user):
        try:
            tmpaccesstoken = uuid.uuid4().hex
            bumper.user_add_token(user["userid"], tmpaccesstoken)
            return tmpaccesstoken

        except Exception as e:
            confserverlog.exception("{}".format(e))

    def generate_authcode(self, user, countrycode, token):
        try:
            tmpauthcode = "{}_{}".format(countrycode, uuid.uuid4().hex)
            bumper.user_add_authcode(user["userid"], token, tmpauthcode)
            return tmpauthcode

        except Exception as e:
            confserverlog.exception("{}".format(e))

    def _auth_any(self, devid, apptype, country, request):
        try:
            user_devid = devid
            countrycode = country
            user = bumper.user_by_deviceid(user_devid)
            bots = bumper.db_get().table("bots").all()

            if user:  # Default to user 0
                tmpuser = user
                if "global_" in apptype:  # EcoVacs Home
                    login_details = EcoVacsHome_Login()
                    login_details.ucUid = "fuid_{}".format(tmpuser["userid"])
                    login_details.loginName = "fusername_{}".format(tmpuser["userid"])
                    login_details.mobile = None
                else:
                    login_details = EcoVacs_Login()

                login_details.accessToken = self.generate_token(tmpuser)
                login_details.uid = "fuid_{}".format(tmpuser["userid"])
                login_details.username = "fusername_{}".format(tmpuser["userid"])
                login_details.country = countrycode
                login_details.email = "null@null.com"
                bumper.user_add_device(tmpuser["userid"], user_devid)
            else:
                bumper.user_add("tmpuser")  # Add a new user
                tmpuser = bumper.user_get("tmpuser")
                if "global_" in apptype:  # EcoVacs Home
                    login_details = EcoVacsHome_Login()
                    login_details.ucUid = "fuid_{}".format(tmpuser["userid"])
                    login_details.loginName = "fusername_{}".format(tmpuser["userid"])
                    login_details.mobile = None
                else:
                    login_details = EcoVacs_Login()

                login_details.accessToken = self.generate_token(tmpuser)
                login_details.uid = "fuid_{}".format(tmpuser["userid"])
                login_details.username = "fusername_{}".format(tmpuser["userid"])
                login_details.country = countrycode
                login_details.email = "null@null.com"
                bumper.user_add_device(tmpuser["userid"], user_devid)

            for bot in bots:  # Add all bots to the user
                bumper.user_add_bot(tmpuser["userid"], bot["did"])

            if "checkLogin" in request.path:  # If request was to check a token do so
                checkToken = self.check_token(
                    apptype, countrycode, tmpuser, request.query["accessToken"]
                )
                isGood = json.loads(checkToken.text)
                if isGood["code"] == "0000":
                    return isGood

            # Deactivate old tokens and authcodes
            bumper.user_revoke_expired_tokens(tmpuser["userid"])

            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": json.loads(login_details.toJSON()),
                # {
                #    "accessToken": self.generate_token(tmpuser),  # Generate a token
                #    "country": countrycode,
                #    "email": "null@null.com",
                #    "uid": "fuid_{}".format(tmpuser["userid"]),
                #    "username": "fusername_{}".format(tmpuser["userid"]),
                # },
                "msg": "操作成功",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return body

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_logout(self, request):
        try:
            user_devid = request.match_info.get("devid", "")
            if not user_devid == "":
                user = bumper.user_by_deviceid(user_devid)
                if user:
                    if bumper.check_token(user["userid"], request.query["accessToken"]):
                        # Deactivate old tokens and authcodes
                        bumper.user_revoke_token(
                            user["userid"], request.query["accessToken"]
                        )

            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": None,
                "msg": "操作成功",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_getAuthCode(self, request):
        try:
            apptype = request.match_info.get("apptype", "")
            user_devid = request.match_info.get("devid", "")  # Ecovacs
            if user_devid == "":
                user_devid = request.query["deviceId"]  # Ecovacs Home

            if not user_devid == "":
                user = bumper.user_by_deviceid(user_devid)
                token = ""
                if user:
                    if "accessToken" in request.query:
                        token = bumper.user_get_token(
                            user["userid"], request.query["accessToken"]
                        )
                    if token:
                        authcode = ""
                        if not "authcode" in token:
                            authcode = self.generate_authcode(
                                user,
                                request.match_info.get("country", "us"),
                                request.query["accessToken"],
                            )
                        else:
                            authcode = token["authcode"]
                        if "global" in apptype:
                            body = {
                                "code": bumper.RETURN_API_SUCCESS,
                                "data": {
                                    "authCode": authcode,
                                    "ecovacsUid": request.query["uid"],
                                },
                                "msg": "操作成功",
                                "success": True,
                                "time": self.get_milli_time(
                                    datetime.utcnow().timestamp()
                                ),
                            }
                        else:
                            body = {
                                "code": bumper.RETURN_API_SUCCESS,
                                "data": {
                                    "authCode": authcode,
                                    "ecovacsUid": request.query["uid"],
                                },
                                "msg": "操作成功",
                                "time": self.get_milli_time(
                                    datetime.utcnow().timestamp()
                                ),
                            }
                        return web.json_response(body)

            body = {
                "code": bumper.ERR_TOKEN_INVALID,
                "data": None,
                "msg": "当前密码错误",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_checkVersion(self, request):
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "c": None,
                    "img": None,
                    "r": 0,
                    "t": None,
                    "u": None,
                    "ut": 0,
                    "v": None,
                },
                "msg": "操作成功",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_checkAPPVersion(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "c": None,
                    "downPageUrl": None,
                    "img": None,
                    "nextAlertTime": None,
                    "r": 0,
                    "t": None,
                    "u": None,
                    "ut": 0,
                    "v": None,
                },
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_uploadDeviceInfo(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": None,
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_getAdByPositionType(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": None,
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_getBootScreen(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": None,
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_hasUnreadMessage(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": "N",
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_neng_hasUnreadMessage(self, request):  # EcoVacs Home
        try:
            body = {"code": 0, "data": {"hasUnRead": True}}

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_getMsgList(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {"hasNextPage": 0, "items": []},
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_getCnWapShopConfig(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "myShopShowFlag": "N",
                    "myShopUrl": "",
                    "shopIndexShowFlag": "N",
                    "shopIndexUrl": "",
                },
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_getSystemReminder(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "iosGradeTime": {"iodGradeFlag": "N"},
                    "openNotification": {
                        "openNotificationContent": None,
                        "openNotificationFlag": "N",
                        "openNotificationTitle": None,
                    },
                },
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_checkAgreement(self, request):
        try:
            apptype = request.match_info.get("apptype", "")
            if "global_" in apptype:
                body = {
                    "code": bumper.RETURN_API_SUCCESS,
                    "data": [
                        {
                            "force": "N",
                            "id": "20180804040641_7d746faf18b8cb22a50d145598fe4c90",
                            "type": "USER",
                            "url": "https://bumper.ecovacs.com/content/agreement?id=20180804040641_7d746faf18b8cb22a50d145598fe4c90&language=EN",  # "https://gl-us-wap.ecovacs.com/content/agreement?id=20180804040641_7d746faf18b8cb22a50d145598fe4c90&language=EN
                            "version": "1.01",
                        },
                        {
                            "force": "N",
                            "id": "20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac",
                            "type": "PRIVACY",
                            "url": "https://bumper.ecovacs.com/content/agreement?id=20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac&language=EN",  # "https://gl-us-wap.ecovacs.com/content/agreement?id=20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac&language=EN"
                            "version": "1.01",
                        },
                    ],
                    "msg": "操作成功",
                    "success": True,
                    "time": self.get_milli_time(datetime.utcnow().timestamp()),
                }
            else:
                body = {
                    "code": bumper.RETURN_API_SUCCESS,
                    "data": [],
                    "msg": "操作成功",
                    "time": self.get_milli_time(datetime.utcnow().timestamp()),
                }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_homePageAlert(self, request):
        try:
            nextAlert = self.get_milli_time(
                (datetime.now() + timedelta(hours=12)).timestamp()
            )

            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "clickSchemeUrl": None,
                    "clickWebUrl": None,
                    "hasCampaign": "N",
                    "imageUrl": None,
                    "nextAlertTime": nextAlert,
                    "serverTime": self.get_milli_time(datetime.utcnow().timestamp()),
                },
                "msg": "操作成功",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_getProductIotMap(self, request):
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": [
                    {
                        "classid": "dl8fht",
                        "product": {
                            "_id": "5acb0fa87c295c0001876ecf",
                            "name": "DEEBOT 600 Series",
                            "icon": "5acc32067c295c0001876eea",
                            "UILogicId": "dl8fht",
                            "ota": False,
                            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5acc32067c295c0001876eea",
                        },
                    },
                    {
                        "classid": "02uwxm",
                        "product": {
                            "_id": "5ae1481e7ccd1a0001e1f69e",
                            "name": "DEEBOT OZMO Slim10 Series",
                            "icon": "5b1dddc48bc45700014035a1",
                            "UILogicId": "02uwxm",
                            "ota": False,
                            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b1dddc48bc45700014035a1",
                        },
                    },
                    {
                        "classid": "y79a7u",
                        "product": {
                            "_id": "5b04c0227ccd1a0001e1f6a8",
                            "name": "DEEBOT OZMO 900",
                            "icon": "5b04c0217ccd1a0001e1f6a7",
                            "UILogicId": "y79a7u",
                            "ota": True,
                            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b04c0217ccd1a0001e1f6a7",
                        },
                    },
                    {
                        "classid": "jr3pqa",
                        "product": {
                            "_id": "5b43077b8bc457000140363e",
                            "name": "DEEBOT 711",
                            "icon": "5b5ac4cc8d5a56000111e769",
                            "UILogicId": "jr3pqa",
                            "ota": True,
                            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4cc8d5a56000111e769",
                        },
                    },
                    {
                        "classid": "uv242z",
                        "product": {
                            "_id": "5b5149b4ac0b87000148c128",
                            "name": "DEEBOT 710",
                            "icon": "5b5ac4e45f21100001882bb9",
                            "UILogicId": "uv242z",
                            "ota": True,
                            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4e45f21100001882bb9",
                        },
                    },
                    {
                        "classid": "ls1ok3",
                        "product": {
                            "_id": "5b6561060506b100015c8868",
                            "name": "DEEBOT 900 Series",
                            "icon": "5ba4a2cb6c2f120001c32839",
                            "UILogicId": "ls1ok3",
                            "ota": True,
                            "iconUrl": "https://portal-ww.ecouser.net/api/pim/file/get/5ba4a2cb6c2f120001c32839",
                        },
                    },
                ],
            }
            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

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
                        confserverlog.info(
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
                        confserverlog.info(
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

                confserverlog.debug("POST: {} - Response: {}".format(postbody, body))

                return web.json_response(body)

            except Exception as e:
                confserverlog.exception("{}".format(e))

        # Return fail for GET
        body = {"result": "fail", "todo": "result"}
        return web.json_response(body)

    async def handle_appsvr_api(self, request):
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

                confserverlog.debug("POST: {} - Response: {}".format(postbody, body))

                return web.json_response(body)

            except Exception as e:
                confserverlog.exception("{}".format(e))

        # Return fail for GET
        body = {"result": "fail", "todo": "result"}
        return web.json_response(body)

    async def handle_lookup(self, request):
        try:

            body = {}
            postbody = {}
            if request.content_type == "application/x-www-form-urlencoded":
                postbody = await request.post()

            else:
                postbody = json.loads(await request.text())

            confserverlog.debug(postbody)

            todo = postbody["todo"]
            if todo == "FindBest":
                service = postbody["service"]
                if service == "EcoMsgNew":
                    srvip = bumper.bumper_announce_ip
                    srvport = 5223
                    confserverlog.info(
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
                    confserverlog.info(
                        "Announcing EcoUpdate Server to bot as: {}:{}".format(
                            srvip, srvport
                        )
                    )
                    body = {"result": "ok", "ip": srvip, "port": srvport}

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_lg_log(self, request):  # EcoVacs Home
        try:
            json_body = json.loads(await request.text())

            randomid = "".join(random.sample(string.ascii_letters, 6))
            did = json_body["did"]

            botdetails = bumper.bot_get(did)
            if botdetails:
                if not "cmdName" in json_body:
                    if "td" in json_body:
                        json_body["cmdName"] = json_body["td"]
                        # json_body["td"] = "q"

                if not "toId" in json_body:
                    json_body["toId"] = did

                if not "toType" in json_body:
                    json_body["toType"] = botdetails["class"]

                if not "toRes" in json_body:
                    json_body["toRes"] = botdetails["resource"]

                if not "payloadType" in json_body:
                    json_body["payloadType"] = "x"

                if not "payload" in json_body:
                    json_body["payload"] = ""
                    if json_body["td"] == "GetCleanLogs":
                        json_body["td"] = "q"
                        json_body["payload"] = '<ctl count="30"/>'  # <ctl />"

            if did != "":
                bot = bumper.bot_get(did)
                if bot["company"] == "eco-ng":
                    body = ""
                    retcmd = await self.helperbot.send_command(json_body, randomid)
                    confserverlog.debug("Send Bot - {}".format(json_body))
                    confserverlog.debug("Bot Response - {}".format(body))
                    logs = []
                    logsroot = ET.fromstring(retcmd["resp"])
                    if logsroot.attrib["ret"] == "ok":
                        cleanlogs = logsroot.getchildren()
                        for l in cleanlogs:
                            logs.append(l.attrib)

                        body = {
                            "ret": "ok",
                            # "logs": logs, #TODO: Doesn't parse correctly, new protocol & server side processing
                            "logs": [],
                        }

                    else:
                        body = {"ret": "ok", "logs": []}

                    confserverlog.debug(
                        "POST: {} - Response: {}".format(json_body, body)
                    )

                    return web.json_response(body)
                else:
                    # No response, send error back
                    confserverlog.error(
                        "No bots with DID: {} connected to MQTT".format(
                            json_body["toId"]
                        )
                    )
                    body = {"id": randomid, "errno": bumper.ERR_COMMON, "ret": "fail"}
                    return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_devmanager_botcommand(self, request):
        try:
            json_body = json.loads(await request.text())

            randomid = "".join(random.sample(string.ascii_letters, 6))
            did = ""
            if "toId" in json_body:  # Its a command
                did = json_body["toId"]

            if did != "":
                bot = bumper.bot_get(did)
                if bot["company"] == "eco-ng" and bot["mqtt_connection"] == True:
                    retcmd = await self.helperbot.send_command(json_body, randomid)
                    body = retcmd
                    confserverlog.debug("Send Bot - {}".format(json_body))
                    confserverlog.debug("Bot Response - {}".format(body))
                    return web.json_response(body)
                else:
                    # No response, send error back
                    confserverlog.error(
                        "No bots with DID: {} connected to MQTT".format(
                            json_body["toId"]
                        )
                    )
                    body = {
                        "id": randomid,
                        "errno": 500,
                        "ret": "fail",
                        "debug": "wait for response timed out",
                    }
                    return web.json_response(body)

            else:
                if "td" in json_body:  # Seen when doing initial wifi config
                    if json_body["td"] == "PollSCResult":
                        body = {"ret": "ok"}
                        return web.json_response(body)

                    if json_body["td"] == "HasUnreadMsg":  # EcoVacs Home
                        body = {"ret": "ok", "unRead": False}
                        return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def handle_dim_devmanager(self, request):  # Used in EcoVacs Home App
        try:
            json_body = json.loads(await request.text())

            randomid = "".join(random.sample(string.ascii_letters, 6))
            did = ""
            if "toId" in json_body:  # Its a command
                did = json_body["toId"]

            if did != "":
                bot = bumper.bot_get(did)
                if bot["company"] == "eco-ng" and bot["mqtt_connection"] == True:
                    retcmd = await self.helperbot.send_command(json_body, randomid)
                    body = retcmd
                    confserverlog.debug("Send Bot - {}".format(json_body))
                    confserverlog.debug("Bot Response - {}".format(body))
                    return web.json_response(body)
                else:
                    # No response, send error back
                    confserverlog.error(
                        "No bots with DID: {} connected to MQTT".format(
                            json_body["toId"]
                        )
                    )
                    body = {"id": randomid, "errno": bumper.ERR_COMMON, "ret": "fail"}
                    return web.json_response(body)

            else:
                if "td" in json_body:  # Seen when doing initial wifi config
                    if json_body["td"] == "PollSCResult":
                        body = {"ret": "ok"}
                        return web.json_response(body)

                    if json_body["td"] == "HasUnreadMsg":  # EcoVacs Home
                        body = {"ret": "ok", "unRead": False}
                        return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def disconnect(self):
        try:
            confserverlog.info("shutting down")
            if self.run_async:
                self.confthread.join()
            else:
                await self.app.shutdown()

        except Exception as e:
            confserverlog.exception("{}".format(e))

