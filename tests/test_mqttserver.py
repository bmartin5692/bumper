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
    mqtt_address = ("127.0.0.1", 8883)
    mqtt_server = bumper.MQTTServer(mqtt_address, password_file="tests/passwd")
    await mqtt_server.broker_coro()

    with LogCapture() as l:

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

        await asyncio.wait_for(mqtt_helperbot.Client.deliver_message(), timeout=0.1)

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
            "iot/p2p/GetWKVer/helperbot/bumper/helperbot/bot_serial/ls1ok3/wC3g/q/iCmuqp/j"
        )
        await mqtt_helperbot.Client.publish(
            msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
        )
        
        await asyncio.wait_for(mqtt_helperbot.Client.deliver_message(), timeout=0.1)

        l.check_present(
            (
                "helperbot",
                "DEBUG",
                "Send Command - Topic: iot/p2p/GetWKVer/helperbot/bumper/helperbot/bot_serial/ls1ok3/wC3g/q/iCmuqp/j - Message: {}",
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
            "iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/helperbot/bumper/helperbot/p/iCmuqp/j"
        )
        await mqtt_helperbot.Client.publish(
            msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
        )

        await asyncio.wait_for(mqtt_helperbot.Client.deliver_message(), timeout=0.1)

        l.check_present(
            (
                "helperbot",
                "DEBUG",
                'Received Response - Topic: iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/helperbot/bumper/helperbot/p/iCmuqp/j - Message: {"ret":"ok","ver":"0.13.5"}',
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
            "iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/TESTBAD/bumper/helperbot/p/iCmuqp/j"
        )
        await mqtt_helperbot.Client.publish(
            msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
        )

        await asyncio.wait_for(mqtt_helperbot.Client.deliver_message(), timeout=0.1)


        l.check_present(
            (
                "helperbot",
                "DEBUG",
                "Received Message - Topic: iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/TESTBAD/bumper/helperbot/p/iCmuqp/j - Message: test",
            )
        )  # Check received message was logged
        l.clear()
        mqtt_helperbot.Client.disconnect()

        # Received error message
        mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address)
        await mqtt_helperbot.start_helper_bot()
        assert (
            mqtt_helperbot.Client._connected_state._value == True
        )  # Check helperbot is connected
        msg_payload = "<ctl ts='1560904925396' td='errors' old='' new='110'/>"
        msg_topic_name = "iot/atr/errors/bot_serial/ls1ok3/wC3g/x"
        await mqtt_helperbot.Client.publish(
            msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
        )
            
        await asyncio.wait_for(mqtt_helperbot.Client.deliver_message(), timeout=0.1)

        l.check_present(
            (
                "boterror",
                "ERROR",
                "Received Error - Topic: iot/atr/errors/bot_serial/ls1ok3/wC3g/x - Message: <ctl ts='1560904925396' td='errors' old='' new='110'/>",
            )
        )  # Check received message was logged
        l.clear()
        mqtt_helperbot.Client.disconnect()

    await mqtt_server.broker.shutdown()


async def test_helperbot_expire_message():
    mqtt_address = ("127.0.0.1", 8883)
    mqtt_server = bumper.MQTTServer(mqtt_address, password_file="tests/passwd")
    await mqtt_server.broker_coro()

    with LogCapture("helperbot") as l:

        # Test broadcast message
        mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address)
        bumper.mqtt_helperbot = mqtt_helperbot
        await mqtt_helperbot.start_helper_bot()
        assert (
            mqtt_helperbot.Client._connected_state._value == True
        )  # Check helperbot is connected

        expire_msg_payload = '{"ret":"ok","ver":"0.13.5"}'
        expire_msg_topic_name = "iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/helperbot/bumper/helperbot/p/testgood/j"
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

        await asyncio.sleep(0.1)
        mqtt_helperbot.expire_msg_seconds = (
            0.1
        )  # Set expire message seconds to 0.1 so we don't wait 10 seconds
        msg_payload = "<ctl ts='1547822804960' td='DustCaseST' st='0'/>"
        msg_topic_name = "iot/atr/DustCaseST/bot_serial/ls1ok3/wC3g/x"
        await mqtt_helperbot.Client.publish(
            msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
        )  # Send another message to force get_msg


        await asyncio.wait_for(mqtt_helperbot.Client.deliver_message(), timeout=0.1)


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
    mqtt_server = bumper.MQTTServer(mqtt_address, password_file="tests/passwd")
    await mqtt_server.broker_coro()

    mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address)
    bumper.mqtt_helperbot = mqtt_helperbot
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
        "iot/p2p/GetWKVer/bot_serial/ls1ok3/wC3g/helperbot/bumper/helperbot/p/testgood/j"
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

    #mqtt_helperbot.Client.disconnect()

    # Test GetLifeSpan (xml command)
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
    msg_payload = "<ctl ret='ok' type='Brush' left='4142' total='18000'/>"
    msg_topic_name = (
        "iot/p2p/GetLifeSpan/bot_serial/ls1ok3/wC3g/helperbot/bumper/helperbot/p/testx/q"
    )
    await mqtt_helperbot.Client.publish(
        msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
    )

    commandresult = await mqtt_helperbot.send_command(cmdjson, "testx")
    assert commandresult == {
        "id": "testx",
        "resp": "<ctl ret='ok' type='Brush' left='4142' total='18000'/>",
        "ret": "ok",
    }

    # Test json payload (OZMO950)
    cmdjson = {
        "toType": "ls1ok3",
        "payloadType": "j",
        "toRes": "wC3g",
        "payload": {
            "header": {
            "pri": 1,
            "ts": "1569380075887",
            "tzm": -240,
            "ver": "0.0.50"
        }
        },
        "td": "q",
        "toId": "bot_serial",
        "cmdName": "getStats",
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
    msg_payload = '{"body":{"code":0,"data":{"area":0,"cid":"111","start":"1569378657","time":6,"type":"auto"},"msg":"ok"},"header":{"fwVer":"1.6.4","hwVer":"0.1.1","pri":1,"ts":"1569380074036","tzm":480,"ver":"0.0.1"}}'
    
    msg_topic_name = (
        "iot/p2p/getStats/bot_serial/ls1ok3/wC3g/helperbot/bumper/helperbot/p/testj/j"
    )
    await mqtt_helperbot.Client.publish(
        msg_topic_name, msg_payload.encode(), hbmqtt.client.QOS_0
    )

    commandresult = await mqtt_helperbot.send_command(cmdjson, "testj")

    assert commandresult == {
        "id": "testj",
        "resp": {'body':{'code':0,'data':{'area':0,'cid':'111','start':'1569378657','time':6,'type':'auto'},'msg':'ok'},'header':{'fwVer':'1.6.4','hwVer':'0.1.1','pri':1,'ts':'1569380074036','tzm':480,'ver':'0.0.1'}},
        "ret": "ok",
    }

    mqtt_helperbot.Client.disconnect()

    await mqtt_server.broker.shutdown()
    


async def test_mqttserver():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db

    bumper.db = "tests/tmp.db"  # Set db location for testing

    mqtt_address = ("127.0.0.1", 8883)

    mqtt_server = bumper.MQTTServer(mqtt_address, password_file="tests/passwd", allow_anonymous=True)
    
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

    # Test file auth client connect
    test_client = bumper.MQTTHelperBot(mqtt_address)
    test_client.client_id = "test-file-auth"
    # await test_client.start_helper_bot()
    test_client.Client = hbmqtt.client.MQTTClient(
        client_id=test_client.client_id, config={"check_hostname": False, "auto_reconnect": False, "reconnect_retries": 1}
    )

    # good user/pass
    await test_client.Client.connect(
        f"mqtts://test-client:abc123!@{test_client.address[0]}:{test_client.address[1]}/",
        cafile=bumper.ca_cert, cleansession=True
    )

    assert (
        test_client.Client._connected_state._value == True
    )  # Check client is connected
    await test_client.Client.disconnect()
    assert (
        test_client.Client._connected_state._value == False
    )  # Check client is disconnected
    
    # bad password
    with LogCapture() as l:
        
        await test_client.Client.connect(
            f"mqtts://test-client:notvalid!@{test_client.address[0]}:{test_client.address[1]}/",
            cafile=bumper.ca_cert, cleansession=True
        )

        l.check_present(
                ("mqttserver", "INFO", "File Authentication Failed - Username: test-client - ClientID: test-file-auth"),
                order_matters=False
            )
    # no username in file    
        await test_client.Client.connect(
            f"mqtts://test-client-noexist:notvalid!@{test_client.address[0]}:{test_client.address[1]}/",
            cafile=bumper.ca_cert, cleansession=True
        )


        l.check_present(
            ("mqttserver", "INFO", 'File Authentication Failed - No Entry for Username: test-client-noexist - ClientID: test-file-auth'),
            order_matters=False
        )
    
    await mqtt_server.broker.shutdown()
    

async def test_nofileauth_mqttserver():
    with LogCapture() as l:
        
        mqtt_address = ("127.0.0.1", 8883)
        mqtt_server = bumper.MQTTServer(mqtt_address, password_file="tests/passwd-notfound")
        await mqtt_server.broker_coro()
        await mqtt_server.broker.shutdown()        

    l.check_present(
        ("hbmqtt.broker.plugins.bumper", "WARNING", 'Password file tests/passwd-notfound not found'),
        order_matters=False
    )
