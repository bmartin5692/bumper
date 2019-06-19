import mock
from mock import patch
import pytest
from tinydb.storages import MemoryStorage
from tinydb import TinyDB, Query
import bumper
import os
import datetime, time
import platform
import json
import asyncio
from testfixtures import LogCapture
import sys


def mock_subrun(*args):
    return args


@patch("bumper.start")
def test_argparse(mock_start):
    bumper.ca_cert = "tests/test_certs/ca.crt"
    bumper.server_cert = "tests/test_certs/bumper.crt"
    bumper.server_key = "tests/test_certs/bumper.key"

    bumper.main(["--debug"])
    assert bumper.bumper_debug == True
    assert mock_start.called == True

    bumper.main(["--listen", "127.0.0.1"])
    assert bumper.bumper_listen == "127.0.0.1"
    assert mock_start.called == True

    bumper.main(["--announce", "127.0.0.1"])
    assert bumper.bumper_announce_ip == "127.0.0.1"
    assert mock_start.called == True

    bumper.main(["--debug", "--listen", "127.0.0.1", "--announce", "127.0.0.1"])
    assert bumper.bumper_debug == True
    assert bumper.bumper_announce_ip == "127.0.0.1"
    assert bumper.bumper_listen == "127.0.0.1"
    assert mock_start.called == True


@patch("subprocess.run")
@patch("platform.system")
@patch("platform.machine")
@patch("os.execv")
def test_createcert(mock_run, mock_platform, mock_machine, mock_exec):
    mock_run.side_effect = mock_subrun
    platform.system.return_value = "darwin"
    bumper.create_certs()
    assert mock_run.called == True
    assert (
        os.path.join("..", "create_certs", "create_certs_osx")
        in mock_exec.call_args.args[0]
    )

    platform.system.return_value = "windows"
    bumper.create_certs()
    assert mock_run.called == True
    assert (
        os.path.join("..", "create_certs", "create_certs_windows.exe")
        in mock_exec.call_args.args[0]
    )

    platform.system.return_value = "linux"
    bumper.create_certs()
    assert mock_run.called == True
    assert (
        os.path.join("..", "create_certs", "create_certs_linux")
        in mock_exec.call_args.args[0]
    )

    platform.system.return_value = "linux"
    platform.machine.return_value = "arm"
    bumper.create_certs()
    assert mock_run.called == True
    assert (
        os.path.join("..", "create_certs", "create_certs_rpi")
        in mock_exec.call_args.args[0]
    )

    with LogCapture() as l:
        platform.system.return_value = "nixbad"
        bumper.create_certs()

    l.check_present(
        (
            "root",
            "CRITICAL",
            "Can't determine platform. Create certs manually and try again.",
        )
    )


@patch("bumper.first_run")
def test_main(mock_firstrun):
    bumper.ca_cert = "sf"
    bumper.main()
    assert mock_firstrun.called == True
    bumper.ca_cert = "tests/test_certs/ca.crt"
