import mock
import bumper
import asyncio
import pytest
import os
import json
import tinydb
import pytest_asyncio
import xml.etree.ElementTree as ET
import hbmqtt
import logging
from testfixtures import LogCapture


async def test_helperbot_message():
    with LogCapture("helperbot") as l:
        mqtt_address = ("127.0.0.1", 8883)
        mqtt_server = bumper.MQTTServer(mqtt_address)
        broker = hbmqtt.broker.Broker(
            mqtt_server.default_config, plugin_namespace="hbmqtt.test.plugins"
        )
        await broker.start()

        # Test broadcast message
        mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address)
        await mqtt_helperbot.start_helper_bot()
        assert (
            mqtt_helperbot.Client._connected_state._value == True
        )  # Check helperbot is connected
        msg_payload = "<ctl ts='1547822804960' td='DustCaseST' st='0'/>"
        msg_topic_name = "iot/atr/DustCaseST/bot_serial/ls1ok3/wC3g/x"
        await mqtt_helperbot.Client.publish(
            msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
        )
        try:
            await asyncio.wait_for(mqtt_helperbot.Client.deliver_message(), timeout=0.1)
        except asyncio.TimeoutError:
            pass
        l.check_present(
            (
                "helperbot",
                "DEBUG",
                "Received Broadcast - Topic: iot/atr/DustCaseST/bot_serial/ls1ok3/wC3g/x - Message: <ctl ts='1547822804960' td='DustCaseST' st='0'/>",
            )
        )  # Check broadcast message was logged
        l.clear()
        mqtt_helperbot.Client.disconnect()

        # Send command to bot
        mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address)
        await mqtt_helperbot.start_helper_bot()
        assert (
            mqtt_helperbot.Client._connected_state._value == True
        )  # Check helperbot is connected
        msg_payload = "{}"
        msg_topic_name = (
            "iot/p2p/GetWKVer/helper1/bumper/helper1/bot_serial/ls1ok3/wC3g/q/iCmuqp/j"
        )
        await mqtt_helperbot.Client.publish(
            msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
        )
        try:
            await asyncio.wait_for(mqtt_helperbot.Client.deliver_message(), timeout=0.1)
        except asyncio.TimeoutError:
            pass
        l.check_present(
            (
                "helperbot",
                "DEBUG",
                "Send Command - Topic: iot/p2p/GetWKVer/helper1/bumper/helper1/bot_serial/ls1ok3/wC3g/q/iCmuqp/j - Message: {}",
            )
        )  # Check send command message was logged
        l.clear()
        mqtt_helperbot.Client.disconnect()

        # Received response to command
        mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address)
        await mqtt_helperbot.start_helper_bot()
        assert (
            mqtt_helperbot.Client._connected_state._value == True
        )  # Check helperbot is connected
        msg_payload = '{"ret":"ok","ver":"0.13.5"}'
        msg_topic_name = (
            "iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/helper1/bumper/helper1/p/iCmuqp/j"
        )
        await mqtt_helperbot.Client.publish(
            msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
        )
        try:
            await asyncio.wait_for(mqtt_helperbot.Client.deliver_message(), timeout=0.1)
        except asyncio.TimeoutError:
            pass
        l.check_present(
            (
                "helperbot",
                "DEBUG",
                'Received Response - Topic: iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/helper1/bumper/helper1/p/iCmuqp/j - Message: {"ret":"ok","ver":"0.13.5"}',
            )
        )  # Check received response message was logged
        l.clear()
        mqtt_helperbot.Client.disconnect()

        # Received unknown message
        mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address)
        await mqtt_helperbot.start_helper_bot()
        assert (
            mqtt_helperbot.Client._connected_state._value == True
        )  # Check helperbot is connected
        msg_payload = 'test'
        msg_topic_name = (
            "iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/TESTBAD/bumper/helper1/p/iCmuqp/j"
        )
        await mqtt_helperbot.Client.publish(
            msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
        )
        try:
            await asyncio.wait_for(mqtt_helperbot.Client.deliver_message(), timeout=0.1)
        except asyncio.TimeoutError:
            pass
        l.check_present(
            (
                "helperbot",
                "DEBUG",
                'Received Message - Topic: iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/TESTBAD/bumper/helper1/p/iCmuqp/j - Message: test',
            )
        )  # Check received message was logged
        l.clear()
        mqtt_helperbot.Client.disconnect()
        await broker.shutdown()