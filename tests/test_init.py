import mock
from mock import patch
import pytest
from tinydb.storages import MemoryStorage
from tinydb import TinyDB, Query
import bumper
import os
import platform
import json
import asyncio
from testfixtures import LogCapture


def test_strtobool():
    assert bumper.strtobool("t") == True
    assert bumper.strtobool("f") == False
    assert bumper.strtobool(0) == False


async def test_start_stop():
    with LogCapture() as l:
        if os.path.exists("tests/tmp.db"):
            os.remove("tests/tmp.db")  # Remove existing db

        b = bumper
        b.db = "tests/tmp.db"  # Set db location for testing
        b.conf1_listen_address = "127.0.0.1"
        b.conf1_listen_port = 444
        asyncio.create_task(b.start())
        await asyncio.sleep(0.1)
        l.check_present(("bumper", "INFO", "Starting Bumper"))
        l.clear()

        asyncio.create_task(b.shutdown())
        await asyncio.sleep(0.1)
        l.check_present(
            ("bumper", "INFO", "Shutting down"), ("bumper", "INFO", "Shutdown complete")
        )
        assert b.shutting_down == True


async def test_start_stop_debug():
    with LogCapture() as l:
        if os.path.exists("tests/tmp.db"):
            os.remove("tests/tmp.db")  # Remove existing db

        b = bumper
        b.db = "tests/tmp.db"  # Set db location for testing
        b.bumper_listen = "0.0.0.0"
        b.bumper_debug = True
        asyncio.create_task(b.start())

        await asyncio.sleep(0.1)
        asyncio.create_task(b.shutdown())
        l.check_present(("bumper", "INFO", "Starting Bumper"))
        l.clear()
        await asyncio.sleep(0.1)
        l.check_present(
            ("bumper", "INFO", "Shutting down"), ("bumper", "INFO", "Shutdown complete")
        )
        assert b.shutting_down == True

