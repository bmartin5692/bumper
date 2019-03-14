from nose.tools import *
import mock
import bumper
import asyncio
import os
import json
import tinydb
from aiohttp.test_utils import TestClient, TestServer, loop_context
from aiohttp import request

confserver = bumper.ConfServer("127.0.0.1:11111", False, None)
confserver.confserver_app()
app = confserver.app


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

    loop.run_until_complete(test_handle_base())  # Test handle_base

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
        loginresp = json.loads(text)
        if loginresp:
            assert loginresp["code"] == "0000"
            assert "accessToken" in loginresp["data"]
            assert "uid" in loginresp["data"]
            assert "username" in loginresp["data"]
        else:
            assert loginresp

    loop.run_until_complete(test_handle_login())  # Test handle_login

    #Add a user to db and test with existing users
    bumper.user_add("testuser")
    loop.run_until_complete(test_handle_login())  # Test handle_login with user in db

    #Add a bot to db that will be added to user
    bumper.bot_add("sn_123", "did_123", "dev_123", "res_123", "com_123")
    loop.run_until_complete(test_handle_login())  # Test handle_login with user in db

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done

def test_check_login():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db
    bumper.db = "tests/tmp.db"  # Set db location for testing
    loop = asyncio.get_event_loop()
    client = TestClient(TestServer(app), loop=loop)
    loop.run_until_complete(client.start_server())
    root = "http://{}".format(confserver.address)

    async def test_handle_checkLogin_nouser():
        resp = await client.get("/1/private/us/en/dev_1234/ios/1/0/0/user/checkLogin?accessToken=token_1234")
        assert resp.status == 200
        text = await resp.text()
        loginresp = json.loads(text)
        if loginresp:
            assert loginresp["code"] == "0000"
            assert "accessToken" in loginresp["data"]
            assert loginresp["data"]["accessToken"] != "token_1234"
            assert "uid" in loginresp["data"]
            assert "username" in loginresp["data"]
        else:
            assert loginresp

    async def test_handle_checkLogin_withuser():
        resp = await client.get("/1/private/us/en/dev_1234/ios/1/0/0/user/checkLogin?accessToken=token_1234")
        assert resp.status == 200
        text = await resp.text()
        loginresp = json.loads(text)
        if loginresp:
            assert loginresp["code"] == "0000"
            assert "accessToken" in loginresp["data"]
            assert loginresp["data"]["accessToken"] == "token_1234"
            assert "uid" in loginresp["data"]
            assert "username" in loginresp["data"]
        else:
            assert loginresp            

    loop.run_until_complete(test_handle_checkLogin_nouser())  # Test handle_login no user

    #Add a user to db and test with existing users
    bumper.user_add("testuser")
    loop.run_until_complete(test_handle_checkLogin_nouser())  # Test handle_login with user in db

    #Remove dev from tmpuser
    bumper.user_remove_device("tmpuser","dev_1234")

    #Add a token to user and test
    bumper.user_add("testuser")
    bumper.user_add_device("testuser","dev_1234")
    bumper.user_add_token("testuser", "token_1234")
    loop.run_until_complete(test_handle_checkLogin_withuser())  # Test handle_login with user in db

    loop.run_until_complete(
        client.close()
    )  # Close test server after all tests are done
