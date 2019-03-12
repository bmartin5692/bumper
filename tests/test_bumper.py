from nose.tools import *
from tinydb.storages import MemoryStorage
from tinydb import TinyDB, Query
import bumper


def test_useradd():
    btest = bumper
    btest.db = "tests/tmp.db"
    btest.user_add("testuser")

    db = TinyDB("tests/tmp.db")
    users = db.table("users").search(Query().userid == "testuser")
    assert_equals(len(users), 1)
