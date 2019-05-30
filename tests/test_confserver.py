from nose.tools import *
import mock
import bumper
import asyncio
import os
import json
import tinydb
from aiohttp.test_utils import TestClient, TestServer, loop_context
from aiohttp import request

confserver = bumper.ConfServer("127.0.0.1:11111", False, mock.MagicMock)
confserver.confserver_app()
app = confserver.app


def async_return(result):
    f = asyncio.Future()
    f.set_result(result)
    return f


def test_disconnect():
    async def test_disconnect_async():
        await confserver.disconnect()

    loop = asyncio.get_event_loop()
    # Test
    loop.run_until_complete(test_disconnect_async())


def test_base():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_base():
        resp = await client.get("/")
        assert resp.status == 200
        text = await resp.text()
        assert "Bumper!" in text

    # Test
    loop.run_until_complete(test_handle_base())

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_login():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_login():
        resp = await client.get("/1/private/us/en/dev_1234/ios/1/0/0/user/login")
        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
            assert "accessToken" in jsonresp["data"]
            assert "uid" in jsonresp["data"]
            assert "username" in jsonresp["data"]
        else:
            assert jsonresp

    # Test
    loop.run_until_complete(test_handle_login())

    # Add a user to db and test with existing users
    bumper.user_add("testuser")
    # Test
    loop.run_until_complete(test_handle_login())

    # Add a bot to db that will be added to user
    bumper.bot_add("sn_123", "did_123", "dev_123", "res_123", "com_123")
    # Test
    loop.run_until_complete(test_handle_login())

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_logout():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_logout(token=None):
        resp = await client.get(
            "/1/private/us/en/dev_1234/ios/1/0/0/user/logout?accessToken={}".format(
                token
            )
        )
        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
        else:
            assert jsonresp

    # Add a token to user and test
    bumper.user_add("testuser")
    bumper.user_add_device("testuser", "dev_1234")
    bumper.user_add_token("testuser", "token_1234")
    # Test
    loop.run_until_complete(test_handle_logout(token="token_1234"))

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_checkLogin():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_checkLogin(token=None):
        resp = await client.get(
            "/1/private/us/en/dev_1234/ios/1/0/0/user/checkLogin?accessToken={}".format(
                token
            )
        )
        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
            assert "accessToken" in jsonresp["data"]
            if not token:
                assert jsonresp["data"]["accessToken"] != "token_1234"
            else:
                assert jsonresp["data"]["accessToken"] == "token_1234"

            assert "uid" in jsonresp["data"]
            assert "username" in jsonresp["data"]
        else:
            assert jsonresp

    # Test
    loop.run_until_complete(test_handle_checkLogin())

    # Add a user to db and test with existing users
    bumper.user_add("testuser")
    # Test
    loop.run_until_complete(test_handle_checkLogin())

    # Remove dev from tmpuser
    bumper.user_remove_device("tmpuser", "dev_1234")

    # Add a token to user and test
    bumper.user_add("testuser")
    bumper.user_add_device("testuser", "dev_1234")
    bumper.user_add_token("testuser", "token_1234")
    # Test
    loop.run_until_complete(test_handle_checkLogin(token="token_1234"))

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_getAuthCode():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_getAuthCode(uid=None, token=None):
        resp = await client.get(
            "/1/private/us/en/dev_1234/ios/1/0/0/user/getAuthCode?uid={}&accessToken={}".format(
                uid, token
            )
        )
        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            if token:
                assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
                assert "authCode" in jsonresp["data"]
                assert "ecovacsUid" in jsonresp["data"]
            else:
                assert jsonresp["code"] == bumper.ERR_TOKEN_INVALID
        else:
            assert jsonresp

    # Test without user or token
    loop.run_until_complete(test_handle_getAuthCode())

    # Add a token to user and test
    bumper.user_add("testuser")
    bumper.user_add_device("testuser", "dev_1234")
    bumper.user_add_token("testuser", "token_1234")
    # Test
    loop.run_until_complete(test_handle_getAuthCode(uid="testuser", token="token_1234"))

    # The above should have added an authcode to token, try again to test with existing authcode
    # Test
    loop.run_until_complete(test_handle_getAuthCode(uid="testuser", token="token_1234"))

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_checkAgreement():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_checkAgreement():
        resp = await client.get(
            "/1/private/us/en/dev_1234/ios/1/0/0/user/checkAgreement"
        )
        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
        else:
            assert jsonresp

    # Test
    loop.run_until_complete(test_handle_checkAgreement())

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_homePageAlert():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_homePageAlert():
        resp = await client.get(
            "/1/private/us/en/dev_1234/ios/1/0/0/campaign/homePageAlert"
        )
        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
        else:
            assert jsonresp

    # Test
    loop.run_until_complete(test_handle_homePageAlert())

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_checkVersion():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_checkVersion():
        resp = await client.get(
            "/1/private/us/en/dev_1234/ios/1/0/0/common/checkVersion"
        )
        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
        else:
            assert jsonresp

    # Test
    loop.run_until_complete(test_handle_checkVersion())

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_getProductIotMap():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_getProductIotMap():
        resp = await client.post("/api/pim/product/getProductIotMap")
        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            assert jsonresp["code"] == bumper.RETURN_API_SUCCESS
        else:
            assert jsonresp

    # Test
    loop.run_until_complete(test_handle_getProductIotMap())

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_getUsersAPI():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_getUsersApi():
        resp = await client.get("/api/users/user.do")
        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            assert jsonresp["result"] == "fail"
        else:
            assert jsonresp

    # Test
    loop.run_until_complete(test_handle_getUsersApi())

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_postUsersAPI():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_postUsersApi(postbody=None):
        resp = await client.post("/api/users/user.do", json=postbody)

        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            assert jsonresp["result"] == "ok"
        else:
            assert jsonresp

    # Test FindBest
    postbody = {"todo": "FindBest", "service": "EcoMsgNew"}
    # Test
    loop.run_until_complete(test_handle_postUsersApi(postbody))

    # Test EcoUpdate
    postbody = {"todo": "FindBest", "service": "EcoUpdate"}
    # Test
    loop.run_until_complete(test_handle_postUsersApi(postbody))

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
    loop.run_until_complete(test_handle_postUsersApi(postbody))

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
    loop.run_until_complete(test_handle_postUsersApi(postbody))

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
    loop.run_until_complete(test_handle_postUsersApi(postbody))

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
    loop.run_until_complete(test_handle_postUsersApi(postbody))

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
    loop.run_until_complete(test_handle_postUsersApi(postbody))

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_postLookup():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_lookup(postbody=None):
        resp = await client.post("/lookup.do", json=postbody)

        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            assert jsonresp["result"] == "ok"
        else:
            assert jsonresp

    # Test FindBest
    postbody = {"todo": "FindBest", "service": "EcoMsgNew"}
    # Test
    loop.run_until_complete(test_handle_lookup(postbody))

    # Test EcoUpdate
    postbody = {"todo": "FindBest", "service": "EcoUpdate"}
    # Test
    loop.run_until_complete(test_handle_lookup(postbody))

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done


def test_devmgr():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_devmanager(postbody=None, command=False):
        resp = await client.post("/api/iot/devmanager.do", json=postbody)

        assert resp.status == 200
        text = await resp.text()
        jsonresp = json.loads(text)
        if jsonresp:
            if not command:
                assert jsonresp["ret"] == "ok"
            else:
                if "ret" in jsonresp:
                    if jsonresp["ret"] == "ok":
                        assert jsonresp["resp"]
                    else:
                        assert jsonresp["errno"]
        else:
            assert jsonresp

    # Test PollSCResult
    postbody = {"td": "PollSCResult"}
    # Test
    loop.run_until_complete(test_devmanager(postbody, command=False))

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
    # Test
    loop.run_until_complete(test_devmanager(postbody, command=True))

    # Test return fail timeout
    command_timeout_resp = {"id": "resp_1234", "errno": "timeout", "ret": "fail"}
    confserver.helperbot.send_command = mock.MagicMock(
        return_value=async_return(command_timeout_resp)
    )
    # Test
    loop.run_until_complete(test_devmanager(postbody, command=True))

    # Set bot not on mqtt
    bumper.bot_set_mqtt("did_1234", False)
    confserver.helperbot.send_command = mock.MagicMock(
        return_value=async_return(command_getstatus_resp)
    )
    # Test
    loop.run_until_complete(test_devmanager(postbody, command=True))

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done
