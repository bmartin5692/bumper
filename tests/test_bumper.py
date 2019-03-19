from nose.tools import *
import nose
import mock
from tinydb.storages import MemoryStorage
from tinydb import TinyDB, Query
import bumper
import os
import datetime, time
import platform


def test_get_milli_time():
    assert_equals(
        bumper.get_milli_time(
            datetime.datetime(
                2018, 1, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            ).timestamp()
        ),
        1514768400000,
    )


def test_user_db():
    if os.path.exists("tests/tmp.db"):
        os.remove("tests/tmp.db")  # Remove existing db

    # Test os_db_path
    platform.system = mock.MagicMock(return_value="Windows")
    p = platform.system()
    os.getenv = mock.MagicMock(return_value="C:\AppData")
    o = os.getenv("APPDATA")
    assert_equals(bumper.os_db_path(), os.path.join(os.getenv("APPDATA"), "bumper.db"))

    platform.system = mock.MagicMock(return_value="Linux")
    assert_equals(bumper.os_db_path(), os.path.expanduser("~/.config/bumper.db"))

    bumper.db = "tests/tmp.db"  # Set db location for testing
    bumper.user_add("testuser")  # Add testuser

    assert_equals(
        bumper.user_get("testuser")["userid"], "testuser"
    )  # Test that testuser was created and returned

    bumper.user_add_device("testuser", "dev_1234")  # Add device to testuser

    assert_equals(
        bumper.user_by_deviceid("dev_1234")["userid"], "testuser"
    )  # Test that testuser was found by deviceid

    bumper.user_remove_device("testuser", "dev_1234")  # Remove device from testuser

    assert_true(
        "dev_1234" not in bumper.user_get("testuser")["devices"]
    )  # Test that dev_1234 was not found in testuser devices

    bumper.user_add_bot("testuser", "bot_1234")  # Add bot did to testuser

    assert_true(
        "bot_1234" in bumper.user_get("testuser")["bots"]
    )  # Test that bot was found in testuser's bot list

    bumper.user_remove_bot("testuser", "bot_1234")  # Remove bot did from testuser

    assert_true(
        "bot_1234" not in bumper.user_get("testuser")["bots"]
    )  # Test that bot was not found in testuser's bot list

    bumper.user_add_token("testuser", "token_1234")  # Add token to testuser

    assert_true(
        bumper.check_token("testuser", "token_1234")
    )  # Test that token was found for testuser

    assert_true(
        bumper.user_get_token("testuser", "token_1234")
    )  # Test that token was returned for testuser

    bumper.user_add_authcode(
        "testuser", "token_1234", "auth_1234"
    )  # Add authcode to token_1234 for testuser
    assert_true(
        bumper.check_authcode("testuser", "auth_1234")
    )  # Test that authcode was found for testuser

    bumper.user_revoke_authcode(
        "testuser", "token_1234", "auth_1234"
    )  # Remove authcode from testuser
    assert_false(
        bumper.check_authcode("testuser", "auth_1234")
    )  # Test that authcode was not found for testuser
    bumper.user_revoke_token("testuser", "token_1234")  # Remove token from testuser
    assert_false(
        bumper.check_token("testuser", "token_1234")
    )  # Test that token was not found for testuser
    bumper.user_add_token("testuser", "token_1234")  # Add token_1234
    bumper.user_add_token("testuser", "token_4321")  # Add token_4321
    assert_equals(
        len(bumper.user_get_tokens("testuser")), 2
    )  # Test 2 tokens are available
    bumper.user_revoke_all_tokens("testuser")  # Revoke all tokens
    assert_equals(
        len(bumper.user_get_tokens("testuser")), 0
    )  # Test 0 tokens are available

    db = TinyDB("tests/tmp.db")
    tokens = db.table("tokens")
    tokens.insert(
        {
            "userid": "testuser",
            "token": "token_1234",
            "expiration": "{}".format(
                datetime.datetime.now() + datetime.timedelta(seconds=-10)
            ),
        }
    )  # Add expired token
    db.close()
    assert_equals(
        len(bumper.user_get_tokens("testuser")), 1
    )  # Test 1 tokens are available
    bumper.user_revoke_expired_tokens("testuser")  # Revoke expired tokens
    assert_equals(
        len(bumper.user_get_tokens("testuser")), 0
    )  # Test 0 tokens are available

    db = TinyDB("tests/tmp.db")
    tokens = db.table("tokens")
    tokens.insert(
        {
            "userid": "testuser",
            "token": "token_1234",
            "expiration": "{}".format(
                datetime.datetime.now() + datetime.timedelta(seconds=-10)
            ),
        }
    )  # Add expired token
    db.close()
    assert_equals(
        len(bumper.user_get_tokens("testuser")), 1
    )  # Test 1 tokens are available
    bumper.revoke_expired_tokens()  # Revoke expired tokens
    assert_equals(
        len(bumper.user_get_tokens("testuser")), 0
    )  # Test 0 tokens are available


def test_bot_db():
    bumper.db = "tests/tmp.db"  # Set db location for testing
    bumper.bot_add("sn_123", "did_123", "dev_123", "res_123", "co_123")
    assert_true(bumper.bot_get("did_123"))  # Test that bot was added to db

    bumper.bot_set_nick("did_123", "nick_123")
    assert_equals(
        bumper.bot_get("did_123")["nick"], "nick_123"
    )  # Test that nick was added to bot

    bumper.bot_set_mqtt("did_123", True)
    assert_true(
        bumper.bot_get("did_123")["mqtt_connection"]
    )  # Test that mqtt was set True for bot

    bumper.bot_set_xmpp("did_123", True)
    assert_true(
        bumper.bot_get("did_123")["xmpp_connection"]
    )  # Test that xmpp was set True for bot

    bumper.bot_remove("did_123")
    assert_false(bumper.bot_get("did_123"))  # Test that bot is no longer in db


def test_client_db():
    bumper.db = "tests/tmp.db"  # Set db location for testing
    bumper.client_add("user_123", "realm_123", "resource_123")
    assert_true(bumper.client_get("resource_123"))  # Test client was added

    bumper.client_set_mqtt("resource_123", True)
    assert_true(
        bumper.client_get("resource_123")["mqtt_connection"]
    )  # Test that mqtt was set True for client

    bumper.client_set_xmpp("resource_123", False)
    assert_false(
        bumper.client_get("resource_123")["xmpp_connection"]
    )  # Test that xmpp was set False for client    
    assert_equals(len(bumper.get_disconnected_xmpp_clients()), 1) # Test len of connected xmpp clients is 1