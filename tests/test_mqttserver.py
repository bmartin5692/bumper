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
import time


async def test_helperbot_message():
    with LogCapture("helperbot") as l:
        mqtt_address = ("127.0.0.1", 8883)
        mqtt_server = bumper.MQTTServer(mqtt_address)
        await mqtt_server.broker_coro()

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
        msg_payload = "test"
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
                "Received Message - Topic: iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/TESTBAD/bumper/helper1/p/iCmuqp/j - Message: test",
            )
        )  # Check received message was logged
        l.clear()
        mqtt_helperbot.Client.disconnect()
        await mqtt_server.broker.shutdown()


async def test_helperbot_expire_message():
    with LogCapture("helperbot") as l:
        mqtt_address = ("127.0.0.1", 8883)
        mqtt_server = bumper.MQTTServer(mqtt_address)
        await mqtt_server.broker_coro()
        # mqtt_address = ("127.0.0.1", 8883)
        # mqtt_server = bumper.MQTTServer(mqtt_address)
        # broker = hbmqtt.broker.Broker(
        #    mqtt_server.default_config, plugin_namespace="hbmqtt.test.plugins"
        # )
        # await broker.start()

        # Test broadcast message
        mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address)
        await mqtt_helperbot.start_helper_bot()
        assert (
            mqtt_helperbot.Client._connected_state._value == True
        )  # Check helperbot is connected

        expire_msg_payload = '{"ret":"ok","ver":"0.13.5"}'
        expire_msg_topic_name = "iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/helper1/bumper/helper1/p/testgood/j"
        currenttime = time.time()
        mqtt_helperbot.command_responses.append(
            {
                "time": currenttime,
                "topic": expire_msg_topic_name,
                "payload": expire_msg_payload,
            }
        )

        assert {
            "time": currenttime,
            "topic": expire_msg_topic_name,
            "payload": expire_msg_payload,
        } in mqtt_helperbot.command_responses  # check message is in command_responses

        await asyncio.sleep(0.2)
        mqtt_helperbot.expire_msg_seconds = (
            0.1
        )  # Set expire message seconds to 0.1 so we don't wait 10 seconds
        msg_payload = "<ctl ts='1547822804960' td='DustCaseST' st='0'/>"
        msg_topic_name = "iot/atr/DustCaseST/bot_serial/ls1ok3/wC3g/x"
        await mqtt_helperbot.Client.publish(
            msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
        )  # Send another message to force get_msg

        try:
            await asyncio.wait_for(mqtt_helperbot.Client.deliver_message(), timeout=0.1)
        except asyncio.TimeoutError:
            pass

        assert {
            "time": currenttime,
            "topic": expire_msg_topic_name,
            "payload": expire_msg_payload,
        } not in mqtt_helperbot.command_responses  # check message was expired and removed from command_responses

        l.check_present(
            (
                "helperbot",
                "DEBUG",
                "Pruning Message Due To Expiration - Message Topic: {}".format(
                    expire_msg_topic_name
                ),
            )
        )  # Check received message was logged
        mqtt_helperbot.Client.disconnect()
        await mqtt_server.broker.shutdown()


async def test_helperbot_sendcommand():
    mqtt_address = ("127.0.0.1", 8883)
    mqtt_server = bumper.MQTTServer(mqtt_address)
    await mqtt_server.broker_coro()
    # mqtt_address = ("127.0.0.1", 8883)
    # mqtt_server = bumper.MQTTServer(mqtt_address)
    # broker = hbmqtt.broker.Broker(
    #    mqtt_server.default_config, plugin_namespace="hbmqtt.test.plugins"
    # )
    # await broker.start()

    mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address)
    await mqtt_helperbot.start_helper_bot()
    assert (
        mqtt_helperbot.Client._connected_state._value == True
    )  # Check helperbot is connected

    cmdjson = {
        "toType": "ls1ok3",
        "payloadType": "j",
        "toRes": "wC3g",
        "payload": {},
        "td": "q",
        "toId": "bot_serial",
        "cmdName": "GetWKVer",
        "auth": {
            "token": "us_52cb21fef8e547f38f4ec9a699a5d77e",
            "resource": "IOSF53D07BA",
            "userid": "fuid_tmpuser",
            "with": "users",
            "realm": "ecouser.net",
        },
    }
    mqtt_helperbot.wait_resp_timeout_seconds = (
        0.1
    )  # Override wait_resp_timeout (so we don't wait 10 seconds for timeout)
    commandresult = await mqtt_helperbot.send_command(cmdjson, "testfail")
    # Don't send a response, ensure timeout
    assert commandresult == {
        "debug": "wait for response timed out",
        "errno": 500,
        "id": "testfail",
        "ret": "fail",
    }  # Check timeout

    mqtt_helperbot.wait_resp_timeout_seconds = (
        0.2
    )  # Override wait_resp_timeout (so we don't wait 10 seconds for timeout)
    # Send response beforehand
    msg_payload = '{"ret":"ok","ver":"0.13.5"}'
    msg_topic_name = (
        "iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/helper1/bumper/helper1/p/testgood/j"
    )
    await mqtt_helperbot.Client.publish(
        msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
    )

    commandresult = await mqtt_helperbot.send_command(cmdjson, "testgood")
    assert commandresult == {
        "id": "testgood",
        "resp": {"ret": "ok", "ver": "0.13.5"},
        "ret": "ok",
    }

    mqtt_helperbot.Client.disconnect()

    cmdjson = {
        "toType": "ls1ok3",
        "payloadType": "x",
        "toRes": "wC3g",
        "payload": '<ctl type="Brush"/>',
        "td": "q",
        "toId": "bot_serial",
        "cmdName": "GetLifeSpan",
        "auth": {
            "token": "us_52cb21fef8e547f38f4ec9a699a5d77e",
            "resource": "IOSF53D07BA",
            "userid": "fuid_tmpuser",
            "with": "users",
            "realm": "ecouser.net",
        },
    }

    mqtt_helperbot.wait_resp_timeout_seconds = (
        0.2
    )  # Override wait_resp_timeout (so we don't wait 10 seconds for timeout)
    # Send response beforehand
    msg_payload = (
        "{'id': 'testx', 'ret': 'ok', 'resp': "
        "<ctl ret='ok' type='Brush' left='4142' total='18000'/>"
        "}"
    )
    msg_topic_name = (
        "iot/p2p/GetLifeSpan/bot_serial/ls1ok3/wC3g/helper1/bumper/helper1/p/testx/q"
    )
    await mqtt_helperbot.Client.publish(
        msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
    )

    commandresult = await mqtt_helperbot.send_command(cmdjson, "testx")
    assert commandresult == {
        "id": "testx",
        "resp": "{'id': 'testx', 'ret': 'ok', 'resp': <ctl ret='ok' type='Brush' left='4142' total='18000'/>}",
        "ret": "ok",
    }

    mqtt_helperbot.Client.disconnect()

    await mqtt_server.broker.shutdown()


async def test_mqttserver():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db

    bumper.db = "tests/tmp.db"  # Set db location for testing

    mqtt_address = ("127.0.0.1", 8883)

    mqtt_server = bumper.MQTTServer(mqtt_address)
    await mqtt_server.broker_coro()

    # Test helperbot connect
    mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address)
    await mqtt_helperbot.start_helper_bot()
    assert (
        mqtt_helperbot.Client._connected_state._value == True
    )  # Check helperbot is connected
    await mqtt_helperbot.Client.disconnect()

    # Test client connect
    bumper.user_add("user_123")  # Add user to db
    bumper.client_add("user_123", "ecouser.net", "resource_123")  # Add client to db
    test_client = bumper.MQTTHelperBot(mqtt_address)
    test_client.client_id = "user_123@ecouser.net/resource_123"
    # await test_client.start_helper_bot()
    test_client.Client = hbmqtt.client.MQTTClient(
        client_id=test_client.client_id, config={"check_hostname": False}
    )

    await test_client.Client.connect(
        "mqtts://{}:{}/".format(test_client.address[0], test_client.address[1]),
        cafile=bumper.ca_cert,
    )
    assert (
        test_client.Client._connected_state._value == True
    )  # Check client is connected
    await test_client.Client.disconnect()
    assert (
        test_client.Client._connected_state._value == False
    )  # Check client is disconnected

    # Test fake_bot connect
    fake_bot = bumper.MQTTHelperBot(mqtt_address)
    fake_bot.client_id = "bot_serial@ls1ok3/wC3g"
    await fake_bot.start_helper_bot()
    assert (
        fake_bot.Client._connected_state._value == True
    )  # Check fake_bot is connected
    await fake_bot.Client.disconnect()

    await asyncio.sleep(0.1)

    await mqtt_server.broker.shutdown()
