#!/usr/bin/env python3

import logging
import asyncio
import os
import hbmqtt
from hbmqtt.broker import Broker
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2
import pkg_resources
import contextvars
import time
from threading import Thread
import ssl
import bumper
import json
from datetime import datetime, timedelta

helperbotlog = logging.getLogger("helperbot")
mqttserverlog = logging.getLogger("mqttserver")

logging.getLogger("transitions").setLevel(logging.CRITICAL + 1)  # Ignore this logger
logging.getLogger("passlib").setLevel(logging.CRITICAL + 1)  # Ignore this logger
logging.getLogger("hbmqtt.broker").setLevel(
    logging.CRITICAL + 1
)  # Ignore this logger #There are some sublogs that could be set if needed (.plugins)
logging.getLogger("hbmqtt.mqtt.protocol").setLevel(
    logging.CRITICAL + 1
)  # Ignore this logger
logging.getLogger("hbmqtt.client").setLevel(logging.CRITICAL + 1)  # Ignore this logger


class MQTTHelperBot:

    Client = MQTTClient()

    def __init__(
        self,
        address,
        bumper_bots=contextvars.ContextVar,
        bumper_clients=contextvars.ContextVar,
    ):
        self.address = address
        self.client_id = "helper1@bumper/helper1"
        self.command_responses = contextvars.ContextVar("command_responses", default=[])
        self.helperthread = None

    def run(self, run_async=False):
        if run_async:
            hloop = asyncio.new_event_loop()
            helperbotlog.debug("Starting MQTT HelperBot Thread: 1")
            self.helperthread = Thread(
                name="MQTTHelperBot_Thread", target=self.run_helperbot, args=(hloop,)
            )
            self.helperthread.setDaemon(True)
            self.helperthread.start()

        else:
            self.run_helperbot()

    def run_helperbot(self, loop):
        logging.info("Starting MQTT HelperBot")
        print("Starting MQTT HelperBot")
        try:
            asyncio.set_event_loop(loop)
            self.Client = MQTTClient(
                client_id=self.client_id, config={"check_hostname": False}
            )
            loop.run_until_complete(self.start_helper_bot())
            loop.run_until_complete(self.get_msg())
            loop.run_forever()
        except Exception as e:
            helperbotlog.exception("{}".format(e))

    async def start_helper_bot(self):

        try:
            await self.Client.connect(
                "mqtts://{}:{}/".format(self.address[0], self.address[1]),
                cafile=bumper.ca_cert,
            )
            await self.Client.subscribe(
                [
                    ("iot/p2p/+/+/+/+/helper1/bumper/helper1/+/+/+", QOS_0),
                    ("iot/p2p/+", QOS_0),
                ]
            )

        except Exception as e:
            helperbotlog.exception("{}".format(e))

    async def get_msg(self):
        try:
            while True:
                message = await self.Client.deliver_message()

                # helperbotlog.debug("HelperBot MQTT Received Message on Topic: {} - Message: {}".format(message.topic, str(message.payload.decode("utf-8"))))
                cresp = self.command_responses.get()

                if str(message.topic).split("/")[6] == "helper1":
                    cresp.append(
                        {
                            "time": time.time(),
                            "topic": message.topic,
                            "payload": str(message.data.decode("utf-8")),
                        }
                    )

                # Cleanup "expired messages" > 60 seconds from time
                for msg in cresp:
                    expire_time = (
                        datetime.fromtimestamp(msg["time"]) + timedelta(seconds=10)
                    ).timestamp()
                    if time.time() > expire_time:
                        # helperbotlog.debug("Pruning Message Time: {}, MsgTime: {}, MsgTime+60: {}".format(time.time(), msg['time'], expire_time))
                        cresp.remove(msg)

                self.command_responses.set(cresp)
                # helperbotlog.debug("MQTT Command Response List Count: %s" %len(cresp))

        except Exception as e:
            helperbotlog.exception("{}".format(e))

    async def wait_for_resp(self, requestid):
        try:

            t_end = (datetime.now() + timedelta(seconds=10)).timestamp()

            while time.time() < t_end:
                await asyncio.sleep(0.1)
                responses = self.command_responses.get()
                if len(responses) > 0:
                    for msg in responses:
                        topic = str(msg["topic"]).split("/")
                        if topic[6] == "helper1" and topic[10] == requestid:
                            # helperbotlog.debug('VacBot MQTT Response: Topic: %s Payload: %s' % (msg['topic'], msg['payload']))
                            if topic[11] == "j":
                                resppayload = json.loads(msg["payload"])
                            else:
                                resppayload = str(msg["payload"])
                            resp = {"id": requestid, "ret": "ok", "resp": resppayload}
                            cresp = self.command_responses.get()
                            cresp.remove(msg)
                            self.command_responses.set(cresp)
                            return resp

            return {"id": requestid, "errno": "timeout", "ret": "fail"}
        except asyncio.CancelledError as e:
            helperbotlog.debug("wait_for_resp cancelled by asyncio")
        except Exception as e:
            helperbotlog.exception("{}".format(e))

    async def send_command(self, cmdjson, requestid):
        try:
            ttopic = "iot/p2p/{}/helper1/bumper/helper1/{}/{}/{}/q/{}/{}".format(
                cmdjson["cmdName"],
                cmdjson["toId"],
                cmdjson["toType"],
                cmdjson["toRes"],
                requestid,
                cmdjson["payloadType"],
            )
            try:
                await self.Client.publish(
                    ttopic, str(cmdjson["payload"]).encode(), QOS_0
                )
            except Exception as e:
                helperbotlog.exception("{}".format(e))

            resp = await self.wait_for_resp(requestid)

            return resp

        except Exception as e:
            helperbotlog.exception("{}".format(e))


class MQTTServer:
    default_config = {}
    bumper_users = []
    bumper_clients = []
    bumper_bots = []

    async def broker_coro(self):
        try:
            broker = hbmqtt.broker.Broker(config=self.default_config)
            await broker.start()

        except PermissionError as e:
            if "bind" in e.strerror:
                mqttserverlog.exception(
                    "Error binding mqttserver, exiting. Try using a different hostname or IP - {}".format(
                        e
                    )
                )
            exit(1)

        except Exception as e:
            mqttserverlog.exception("{}".format(e))
            exit(1)

    async def active_bot_listing(self):
        try:
            while True:
                await asyncio.sleep(5)
                mqttserverlog.debug("connected bots - %s" % self.bumper_bots.get())

        except Exception as e:
            mqttserverlog.exception("{}".format(e))

    def __init__(
        self,
        address,
        bumper_users=contextvars.ContextVar,
        bumper_bots=contextvars.ContextVar,
        bumper_clients=contextvars.ContextVar,
    ):
        try:
            self.bumper_users = bumper_users
            self.bumper_bots = bumper_bots
            self.bumper_clients = bumper_clients
            self.mqttserverthread = None
            self.address = address

            # The below adds a plugin to the hbmqtt.broker.plugins without having to futz with setup.py
            distribution = pkg_resources.Distribution("hbmqtt.broker.plugins")
            bumper_plugin = pkg_resources.EntryPoint.parse(
                "bumper = bumper.mqttserver:BumperMQTTServer_Plugin", dist=distribution
            )
            distribution._ep_map = {"hbmqtt.broker.plugins": {"bumper": bumper_plugin}}
            pkg_resources.working_set.add(distribution)

            # Initialize bot server
            self.default_config = {
                "listeners": {
                    "default": {"type": "tcp"},
                    "tls1": {
                        "bind": "{}:{}".format(address[0], address[1]),
                        "ssl": "on",
                        "certfile": bumper.server_cert,
                        "keyfile": bumper.server_key,
                    },
                },
                "sys_interval": 10,
                "auth": {
                    "allow-anonymous": False,
                    "password-file": os.path.join(
                        os.path.dirname(os.path.realpath(__file__)), "passwd"
                    ),
                    "plugins": ["bumper"],  # No plugins == no auth
                },
                "topic-check": {"enabled": False},
                "bumper": {
                    "bumper_users": self.bumper_users,
                    "bumper_bots": self.bumper_bots,
                    "bumper_clients": self.bumper_clients,
                },
            }

        except Exception as e:
            mqttserverlog.exception("{}".format(e))

    def run(self, run_async=False):
        if run_async:
            sloop = asyncio.new_event_loop()
            mqttserverlog.debug("Starting MQTTServer Thread: 1")
            self.mqttserverthread = Thread(
                name="MQTTServer_Thread", target=self.run_server, args=(sloop,)
            )
            self.mqttserverthread.setDaemon(True)
            self.mqttserverthread.start()

        else:
            self.run_server()

    def run_server(self, loop):

        logging.info("Starting MQTT Server at {}".format(self.address))
        print("Starting MQTT Server at {}".format(self.address))
        try:
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.broker_coro())
            # loop.run_until_complete(self.active_bot_listing())
            loop.run_forever()

        except Exception as e:
            mqttserverlog.exception("{}".format(e))


class BumperMQTTServer_Plugin:
    def __init__(self, context):
        self.context = context
        try:
            self.bumper_config = self.context.config["bumper"]
            self.auth_config = self.context.config["auth"]

        except KeyError:
            self.context.logger.warning(
                "'bumper' section not found in context configuration"
            )
        except Exception as e:
            mqttserverlog.exception("{}".format(e))

    async def authenticate(self, *args, **kwargs):
        if not self.auth_config:
            # auth config section not found
            self.context.logger.warning(
                "'auth' section not found in context configuration"
            )
            return False

        allow_anonymous = self.auth_config.get(
            "allow-anonymous", True
        )  # allow anonymous by default
        if allow_anonymous:
            authenticated = True
            self.context.logger.debug("Authentication success: config allows anonymous")
        else:
            try:
                bumper_users = self.bumper_config["bumper_users"].get()
                bumper_bots = self.bumper_config["bumper_bots"].get()
                bumper_clients = self.bumper_config["bumper_clients"].get()
                session = kwargs.get("session", None)
                username = session.username
                password = session.password
                client_id = session.client_id

                didsplit = str(client_id).split("@")
                # If this isn't a fake user (fuid) then add as a bot
                if not (
                    str(didsplit[0]).startswith("fuid")
                    or str(didsplit[0]).startswith("helper")
                ):
                    tmpbotdetail = str(didsplit[1]).split("/")
                    bumper.bot_add(
                        username,
                        didsplit[0],
                        tmpbotdetail[0],
                        tmpbotdetail[1],
                        "eco-ng",
                    )
                    
                    mqttserverlog.debug(
                        "new bot authenticated SN: {} DID: {}".format(
                            username, didsplit[0]
                        )
                    )
                    authenticated = True

                else:
                    tmpclientdetail = str(didsplit[1]).split("/")
                    userid = didsplit[0]
                    realm = tmpclientdetail[0]
                    resource = tmpclientdetail[1]

                    if userid == "helper1":
                        authenticated = True
                    else:
                        auth = False
                        if bumper.check_authcode(didsplit[0], password):
                            auth = True
                        elif bumper.use_auth == False:
                            auth = True

                        if auth:
                            bumper.client_add(userid, realm, resource)
                            mqttserverlog.debug(
                                "client authenticated {}".format(userid)
                            )
                            authenticated = True

                        else:
                            authenticated = False

            except Exception as e:
                mqttserverlog.exception("Session: {} - {}".format((kwargs.get("session", None)),e))
                authenticated = False

        return authenticated

    async def on_broker_client_connected(self, client_id):
        try:
            didsplit = str(client_id).split("@")

            bot = bumper.bot_get(didsplit[0])
            if bot:
                bumper.bot_set_mqtt(bot["did"], True)
                return

            clientuserid = didsplit[0]
            clientresource = didsplit[1].split("/")[1]
            client = bumper.client_get(clientresource)
            if client:
                bumper.client_set_mqtt(client["resource"], True)
                return

        except Exception as e:
            mqttserverlog.exception("{}".format(e))

    async def on_broker_client_disconnected(self, client_id):
        try:
            didsplit = str(client_id).split("@")

            bot = bumper.bot_get(didsplit[0])
            if bot:
                bumper.bot_set_mqtt(bot["did"], False)

            clientuserid = didsplit[0]
            clientresource = didsplit[1].split("/")[1]
            client = bumper.client_get(clientresource)
            if client:
                bumper.client_set_mqtt(client["resource"], False)

        except Exception as e:
            mqttserverlog.exception("{}".format(e))

