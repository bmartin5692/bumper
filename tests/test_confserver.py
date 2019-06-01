import mock
import bumper
import asyncio
import pytest
import os
import json
import tinydb
import pytest_aiohttp
from aiohttp import web


def create_confserver():
    return bumper.ConfServer("127.0.0.1:11111", False, mock.MagicMock)


def create_app(loop):
    confserver = bumper.ConfServer("127.0.0.1:11111", False, mock.MagicMock)
    confserver.confserver_app(loop=loop)
    return confserver.app


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


async def test_base(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    resp = await client.get("/")
    assert resp.status == 200
    text = await resp.text()
    assert "Bumper!" in text


async def test_login(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    # Test without user
    resp = await client.get("/1/private/us/en/dev_1234/ios/1/0/0/user/login")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]

    # Add a user to db and test with existing users
    bumper.user_add("testuser")
    resp = await client.get("/1/private/us/en/dev_1234/ios/1/0/0/user/login")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]

    # Add a bot to db that will be added to user
    bumper.bot_add("sn_123", "did_123", "dev_123", "res_123", "com_123")
    resp = await client.get("/1/private/us/en/dev_1234/ios/1/0/0/user/login")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]


async def test_logout(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    # Add a token to user and test
    bumper.user_add("testuser")
    bumper.user_add_device("testuser", "dev_1234")
    bumper.user_add_token("testuser", "token_1234")
    resp = await client.get(
        "/1/private/us/en/dev_1234/ios/1/0/0/user/logout?accessToken={}".format(
            "token_1234"
        )
    )

    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS


async def test_checkLogin(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    # Test without token
    resp = await client.get(
        "/1/private/us/en/dev_1234/ios/1/0/0/user/checkLogin?accessToken={}".format(
            None
        )
    )
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert jsonresp["data"]["accessToken"] != "token_1234"
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]

    # Add a user to db and test with existing users
    bumper.user_add("testuser")
    resp = await client.get(
        "/1/private/us/en/dev_1234/ios/1/0/0/user/checkLogin?accessToken={}".format(
            None
        )
    )
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert jsonresp["data"]["accessToken"] != "token_1234"
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]

    # Remove dev from tmpuser
    bumper.user_remove_device("tmpuser", "dev_1234")

    # Add a token to user and test
    bumper.user_add("testuser")
    bumper.user_add_device("testuser", "dev_1234")
    bumper.user_add_token("testuser", "token_1234")
    resp = await client.get(
        "/1/private/us/en/dev_1234/ios/1/0/0/user/checkLogin?accessToken={}".format(
            "token_1234"
        )
    )
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
    assert "accessToken" in jsonresp["data"]
    assert jsonresp["data"]["accessToken"] == "token_1234"
    assert "uid" in jsonresp["data"]
    assert "username" in jsonresp["data"]


async def test_getAuthCode(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    # Test without user or token
    resp = await client.get(
        "/1/private/us/en/dev_1234/ios/1/0/0/user/getAuthCode?uid={}&accessToken={}".format(
            None, None
        )
    )
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.ERR_TOKEN_INVALID

    # Add a token to user and test
    bumper.user_add("testuser")
    bumper.user_add_device("testuser", "dev_1234")
    bumper.user_add_token("testuser", "token_1234")
    resp = await client.get(
        "/1/private/us/en/dev_1234/ios/1/0/0/user/getAuthCode?uid={}&accessToken={}".format(
            "testuser", "token_1234"
        )
    )
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
    assert "authCode" in jsonresp["data"]
    assert "ecovacsUid" in jsonresp["data"]

    # The above should have added an authcode to token, try again to test with existing authcode
    resp = await client.get(
        "/1/private/us/en/dev_1234/ios/1/0/0/user/getAuthCode?uid={}&accessToken={}".format(
            "testuser", "token_1234"
        )
    )
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
    assert "authCode" in jsonresp["data"]
    assert "ecovacsUid" in jsonresp["data"]


async def test_checkAgreement(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    resp = await client.get("/1/private/us/en/dev_1234/ios/1/0/0/user/checkAgreement")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS


async def test_homePageAlert(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    resp = await client.get(
        "/1/private/us/en/dev_1234/ios/1/0/0/campaign/homePageAlert"
    )
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS


async def test_checkVersion(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    resp = await client.get("/1/private/us/en/dev_1234/ios/1/0/0/common/checkVersion")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS


async def test_getProductIotMap(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    resp = await client.post("/api/pim/product/getProductIotMap")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["code"] == bumper.RETURN_API_SUCCESS


async def test_getUsersAPI(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    resp = await client.get("/api/users/user.do")
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "fail"


async def test_postUsersAPI(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    # Test FindBest
    postbody = {"todo": "FindBest", "service": "EcoMsgNew"}
    resp = await client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test EcoUpdate
    postbody = {"todo": "FindBest", "service": "EcoUpdate"}
    resp = await client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test loginByItToken - Uses the authcode
    bumper.user_add("testuser")
    bumper.user_add_device("testuser", "dev_1234")
    bumper.user_add_token("testuser", "token_1234")
    bumper.user_add_authcode("testuser", "token_1234", "auth_1234")
    bumper.user_add_bot("testuser", "did_1234")
    bumper.bot_add("sn_1234", "did_1234", "class_1234", "res_1234", "com_1234")
    # Test
    postbody = {
        "country": "US",
        "last": "",
        "realm": "ecouser.net",
        "resource": "dev_1234",
        "todo": "loginByItToken",
        "token": "auth_1234",
        "userId": "testuser",
    }
    resp = await client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test GetDeviceList
    postbody = {
        "auth": {
            "realm": "ecouser.net",
            "resource": "dev_1234",
            "token": "token_1234",
            "userid": "testuser",
            "with": "users",
        },
        "todo": "GetDeviceList",
        "userid": "testuser",
    }
    resp = await client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test SetDeviceNick
    postbody = {
        "auth": {
            "realm": "ecouser.net",
            "resource": "dev_1234",
            "token": "token_1234",
            "userid": "testuser",
            "with": "users",
        },
        "todo": "SetDeviceNick",
        "nick": "botnick",
        "did": "did_1234",
    }
    resp = await client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test AddOneDevice - Same as set nick for some bots
    postbody = {
        "auth": {
            "realm": "ecouser.net",
            "resource": "dev_1234",
            "token": "token_1234",
            "userid": "testuser",
            "with": "users",
        },
        "todo": "AddOneDevice",
        "nick": "botnick",
        "did": "did_1234",
    }
    resp = await client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"

    # Test DeleteOneDevice - remove bot
    postbody = {
        "auth": {
            "realm": "ecouser.net",
            "resource": "dev_1234",
            "token": "token_1234",
            "userid": "testuser",
            "with": "users",
        },
        "todo": "DeleteOneDevice",
        "did": "did_1234",
    }
    resp = await client.post("/api/users/user.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    jsonresp = json.loads(text)
    assert jsonresp["result"] == "ok"


async def test_postLookup(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    client = await aiohttp_client(create_app)

    # Test FindBest
    postbody = {"todo": "FindBest", "service": "EcoMsgNew"}
    resp = await client.post("/lookup.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["result"] == "ok"

    # Test EcoUpdate
    postbody = {"todo": "FindBest", "service": "EcoUpdate"}
    resp = await client.post("/lookup.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["result"] == "ok"


async def test_devmgr(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    confserver = create_confserver()
    client = await aiohttp_client(create_app)

    # Test PollSCResult
    postbody = {"td": "PollSCResult"}
    resp = await client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "ok"

    # Test BotCommand
    bumper.bot_add("sn_1234", "did_1234", "dev_1234", "res_1234", "eco-ng")
    bumper.bot_set_mqtt("did_1234", True)
    postbody = {"toId": "did_1234"}

    # Test return get status
    command_getstatus_resp = {
        "id": "resp_1234",
        "resp": "<ctl ret='ok' status='idle'/>",
        "ret": "ok",
    }
    confserver.helperbot.send_command = mock.MagicMock(
        return_value=async_return(command_getstatus_resp)
    )
    resp = await client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "ok"

    # Test return fail timeout
    command_timeout_resp = {"id": "resp_1234", "errno": "timeout", "ret": "fail"}
    confserver.helperbot.send_command = mock.MagicMock(
        return_value=async_return(command_timeout_resp)
    )
    resp = await client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "fail"

    # Set bot not on mqtt
    bumper.bot_set_mqtt("did_1234", False)
    confserver.helperbot.send_command = mock.MagicMock(
        return_value=async_return(command_getstatus_resp)
    )
    resp = await client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "fail"


async def test_dim_devmanager(aiohttp_client):
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    confserver = create_confserver()
    client = await aiohttp_client(create_app)

    # Test PollSCResult
    postbody = {"td": "PollSCResult"}
    resp = await client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "ok"

    # Test HasUnreadMsg
    postbody = {"td": "HasUnreadMsg"}
    resp = await client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "ok"
    assert test_resp["unRead"] == False

    # Test BotCommand
    bumper.bot_add("sn_1234", "did_1234", "dev_1234", "res_1234", "eco-ng")
    bumper.bot_set_mqtt("did_1234", True)
    postbody = {"toId": "did_1234"}

    # Test return get status
    command_getstatus_resp = {
        "id": "resp_1234",
        "resp": "<ctl ret='ok' status='idle'/>",
        "ret": "ok",
    }
    confserver.helperbot.send_command = mock.MagicMock(
        return_value=async_return(command_getstatus_resp)
    )
    resp = await client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "ok"

    # Test return fail timeout
    command_timeout_resp = {"id": "resp_1234", "errno": "timeout", "ret": "fail"}
    confserver.helperbot.send_command = mock.MagicMock(
        return_value=async_return(command_timeout_resp)
    )
    resp = await client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "fail"
    assert test_resp["errno"] == "timeout"

    # Set bot not on mqtt
    bumper.bot_set_mqtt("did_1234", False)
    confserver.helperbot.send_command = mock.MagicMock(
        return_value=async_return(command_getstatus_resp)
    )
    resp = await client.post("/api/dim/devmanager.do", json=postbody)
    assert resp.status == 200
    text = await resp.text()
    test_resp = json.loads(text)
    assert test_resp["ret"] == "fail"

