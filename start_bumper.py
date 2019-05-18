#!/usr/bin/env python3

import logging
import bumper
import sys, socket
import time
import platform
import os
os.environ['PYTHONASYNCIODEBUG'] = '1'
import asyncio


def main():
    args = sys.argv
    listen_host = ""

    if len(args) > 0:
        if "--debug" in args:
            logging.basicConfig(
                level=logging.DEBUG,
                format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)d :: %(message)s",
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s",
            )
            # format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)d :: %(message)s")
    
        if "--listen" in args:            
            listen_host = args[args.index("--listen") + 1]
    
    if listen_host == "":
        if platform.system() == "Darwin":  # If a Mac, use 0.0.0.0 for listening
            listen_host = "0.0.0.0"
        else:
            listen_host = socket.gethostbyname(socket.gethostname())      
    
    conf_address_443 = (listen_host, 443)
    conf_address_8007 = (listen_host, 8007)
    xmpp_address = (listen_host, 5223)
    mqtt_address = (listen_host, 8883)

    xmpp_server = bumper.XMPPServer(
        xmpp_address
    )
    mqtt_server = bumper.MQTTServer(mqtt_address)
    mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address)
    conf_server = bumper.ConfServer(
        conf_address_443, usessl=True, helperbot=mqtt_helperbot
    )
    conf_server_2 = bumper.ConfServer(
        conf_address_8007, usessl=False, helperbot=mqtt_helperbot
    )

    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()

    # Start web servers
    loop.set_debug(True)
    conf_server.confserver_app()
    conf_server_2.confserver_app()
    asyncio.ensure_future(conf_server.start_server(),loop=loop)
    asyncio.ensure_future(conf_server_2.start_server(),loop=loop)

    # Start MQTT Server
    asyncio.ensure_future(mqtt_server.broker_coro())

    # Start MQTT Helperbot
    asyncio.ensure_future(mqtt_helperbot.start_helper_bot())
    
    # Start XMPP Server
    asyncio.ensure_future(xmpp_server.async_server())

    loop.run_forever()


    # start xmpp server on port 5223 (sync)
    #xmpp_server.run(run_async=True)  # Start in new thread

    # start mqtt server on port 8883 (async)
    #mqtt_server.run(run_async=True)  # Start in new thread

    #time.sleep(1.5)  # Wait for broker startup

    # start mqtt_helperbot (async)
    #mqtt_helperbot.run(run_async=True)  # Start in new thread

    # start conf server on port 443 (async) - Used for most https calls
    #conf_server.run(run_async=True)  # Start in new thread

    # start conf server on port 8007 (async) - Used for a load balancer request
    #conf_server_2.run(run_async=True)  # Start in new thread

    while True:
        try:
            time.sleep(30)
            bumper.revoke_expired_tokens()
            disconnected_clients = bumper.get_disconnected_xmpp_clients()
            for client in disconnected_clients:
                xmpp_server.remove_client_byuid(client["userid"])

        except KeyboardInterrupt:
            bumper.bumperlog.info("Bumper Exiting - Keyboard Interrupt")
            print("Bumper Exiting")
            exit(0)


if __name__ == "__main__":
    main()
