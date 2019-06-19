#!/usr/bin/env python3

import logging
import asyncio
import os
import hbmqtt
from hbmqtt.broker import Broker
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2
import pkg_resources
import time
import bumper
import json
from datetime import datetime, timedelta
import bumper

helperbotlog = logging.getLogger("helperbot")
boterrorlog = logging.getLogger("boterror")
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
    wait_resp_timeout_seconds = 10
    expire_msg_seconds = 10

    def __init__(self, address):
        self.address = address
        self.client_id = "helper1@bumper/helper1"
        self.command_responses = []
        self.helperthread = None

    async def start_helper_bot(self):

        try:
            self.Client = MQTTClient(
                client_id=self.client_id, config={"check_hostname": False}
            )

            await self.Client.connect(
                "mqtts://{}:{}/".format(self.address[0], self.address[1]),
                cafile=bumper.ca_cert,
            )
            await self.Client.subscribe(
                [
                    ("iot/p2p/+/+/+/+/helper1/bumper/helper1/+/+/+", QOS_0),
                    ("iot/p2p/+", QOS_0),
                    ("iot/atr/+", QOS_0),
                ]
            )

            asyncio.create_task(self.get_msg())

        except ConnectionRefusedError as e:
            helperbotlog.Error(e)
            pass

        except asyncio.CancelledError as e:
            pass

        except hbmqtt.client.ConnectException as e:
            helperbotlog.Error(e)
            pass

        except Exception as e:
            helperbotlog.exception("{}".format(e))

    async def get_msg(self):
        while True:
            message = await self.Client.deliver_message()

            if str(message.topic).split("/")[6] == "helper1":
                # Response to command
                helperbotlog.debug(
                    "Received Response - Topic: {} - Message: {}".format(
                        message.topic, str(message.data.decode("utf-8"))
                    )
                )
                self.command_responses.append(
                    {
                        "time": time.time(),
                        "topic": message.topic,
                        "payload": str(message.data.decode("utf-8")),
                    }
                )
            elif str(message.topic).split("/")[3] == "helper1":
                # Helperbot sending command
                helperbotlog.debug(
                    "Send Command - Topic: {} - Message: {}".format(
                        message.topic, str(message.data.decode("utf-8"))
                    )
                )
            elif str(message.topic).split("/")[1] == "atr":
                # Broadcast message received on atr
                if str(message.topic).split("/")[2] == "errors":
                    boterrorlog.error(
                        "Received Error - Topic: {} - Message: {}".format(
                            message.topic, str(message.data.decode("utf-8"))
                        )
                    )
                else:
                    helperbotlog.debug(
                        "Received Broadcast - Topic: {} - Message: {}".format(
                            message.topic, str(message.data.decode("utf-8"))
                        )
                    )

            else:
                helperbotlog.debug(
                    "Received Message - Topic: {} - Message: {}".format(
                        message.topic, str(message.data.decode("utf-8"))
                    )
                )

            # Cleanup "expired messages" > 60 seconds from time
            for msg in self.command_responses:
                expire_time = (
                    datetime.fromtimestamp(msg["time"])
                    + timedelta(seconds=self.expire_msg_seconds)
                ).timestamp()
                if time.time() > expire_time:
                    helperbotlog.debug(
                        "Pruning Message Due To Expiration - Message Topic: {}".format(
                            msg["topic"]
                        )
                    )
                    self.command_responses.remove(msg)

    async def wait_for_resp(self, requestid):
        try:

            t_end = (
                datetime.now() + timedelta(seconds=self.wait_resp_timeout_seconds)
            ).timestamp()

            while time.time() < t_end:
                await asyncio.sleep(0.1)
                if len(self.command_responses) > 0:
                    for msg in self.command_responses:
                        topic = str(msg["topic"]).split("/")
                        if topic[6] == "helper1" and topic[10] == requestid:
                            # helperbotlog.debug('VacBot MQTT Response: Topic: %s Payload: %s' % (msg['topic'], msg['payload']))
                            if topic[11] == "j":
                                resppayload = json.loads(msg["payload"])
                            else:
                                resppayload = str(msg["payload"])
                            resp = {"id": requestid, "ret": "ok", "resp": resppayload}
                            self.command_responses.remove(msg)
                            return resp

            return {
                "id": requestid,
                "errno": 500,
                "ret": "fail",
                "debug": "wait for response timed out",
            }
        except asyncio.CancelledError as e:
            helperbotlog.debug("wait_for_resp cancelled by asyncio")
            return {
                "id": requestid,
                "errno": 500,
                "ret": "fail",
                "debug": "wait for response timed out",
            }
        except Exception as e:
            helperbotlog.exception("{}".format(e))
            return {
                "id": requestid,
                "errno": 500,
                "ret": "fail",
                "debug": "wait for response timed out",
            }

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
            return {}


class MQTTServer:
    default_config = {}
    broker = None

    async def broker_coro(self):

        mqttserverlog.info(
            "Starting MQTT Server at {}:{}".format(self.address[0], self.address[1])
        )
        self.broker = hbmqtt.broker.Broker(config=self.default_config)

        try:
            await self.broker.start()

        except hbmqtt.broker.BrokerException as e:
            mqttserverlog.exception(e)
            asyncio.create_task(bumper.shutdown())
            pass

        except Exception as e:
            mqttserverlog.exception("{}".format(e))
            asyncio.create_task(bumper.shutdown())

    def __init__(self, address):
        try:
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
            }

        except Exception as e:
            mqttserverlog.exception("{}".format(e))


class BumperMQTTServer_Plugin:
    def __init__(self, context):
        self.context = context
        try:
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
                session = kwargs.get("session", None)
                username = session.username
                password = session.password
                client_id = session.client_id

                didsplit = str(client_id).split("@")
                if not (  # if ecouser or bumper aren't in details it is a bot
                    "ecouser" in didsplit[1] or "bumper" in didsplit[1]
                ):
                    tmpbotdetail = str(didsplit[1]).split("/")
                    bumper.bot_add(
                        username,
                        didsplit[0],
                        tmpbotdetail[0],
                        tmpbotdetail[1],
                        "eco-ng",
                    )

                    mqttserverlog.info(
                        "bot authenticated SN: {} DID: {}".format(username, didsplit[0])
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
                            mqttserverlog.info("client authenticated {}".format(userid))
                            authenticated = True

                        else:
                            authenticated = False

            except Exception as e:
                mqttserverlog.exception(
                    "Session: {} - {}".format((kwargs.get("session", None)), e)
                )
                authenticated = False

        return authenticated

    async def on_broker_client_connected(self, client_id):
        try:
            didsplit = str(client_id).split("@")

            bot = bumper.bot_get(didsplit[0])
            if bot:
                bumper.bot_set_mqtt(bot["did"], True)
                return

            # clientuserid = didsplit[0]
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
                return

            # clientuserid = didsplit[0]
            clientresource = didsplit[1].split("/")[1]
            client = bumper.client_get(clientresource)
            if client:
                bumper.client_set_mqtt(client["resource"], False)
                return

        except Exception as e:
            mqttserverlog.exception("{}".format(e))

