#!/usr/bin/env python3

import asyncio
import logging
import os
import ssl

import aiohttp_jinja2
import jinja2
from aiohttp import web

from bumper import plugins
from bumper.models import *


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
    def __init__(self, address, usessl=False):
        self.usessl = usessl
        self.address = address
        self.app = None
        self.site = None
        self.runner = None
        self.runners = []
        self.excludelogging = ["base", "remove-bot", "remove-client", "restart-service"]

    def get_milli_time(self, timetoconvert):
        return int(round(timetoconvert * 1000))

    def confserver_app(self):
        self.app = web.Application(loop=asyncio.get_event_loop(), middlewares=[
            self.log_all_requests,
            ])
        aiohttp_jinja2.setup(self.app, loader=jinja2.FileSystemLoader(os.path.join(bumper.bumper_dir,"bumper","web","templates")))

        self.app.add_routes(
            [
                web.get("", self.handle_base, name="base"),
                web.get("/bot/remove/{did}", self.handle_RemoveBot, name='remove-bot'),       
                web.get("/client/remove/{resource}", self.handle_RemoveClient, name='remove-client'),      
                web.get("/restart_{service}", self.handle_RestartService, name='restart-service'),                
                web.post("/lookup.do", self.handle_lookup),
                web.post("/newauth.do", self.handle_newauth),
            ]
        )

        # common api paths
        api_v1 = {"prefix": "/v1/", "app": web.Application()} # for /v1/   
        api_v2 = {"prefix": "/v2/", "app": web.Application()} # for /v2/   
        portal_api = {"prefix": "/api/", "app": web.Application()} # for /api/ 
        upload_api = {"prefix": "/upload/", "app": web.Application()} # for /upload/ 
        
        apis = {
            "api_v1": api_v1,
            "api_v2": api_v2,
            "portal_api": portal_api,
            "upload_api": upload_api,
            
        }
        
        # Load plugins
        for plug in bumper.discovered_plugins:
            if isinstance(bumper.discovered_plugins[plug].plugin, bumper.plugins.ConfServerApp):                
                plugin = bumper.discovered_plugins[plug].plugin                
                if plugin.plugin_type == "sub_api": # app or sub_api
                    if plugin.sub_api in apis:
                        if plugin.routes:
                            logging.debug(f"Adding confserver sub_api ({plugin.name})")
                            apis[plugin.sub_api]["app"].add_routes(plugin.routes)
                
                elif plugin.plugin_type == "app":
                    if plugin.path_prefix and plugin.app:
                        logging.debug(f"Adding confserver plugin ({plugin.name})")
                        self.app.add_subapp(plugin.path_prefix, plugin.app)      
        
        for api in apis:         
            self.app.add_subapp(apis[api]["prefix"], apis[api]["app"])

        #for resource in self.app.router.resources():
        #    print(resource)


 
    async def start_site(self, app, address='localhost', port=8080, usessl=False):
        runner = web.AppRunner(app)
        self.runners.append(runner)
        await runner.setup()
        if usessl:
            ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_ctx.load_cert_chain(bumper.server_cert, bumper.server_key)
            site = web.TCPSite(
                runner,
                host=address,
                port=port,
                ssl_context=ssl_ctx,
            )

        else:
            site = web.TCPSite(
                runner, host=address, port=port
            )

        await site.start()

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

            bots = bumper.db_get().table("bots").all()
            clients = bumper.db_get().table("clients").all()
            helperbot = bumper.mqtt_helperbot.Client.session.transitions.state
            mqttserver = bumper.mqtt_server.broker
            xmppserver = bumper.xmpp_server
            mq_sessions = []
            for sess in mqttserver._sessions:
                tmpsess = []
                tmpsess.append({
                    "username": mqttserver._sessions[sess][0].username,
                    "client_id": mqttserver._sessions[sess][0].client_id,
                    "state": mqttserver._sessions[sess][0].transitions.state,
                })
               
                mq_sessions.append(tmpsess)
            all = {
                "bots": bots,
                "clients": clients,
                "helperbot": [{"state": helperbot}],
                "mqtt_server": [
                    {"state": mqttserver.transitions.state},
                    {
                        "sessions": [
                            {"count": len(mqttserver._sessions)},
                            {"clients": mq_sessions},
                        ]
                    },
                ],
                "xmpp_server": xmppserver
            }            
            resp = aiohttp_jinja2.render_template('home.jinja2', request, context=all)
            #return web.json_response(all)
            return resp

        except Exception as e:
            confserverlog.exception("{}".format(e))

    @web.middleware
    async def log_all_requests(self, request, handler):

        if request._match_info.route.name not in self.excludelogging:
            to_log = {
                "request": {
                    "route_name": f"{request.match_info.route.name}",
                    "method": f"{request.method}",
                    "path": f"{request.path}",
                    "query_string": f"{request.query_string}",
                    "raw_path": f"{request.raw_path}",
                    "raw_headers": f'{",".join(map("{}".format, request.raw_headers))}',
                }
            }
            try:
                postbody = None
                if request.content_length:
                    if request.content_type == "application/x-www-form-urlencoded":
                        postbody = await request.post()

                    elif request.content_type == "application/json":
                        try:
                            postbody = json.loads(await request.text())
                        except Exception as e:
                            confserverlog.error("Request body not json: {} - {}".format(e, e.doc))
                            postbody = e.doc
                    
                    else:
                        postbody = await request.post()

                to_log["request"]["body"] = f"{postbody}"

                response = await handler(request)
                if response is None:
                    confserverlog.warning("Response was null!")
                    confserverlog.warning(json.dumps(to_log))
                    return response

                to_log["response"] = {
                    "status": f"{response.status}",
                }
                if not "application/octet-stream" in response.content_type:
                    to_log["response"]["body"] = f"{json.loads(response.body)}"

                confserverlog.debug(json.dumps(to_log))
                
                return response

            except web.HTTPNotFound as notfound:
                confserverlog.debug("Request path {} not found".format(request.raw_path))
                confserverlog.debug(json.dumps(to_log))
                return notfound

            except Exception as e:
                confserverlog.exception("{}".format(e))
                confserverlog.error(json.dumps(to_log))
                return e 

        else:
            return await handler(request)

    async def restart_Helper(self):

        await bumper.mqtt_helperbot.Client.disconnect()
        asyncio.create_task(bumper.mqtt_helperbot.start_helper_bot())

    async def restart_MQTT(self):
        
        if not (bumper.mqtt_server.broker.transitions.state == "stopped" or bumper.mqtt_server.broker.transitions.state == "not_started"):
            # close session writers - this was required so bots would reconnect properly after restarting
            for sess in list(bumper.mqtt_server.broker._sessions):                
                sessobj = bumper.mqtt_server.broker._sessions[sess][1]
                if sessobj.session.transitions.state == "connected":
                    await sessobj.writer.close()

            #await bumper.mqtt_server.broker.shutdown()
            aloop = asyncio.get_event_loop()
            aloop.call_later(
            0.1, lambda: asyncio.create_task(bumper.mqtt_server.broker.shutdown())
            )  # In .1 seconds shutdown broker

        
        aloop = asyncio.get_event_loop()
        aloop.call_later(
           1.5, lambda: asyncio.create_task(bumper.mqtt_server.broker_coro())
        )  # In 1.5 seconds start broker

    async def restart_XMPP(self):
        bumper.xmpp_server.disconnect()
        await bumper.xmpp_server.start_async_server()

    async def handle_RestartService(self, request):
        try:
            service = request.match_info.get("service", "")
            if service == "Helperbot":
                await self.restart_Helper()
                return web.json_response({"status": "complete"})
            elif service == "MQTTServer":
                asyncio.create_task(self.restart_MQTT())
                aloop = asyncio.get_event_loop()
                aloop.call_later(
                    5, lambda: asyncio.create_task(self.restart_Helper())
                )  # In 5 seconds restart Helperbot
                
                return web.json_response({"status": "complete"})
            elif service == "XMPPServer":
                await self.restart_XMPP()
                return web.json_response({"status": "complete"})
            else:
                return web.json_response({"status": "invalid service"})

        except Exception as e:
            confserverlog.exception("{}".format(e))
            pass

    async def handle_RemoveBot(self, request):
        try:
            did = request.match_info.get("did", "")
            bumper.bot_remove(did)
            if bumper.bot_get(did):
                return web.json_response({"status": "failed to remove bot"})
            else:
                return web.json_response({"status": "successfully removed bot"})

        except Exception as e:
            confserverlog.exception("{}".format(e))
            pass        

    async def handle_RemoveClient(self, request):
        try:           
            resource = request.match_info.get("resource", "")
            bumper.client_remove(resource)
            if bumper.client_get(resource):
               return web.json_response({"status": "failed to remove client"})
            else:
               return web.json_response({"status": "successfully removed client"})

        except Exception as e:
            confserverlog.exception("{}".format(e))
            pass                

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
                            "time": self.get_milli_time(datetime.utcnow().timestamp()),
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

    async def handle_newauth(self, request):
        # Bumper is only returning the submitted token. No reason yet to create another new token
        try:
            if request.content_type == "application/x-www-form-urlencoded":
                postbody = await request.post()
            else:
                postbody = json.loads(await request.text())

            confserverlog.debug(postbody)

            body = {
                "authCode": postbody["itToken"],
                "result": "ok",
                "todo": "result"
            }

            return web.json_response(body)

        except Exception as e:
            confserverlog.exception("{}".format(e))

    async def disconnect(self):
        try:
            confserverlog.info("shutting down")
            await self.app.shutdown()

        except Exception as e:
            confserverlog.exception("{}".format(e))

    class ConfServer_GeneralFunctions:
        def __init__(self):
            pass

        def get_milli_time(self, timetoconvert):
            return int(round(timetoconvert * 1000))      

    class ConfServer_AuthHandler:
        def __init__(self):
            self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time
            pass
        
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


        async def login(self, request):
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
                                    "time": self.get_milli_time(datetime.utcnow().timestamp()),
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


        async def get_AuthCode(self, request):
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
                    if "did" in bot:
                        bumper.user_add_bot(tmpuser["userid"], bot["did"])
                    else:
                        confserverlog.error("No DID for bot: {}".format(bot))

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


        def getUserAccountInfo(self, request):
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

                # Example body
                # {
                # "code": "0000",
                # "data": {
                #     "email": "user@gmail.com",
                #     "hasMobile": "N",
                #     "hasPassword": "Y",
                #     "headIco": "",
                #     "loginName": "user@gmail.com",
                #     "mobile": null,
                #     "mobileAreaNo": null,
                #     "nickname": "",
                #     "obfuscatedMobile": null,
                #     "thirdLoginInfoList": [
                #     {
                #         "accountType": "WeChat",
                #         "hasBind": "N"
                #     }
                #     ],
                #     "uid": "20180719212155_*****",
                #     "userName": "EAY*****"
                # },
                # "msg": "操作成功",
                # "success": true,
                # "time": 1578203898343
                # }

                return web.json_response(body)

            except Exception as e:
                confserverlog.exception("{}".format(e))                           

        async def logout(self, request):
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