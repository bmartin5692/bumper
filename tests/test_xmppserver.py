import mock
import bumper
import asyncio
import pytest
import os
import json
import tinydb
import pytest_asyncio
import xml.etree.ElementTree as ET
import socket
from testfixtures import LogCapture
import ssl


def return_send_data(data, *args, **kwargs):
    return data


def mock_transport_extra_info(*args, **kwargs):
    return ("127.0.0.1", 5223)


async def test_xmpp_server():
    xmpp_address = ("127.0.0.1", 5223)
    xmpp_server = bumper.XMPPServer(xmpp_address)
    await xmpp_server.start_async_server()

    with LogCapture("xmppserver") as l:

        reader, writer = await asyncio.open_connection("127.0.0.1", 5223)

        writer.write(b"<stream:stream />")  # Start stream
        await writer.drain()

        await asyncio.sleep(0.1)

        assert len(xmpp_server.clients) == 1  # Client count increased
        assert (
            xmpp_server.clients[0].address[1]
            == writer.transport.get_extra_info("sockname")[1]
        )

        writer.close()  # Close connection
        await writer.wait_closed()

        await asyncio.sleep(0.1)

        assert len(xmpp_server.clients) == 0  # Client count decreased

        reader, writer = await asyncio.open_connection("127.0.0.1", 5223)

        writer.write(b"<stream:stream />")  # Start stream
        await writer.drain()

        await asyncio.sleep(0.1)

    xmpp_server.disconnect()


async def test_client_connect_no_starttls(*args, **kwargs):
    test_transport = asyncio.Transport()
    test_transport.get_extra_info = mock.Mock(return_value=mock_transport_extra_info())
    test_transport.write = mock.Mock(return_value=return_send_data)
    xmppclient = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient.state = xmppclient.CONNECT  # Set client state to CONNECT
    mock_send = xmppclient.send = mock.Mock(side_effect=return_send_data)

    # Send connect stream from "client"
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
        == '<stream:features><starttls xmlns="urn:ietf:params:xml:ns:xmpp-tls"><required/></starttls><mechanisms xmlns="urn:ietf:params:xml:ns:xmpp-sasl"><mechanism>PLAIN</mechanism></mechanisms></stream:features>'
    )

    # Reset mock calls
    mock_send.reset_mock()

    # Client sendss auth - Ignoring the starttls, we don't force this with bumper
    test_data = '<auth xmlns="urn:ietf:params:xml:ns:xmpp-sasl" mechanism="PLAIN">AGZ1aWRfdG1wdXNlcgAwL0lPU0Y1M0QwN0JBL3VzXzg5ODgwMmZkYmM0NDQxYjBiYzgxNWIxZDFjNjgzMDJl</auth>'.encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<success xmlns="urn:ietf:params:xml:ns:xmpp-sasl"/>'
    )  # Client successfully authenticated
    assert xmppclient.state == xmppclient.INIT  # Client moved to INIT state


async def test_client_end_stream(*args, **kwargs):
    test_transport = asyncio.Transport()
    test_transport.get_extra_info = mock.Mock(return_value=mock_transport_extra_info())
    test_transport.write = mock.Mock(return_value=return_send_data)
    xmppclient = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient.state = xmppclient.CONNECT  # Set client state to CONNECT
    mock_send = xmppclient.send = mock.Mock(side_effect=return_send_data)

    # Send end stream from "client"
    test_data = "</stream:stream>".encode("utf-8")
    xmppclient._parse_data(test_data)

    # Expect 2 calls to send
    assert mock_send.call_count == 1
    # Server opens stream
    assert mock_send.mock_calls[0].args[0] == "</stream:stream>"

    # Reset mock calls
    mock_send.reset_mock()

    # Send abnormal stream from "client"
    test_data = "<badstr />".encode("utf-8")
    xmppclient._parse_data(test_data)

    # Reset mock calls
    mock_send.reset_mock()

    # Send blank from "client"
    test_data = "".encode("utf-8")
    xmppclient._parse_data(test_data)


async def test_client_connect_starttls_called(*args, **kwargs):
    test_transport = asyncio.Transport()
    test_transport.get_extra_info = mock.Mock(return_value=mock_transport_extra_info())
    test_transport.write = mock.Mock(return_value=return_send_data)
    xmppclient = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient.state = xmppclient.CONNECT  # Set client state to CONNECT
    mock_send = xmppclient.send = mock.Mock(side_effect=return_send_data)

    # Send connect stream from "client"
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
        == '<stream:features><starttls xmlns="urn:ietf:params:xml:ns:xmpp-tls"><required/></starttls><mechanisms xmlns="urn:ietf:params:xml:ns:xmpp-sasl"><mechanism>PLAIN</mechanism></mechanisms></stream:features>'
    )

    # Reset mock calls
    mock_send.reset_mock()

    mock_tls = xmppclient._handle_starttls = mock.Mock()

    # Send start tls from "client"
    test_data = "<starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'/>".encode("utf-8")
    xmppclient._parse_data(test_data)

    # After upgrading connection, server tells client to proceed with auth again
    assert mock_tls.called
    xmppclient.TLSUpgraded = True

    # After TLS is upgraded, Client establishes session again and will auth this time
    # Send connect stream from "client"
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
    # Server tells client available features (without STARTTLS)
    assert (
        mock_send.mock_calls[1].args[0]
        == '<stream:features><mechanisms xmlns="urn:ietf:params:xml:ns:xmpp-sasl"><mechanism>PLAIN</mechanism></mechanisms></stream:features>'
    )
    # Reset mock calls
    mock_send.reset_mock()

    # Client sends auth
    test_data = '<auth xmlns="urn:ietf:params:xml:ns:xmpp-sasl" mechanism="PLAIN">AGZ1aWRfdG1wdXNlcgAwL0lPU0Y1M0QwN0JBL3VzXzg5ODgwMmZkYmM0NDQxYjBiYzgxNWIxZDFjNjgzMDJl</auth>'.encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<success xmlns="urn:ietf:params:xml:ns:xmpp-sasl"/>'
    )  # Client successfully authenticated
    assert xmppclient.state == xmppclient.INIT  # Client moved to INIT state


async def test_xmpp_server_client_tls():

    xmpp_address = ("127.0.0.1", 5223)
    xmpp_server = bumper.XMPPServer(xmpp_address)
    await xmpp_server.start_async_server()

    with LogCapture("xmppserver") as l:

        async def do_stuff_after_start_tls(
            ssl_reader, ssl_writer
        ):  # Used after starttls

            writer.write(
                b"<stream:stream xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0' to='ecouser.net'>"
            )  # New Stream

            await writer.drain()

            writer.write(
                b'<auth xmlns="urn:ietf:params:xml:ns:xmpp-sasl" mechanism="PLAIN">AGZ1aWRfdG1wdXNlcgAwL0lPU0Y1M0QwN0JBL3VzXzg5ODgwMmZkYmM0NDQxYjBiYzgxNWIxZDFjNjgzMDJl</auth>'
            )  # Send Auth

            await writer.drain()

    reader, writer = await asyncio.open_connection("127.0.0.1", 5223)

    writer.write(
        b"<stream:stream xmlns='jabber:client' xmlns:stream='http://etherx.jabber.org/streams' version='1.0' to='ecouser.net'>"
    )  # Start stream
    await writer.drain()

    await asyncio.sleep(0.1)

    writer.write(
        b"<starttls xmlns='urn:ietf:params:xml:ns:xmpp-tls'/>"
    )  # Send StartTLS
    await writer.drain()

    await asyncio.sleep(0.1)

    # Below will upgrade connection to TLS then callback to "do_stuff_after_start_tls"
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ssl_context.check_hostname = False
    ssl_context.load_verify_locations(cafile=bumper.ca_cert)
    loop = asyncio.get_event_loop()
    transport = writer.transport
    protocol = writer.transport.get_protocol()
    new_transport = await loop.start_tls(
        transport, protocol, ssl_context, server_side=False
    )
    protocol._stream_reader = asyncio.StreamReader(loop=loop)
    protocol._client_connected_cb = do_stuff_after_start_tls
    protocol.connection_made(new_transport)

    print(l)


async def test_client_init(*args, **kwargs):
    test_transport = asyncio.Transport()
    test_transport.get_extra_info = mock.Mock(return_value=mock_transport_extra_info())
    test_transport.write = mock.Mock(return_value=return_send_data)
    xmppclient = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient.state = xmppclient.INIT  # Set client state to INIT
    xmppclient.uid = "fuid_tmpuser"
    xmppclient.resource = "IOSF53D07BA"
    xmppclient.bumper_jid = "fuid_tmpuser@ecouser.net/IOSF53D07BA"
    xmppclient.type = xmppclient.CONTROLLER
    mock_send = xmppclient.send = mock.Mock(side_effect=return_send_data)

    # Send connect stream from "client"
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
    # Server tells client binds
    assert (
        mock_send.mock_calls[1].args[0]
        == '<stream:features><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"/><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></stream:features>'
    )

    # Reset mock calls
    mock_send.reset_mock()

    # Send bind from "client"
    test_data = '<iq type="set" id="5E9872D5-547E-49AF-AE51-9EFAA282F952"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"><resource>IOSF53D07BA</resource></bind></iq>'.encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<iq type="result" id="5E9872D5-547E-49AF-AE51-9EFAA282F952"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"><jid>fuid_tmpuser@ecouser.net/IOSF53D07BA</jid></bind></iq>'
    )  # client successfully binded
    assert xmppclient.state == xmppclient.BIND  # client moved to BIND state

    # Reset mock calls
    mock_send.reset_mock()

    # Send set session from client
    test_data = '<iq type="set" id="FA1041E7-AA27-43DD-BAA3-64DE2DE56AA3"><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></iq>'.encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert xmppclient.state == xmppclient.READY  # client moved to READY state
    assert (
        mock_send.mock_calls[0].args[0]
        == '<iq type="result" id="FA1041E7-AA27-43DD-BAA3-64DE2DE56AA3" />'
    )  # client ready

    # Reset mock calls
    mock_send.reset_mock()

    # Send presense from client
    test_data = '<presence type="available"/>'.encode("utf-8")
    xmppclient._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<presence to="fuid_tmpuser@ecouser.net/IOSF53D07BA"> dummy </presence>'
    )  # client presence - dummy response


async def test_bot_connect(*args, **kwargs):
    test_transport = asyncio.Transport()
    test_transport.get_extra_info = mock.Mock(return_value=mock_transport_extra_info())
    test_transport.write = mock.Mock(return_value=return_send_data)
    xmppclient = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient.state = xmppclient.CONNECT  # Set client state to CONNECT
    mock_send = xmppclient.send = mock.Mock(side_effect=return_send_data)

    # Send connect stream from "bot"
    test_data = "<stream:stream xmlns:stream='http://etherx.jabber.org/streams' xmlns='jabber:client' to='159.ecorobot.net' version='1.0'>".encode(
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
        == '<stream:features><starttls xmlns="urn:ietf:params:xml:ns:xmpp-tls"><required/></starttls><mechanisms xmlns="urn:ietf:params:xml:ns:xmpp-sasl"><mechanism>PLAIN</mechanism></mechanisms></stream:features>'
    )

    # Reset mock calls
    mock_send.reset_mock()

    # Send auth from "bot"
    test_data = "<auth xmlns='urn:ietf:params:xml:ns:xmpp-sasl' mechanism='PLAIN'>AEUwMDAwMDAwMDAwMDAwMDAxMjM0AGVuY3J5cHRlZF9wYXNz</auth>".encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<success xmlns="urn:ietf:params:xml:ns:xmpp-sasl"/>'
    )  # Bot successfully authenticated
    assert xmppclient.state == xmppclient.INIT  # Bot moved to INIT state
    assert xmppclient.type == xmppclient.BOT  # Client type is now bot


async def test_bot_init(*args, **kwargs):
    test_transport = asyncio.Transport()
    test_transport.get_extra_info = mock.Mock(return_value=mock_transport_extra_info())
    test_transport.write = mock.Mock(return_value=return_send_data)
    xmppclient = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient.state = xmppclient.INIT  # Set client state to INIT
    xmppclient.uid = "E0000000000000001234"
    xmppclient.devclass = "159"
    xmppclient.type = xmppclient.BOT
    mock_send = xmppclient.send = mock.Mock(side_effect=return_send_data)

    # Send connect stream from "bot"
    test_data = "<stream:stream xmlns:stream='http://etherx.jabber.org/streams' xmlns='jabber:client' to='159.ecorobot.net' version='1.0'>".encode(
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
    # Server tells client binds
    assert (
        mock_send.mock_calls[1].args[0]
        == '<stream:features><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"/><session xmlns="urn:ietf:params:xml:ns:xmpp-session"/></stream:features>'
    )

    # Reset mock calls
    mock_send.reset_mock()

    # Send bind from "bot"
    test_data = "<iq type='set' id='2521'><bind xmlns='urn:ietf:params:xml:ns:xmpp-bind'><resource>atom</resource></bind></iq>".encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<iq type="result" id="2521"><bind xmlns="urn:ietf:params:xml:ns:xmpp-bind"><jid>E0000000000000001234@159.ecorobot.net/atom</jid></bind></iq>'
    )  # Bot successfully binded
    assert xmppclient.state == xmppclient.BIND  # Bot moved to BIND state

    # Reset mock calls
    mock_send.reset_mock()

    # Send set session from bot
    test_data = "<iq type='set' id='2522'><session xmlns='urn:ietf:params:xml:ns:xmpp-session'/></iq>".encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert xmppclient.state == xmppclient.READY  # Bot moved to READY state
    assert (
        mock_send.mock_calls[0].args[0] == '<iq type="result" id="2522" />'
    )  # Bot ready

    # Reset mock calls
    mock_send.reset_mock()

    # Send presense from bot
    test_data = "<presence><status>hello world</status></presence><iq type='result' from='E0000000000000001234@159.ecorobot.net/atom' to='ecouser.net' id='s2c1'/>".encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<presence to="E0000000000000001234@159.ecorobot.net/atom"> dummy </presence>'
    )  # bot presence - dummy response


async def test_ping_server(*args, **kwargs):
    test_transport = asyncio.Transport()
    test_transport.get_extra_info = mock.Mock(return_value=mock_transport_extra_info())
    test_transport.write = mock.Mock(return_value=return_send_data)
    xmppclient = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient.state = xmppclient.READY  # Set client state to READY
    xmppclient.uid = "E0000000000000001234"
    xmppclient.devclass = "159"
    mock_send = xmppclient.send = mock.Mock(side_effect=return_send_data)

    # Ping from bot
    test_data = '<iq xmlns:ns0="urn:xmpp:ping" from="E000BVTNX18700260382@159.ecorobot.net/atom" id="2542" to="159.ecorobot.net" type="get"><ping /></iq>'.encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<iq type="result" id="2542" from="159.ecorobot.net" />'
    )  # ping response


async def test_ping_client_to_client(*args, **kwargs):

    test_transport = asyncio.Transport()
    test_transport.get_extra_info = mock.Mock(return_value=mock_transport_extra_info())
    test_transport.write = mock.Mock(return_value=return_send_data)
    xmppclient = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient.state = xmppclient.READY  # Set client state to READY
    xmppclient.uid = "E0000000000000001234"
    xmppclient.devclass = "159"
    xmppclient.bumper_jid = "E0000000000000001234@159.ecorobot.net/atom"
    mock_send = xmppclient.send = mock.Mock(side_effect=return_send_data)

    xmppclient2 = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient2.state = xmppclient.READY  # Set client state to READY
    xmppclient2.uid = "fuid_tmpuser"
    xmppclient2.resource = "IOSF53D07BA"
    xmppclient2.bumper_jid = "fuid_tmpuser@ecouser.net/IOSF53D07BA"
    mock_send2 = xmppclient2.send = mock.Mock(side_effect=return_send_data)

    bumper.xmppserver.XMPPServer.clients.append(xmppclient)
    bumper.xmppserver.XMPPServer.clients.append(xmppclient2)

    # Ping from user to bot
    test_data = '<iq id="104934615" to="fuid_tmpuser@ecouser.net/IOSF53D07BA" type="get"><ping xmlns="urn:xmpp:ping" /></iq>'.encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert (
        mock_send2.mock_calls[0].args[0]
        == '<iq from="E0000000000000001234@159.ecorobot.net/atom" id="104934615" to="fuid_tmpuser@ecouser.net/IOSF53D07BA" type="get"><ping xmlns="urn:xmpp:ping" /></iq>'
    )  # ping response

    # Ping response from bot to user
    test_data = "<iq type='result' to='E0000000000000001234@159.ecorobot.net/atom' id='104934615'/>".encode(
        "utf-8"
    )
    xmppclient2._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<iq from="fuid_tmpuser@ecouser.net/IOSF53D07BA" id="104934615" to="E0000000000000001234@159.ecorobot.net/atom" type="result" />'
    )  # ping response


async def test_client_send_iq(*args, **kwargs):
    test_transport = asyncio.Transport()
    test_transport.get_extra_info = mock.Mock(return_value=mock_transport_extra_info())
    test_transport.write = mock.Mock(return_value=return_send_data)
    xmppclient = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient.state = xmppclient.READY  # Set client state to READY
    xmppclient.uid = "fuid_tmpuser"
    xmppclient.resource = "IOSF53D07BA"
    xmppclient.bumper_jid = "fuid_tmpuser@ecouser.net/IOSF53D07BA"
    xmppclient.type - xmppclient.CONTROLLER
    mock_send = xmppclient.send = mock.Mock(side_effect=return_send_data)
    bumper.xmppserver.XMPPServer.clients.append(xmppclient)

    xmppclient2 = bumper.xmppserver.XMPPAsyncClient(test_transport)
    xmppclient2.state = xmppclient.READY  # Set client state to READY
    xmppclient2.uid = "E0000000000000001234"
    xmppclient2.devclass = "159"
    xmppclient2.bumper_jid = "E0000000000000001234@159.ecorobot.net/atom"
    xmppclient2.type = xmppclient2.BOT
    mock_send2 = xmppclient2.send = mock.Mock(side_effect=return_send_data)

    bumper.xmppserver.XMPPServer.clients.append(xmppclient2)

    # Roster IQ - Only seen from Android app so far
    test_data = '<iq id="EE0XQ-2" type="get"><query xmlns="jabber:iq:roster" ></query></iq>'.encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<iq type="error" id="EE0XQ-2"><error type="cancel" code="501"><feature-not-implemented xmlns="urn:ietf:params:xml:ns:xmpp-stanzas"/></error></iq>'
    )  # feature not implemented response

    # Reset mock calls
    mock_send.reset_mock()

    # Bot Command
    test_data = '<iq id="7" to="E0000000000000001234@159.ecorobot.net/atom" type="set"><query xmlns="com:ctl"><ctl id="72107787" td="GetCleanState" /></query></iq>'.encode(
        "utf-8"
    )
    xmppclient._parse_data(test_data)

    assert (
        mock_send2.mock_calls[0].args[0]
        == '<iq from="fuid_tmpuser@ecouser.net/IOSF53D07BA" id="7" to="E0000000000000001234@159.ecorobot.net/atom" type="set"><query xmlns="com:ctl"><ctl id="72107787" td="GetCleanState" /></query></iq>'
    )  # command was sent to bot

    # Reset mock calls
    mock_send.reset_mock()

    # Bot response to query
    test_data = '<iq xmlns:ns0="com:ctl" id="2679" to="fuid_tmpuser@ecouser.net/IOSF53D07BA" type="set"><query><ctl td="ChargeState"><charge h="0" r="a" type="Going" /></ctl></query></iq>'.encode(
        "utf-8"
    )
    xmppclient2._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<iq from="E0000000000000001234@159.ecorobot.net/atom" id="2679" to="fuid_tmpuser@ecouser.net/IOSF53D07BA" type="set"><query xmlns="com:ctl"><ctl td="ChargeState"><charge h="0" r="a" type="Going" /></ctl></query></iq>'
    )  # result sent to client

    # Reset mock calls
    mock_send.reset_mock()

    # Bot result
    test_data = "<iq type='result' from='E0000000000000001234@159.ecorobot.net/atom' to='ecouser.net' id='s2c1'/>".encode(
        "utf-8"
    )
    xmppclient2._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<iq from="E0000000000000001234@159.ecorobot.net/atom" id="s2c1" to="ecouser.net" type="result" />'
    )  # result sent to ecouser.net

    # Reset mock calls
    mock_send.reset_mock()

    # Bot iq set
    test_data = "<iq to='fuid_tmpuser@ecouser.net/IOSF53D07BA' type='set' id='2700'><query xmlns='com:ctl'><ctl td='BatteryInfo'><battery power='100'/></ctl></query></iq>".encode(
        "utf-8"
    )
    xmppclient2._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<iq from="E0000000000000001234@159.ecorobot.net/atom" id="2700" to="fuid_tmpuser@ecouser.net/IOSF53D07BA" type="set"><query xmlns="com:ctl"><ctl td="BatteryInfo"><battery power="100" /></ctl></query></iq>'
    )  # result sent to ecouser.net

    # Reset mock calls
    mock_send.reset_mock()

    # Bot error report
    test_data = "<iq to='fuid_tmpuser@ecouser.net/IOSF53D07BA' type='set' id='631'><query xmlns='com:ctl'><ctl td='error' errs='102'/></query></iq>".encode(
        "utf-8"
    )
    xmppclient2._parse_data(test_data)

    assert (
        mock_send.mock_calls[0].args[0]
        == '<iq from="E0000000000000001234@159.ecorobot.net/atom" id="631" to="fuid_tmpuser@ecouser.net/IOSF53D07BA" type="set"><query xmlns="com:ctl"><ctl errs="102" td="error" /></query></iq>'
    )  # result sent to ecouser.net

    # Reset mock calls
    mock_send.reset_mock()

    # Bot "DorpError" to all
    test_data = "<iq to='rl.ecorobot.net' type='set' id='1234'><query xmlns='com:sf'><sf td='pub' t='log' ts='1559893796000' tp='p' k='DeviceAlert' v='DorpError' f='E0000000000000001234@159.ecorobot.net' g='fuid_tmpuser@ecouser.net'/></query></iq>".encode(
        "utf-8"
    )
    xmppclient2._parse_data(test_data)
    assert (
        mock_send.mock_calls[0].args[0]
        == '<iq xmlns="com:sf" from="E0000000000000001234@159.ecorobot.net/atom" id="1234" to="rl.ecorobot.net" type="set"><query xmlns="com:ctl"><sf f="E0000000000000001234@159.ecorobot.net" g="fuid_tmpuser@ecouser.net" k="DeviceAlert" t="log" td="pub" tp="p" ts="1559893796000" v="DorpError" /></query></iq>'
    )  # result sent to ecouser.net

    # Reset mock calls
    mock_send.reset_mock()

