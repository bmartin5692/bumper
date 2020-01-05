#!/usr/bin/env python3
import bumper
from bumper.models import VacBotClient, VacBotDevice, BumperUser, EcoVacsHomeProducts
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from datetime import datetime, timedelta
import os
import json
import logging


def test_db_path():
    bumper.db = None
    assert bumper.db_file() == os.path.join(bumper.data_dir, "bumper.db")


def test_user_db():

    bumper.db = "tests/tmp.db"  # Set db location for testing
    bumper.user_add("testuser")  # Add testuser

    assert (
        bumper.user_get("testuser")["userid"] == "testuser"
    )  # Test that testuser was created and returned

    bumper.user_add_device("testuser", "dev_1234")  # Add device to testuser

    assert (
        bumper.user_by_deviceid("dev_1234")["userid"] == "testuser"
    )  # Test that testuser was found by deviceid

    bumper.user_remove_device("testuser", "dev_1234")  # Remove device from testuser

    assert "dev_1234" not in bumper.user_get("testuser")["devices"]
    # Test that dev_1234 was not found in testuser devices

    bumper.user_add_bot("testuser", "bot_1234")  # Add bot did to testuser

    assert "bot_1234" in bumper.user_get("testuser")["bots"]
    # Test that bot was found in testuser's bot list

    bumper.user_remove_bot("testuser", "bot_1234")  # Remove bot did from testuser

    assert "bot_1234" not in bumper.user_get("testuser")["bots"]
    # Test that bot was not found in testuser's bot list

    bumper.user_add_token("testuser", "token_1234")  # Add token to testuser

    assert bumper.check_token("testuser", "token_1234")
    # Test that token was found for testuser

    assert bumper.user_get_token("testuser", "token_1234")
    # Test that token was returned for testuser

    bumper.user_add_authcode(
        "testuser", "token_1234", "auth_1234"
    )  # Add authcode to token_1234 for testuser
    assert bumper.check_authcode("testuser", "auth_1234")
    # Test that authcode was found for testuser

    bumper.user_revoke_authcode(
        "testuser", "token_1234", "auth_1234"
    )  # Remove authcode from testuser
    assert bumper.check_authcode("testuser", "auth_1234") == False
    # Test that authcode was not found for testuser
    bumper.user_revoke_token("testuser", "token_1234")  # Remove token from testuser
    assert (
        bumper.check_token("testuser", "token_1234") == False
    )  # Test that token was not found for testuser
    bumper.user_add_token("testuser", "token_1234")  # Add token_1234
    bumper.user_add_token("testuser", "token_4321")  # Add token_4321
    assert len(bumper.user_get_tokens("testuser")) == 2  # Test 2 tokens are available
    bumper.user_revoke_all_tokens("testuser")  # Revoke all tokens
    assert len(bumper.user_get_tokens("testuser")) == 0  # Test 0 tokens are available

    db = TinyDB("tests/tmp.db")
    tokens = db.table("tokens")
    tokens.insert(
        {
            "userid": "testuser",
            "token": "token_1234",
            "expiration": "{}".format(datetime.now() + timedelta(seconds=-10)),
        }
    )  # Add expired token
    db.close()
    assert len(bumper.user_get_tokens("testuser")) == 1  # Test 1 tokens are available
    bumper.user_revoke_expired_tokens("testuser")  # Revoke expired tokens
    assert len(bumper.user_get_tokens("testuser")) == 0  # Test 0 tokens are available

    db = TinyDB("tests/tmp.db")
    tokens = db.table("tokens")
    tokens.insert(
        {
            "userid": "testuser",
            "token": "token_1234",
            "expiration": "{}".format(datetime.now() + timedelta(seconds=-10)),
        }
    )  # Add expired token
    db.close()
    assert len(bumper.user_get_tokens("testuser")) == 1  # Test 1 tokens are available
    bumper.revoke_expired_tokens()  # Revoke expired tokens
    assert len(bumper.user_get_tokens("testuser")) == 0  # Test 0 tokens are available


def test_bot_db():
    bumper.db = "tests/tmp.db"  # Set db location for testing
    bumper.bot_add("sn_123", "did_123", "dev_123", "res_123", "co_123")
    assert bumper.bot_get("did_123")  # Test that bot was added to db

    bumper.bot_set_nick("did_123", "nick_123")
    assert (
        bumper.bot_get("did_123")["nick"] == "nick_123"
    )  # Test that nick was added to bot

    bumper.bot_set_mqtt("did_123", True)
    assert bumper.bot_get("did_123")[
        "mqtt_connection"
    ]  # Test that mqtt was set True for bot

    bumper.bot_set_xmpp("did_123", True)
    assert bumper.bot_get("did_123")[
        "xmpp_connection"
    ]  # Test that xmpp was set True for bot

    bumper.bot_remove("did_123")
    assert bumper.bot_get("did_123") == None  # Test that bot is no longer in db


def test_client_db():
    bumper.db = "tests/tmp.db"  # Set db location for testing
    bumper.client_add("user_123", "realm_123", "resource_123")
    assert bumper.client_get("resource_123")  # Test client was added

    bumper.client_set_mqtt("resource_123", True)
    assert bumper.client_get("resource_123")[
        "mqtt_connection"
    ]  # Test that mqtt was set True for client

    bumper.client_set_xmpp("resource_123", False)
    assert (
        bumper.client_get("resource_123")["xmpp_connection"] == False
    )  # Test that xmpp was set False for client
    assert (
        len(bumper.get_disconnected_xmpp_clients()) > 0
    )  # Test len of connected xmpp clients is 1

    bumper.client_remove("resource_123")
    assert bumper.client_get("resource_123") == None
