#!/usr/bin/env python3

import logging
import bumper
import sys, socket
import time
import platform
import asyncio


def main():
    args = sys.argv

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
    
    listen_host = args.index("--listen")
    if (len(args) - 1) >= (listen_host + 1):
        listen_host = args[listen_host+1]
    else:        
        if platform.system() == "Darwin":  # If a Mac, use 0.0.0.0 for listening
            listen_host = "0.0.0.0"
        else:
            listen_host = socket.gethostbyname(socket.gethostname())
            #listen_host = "localhost"  # Try this if the above doesn't work

    
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

    # add user
    # users = bumper.bumper_users_var.get()
    # user1 = bumper.BumperUser('user1')
    # user1.add_device('devid')
    # user1.add_bot('bot_did')
    # users.append(user1)
    # bumper.bumper_users_var.set(users)

    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()

    # Start web servers
    conf_server.confserver_app()
    conf_server_2.confserver_app()
    asyncio.ensure_future(conf_server.start_server(),loop=loop)
    asyncio.ensure_future(conf_server_2.start_server(),loop=loop)

    # Start MQTT Server
    asyncio.ensure_future(mqtt_server.broker_coro())

    # Start MQTT Helperbot
    asyncio.ensure_future(mqtt_helperbot.start_helper_bot())
    
    loop.run_forever()

    # start xmpp server on port 5223 (sync)
    xmpp_server.run(run_async=True)  # Start in new thread

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
