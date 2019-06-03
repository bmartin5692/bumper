import mock
import bumper
import asyncio
import pytest
import os
import json
import tinydb
import pytest_asyncio


def return_send_data(data, *args, **kwargs):
    return data


def mock_transport_extra_info(*args, **kwargs):
    return ("127.0.0.1", 1234)


async def test_client(*args, **kwargs):
    test_transport = asyncio.Transport()
    test_transport.get_extra_info = mock.Mock(return_value=mock_transport_extra_info())
    test_transport.write = mock.Mock(return_value=return_send_data)
    xmppclient = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient.state = xmppclient.INIT  # Set client state to INIT
    mock_send = xmppclient.send = mock.Mock(side_effect=return_send_data)

    # Send init connect stream from "client"
    test_data = "<stream:stream xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0' to='ecouser.net'>".encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    # Expect 2 calls to send
    assert mock_send.call_count == 2
    # Server opens stream
    assert (
        mock_send.mock_calls[0].args[0]
        == '<stream:stream xmlns:stream="http://etherx.jabber.org/streams" xmlns="jabber:client" version="1.0" id="1" from="ecouser.net">'
    )
    # Server tells client available features
    assert (
        mock_send.mock_calls[1].args[0]
        == '<stream:features><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"/><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></stream:features>'
    )

    # Reset mock calls
    mock_send.reset_mock()

