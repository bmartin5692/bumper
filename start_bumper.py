#!/usr/bin/env python3

import logging
import bumper
import sys, socket
import time
import platform
import os
#os.environ['PYTHONASYNCIODEBUG'] = '1' # Uncomment to enable ASYNCIODEBUG
import asyncio


async def main():
    try:
        loop = asyncio.get_event_loop()
    except:
        loop = asyncio.new_event_loop()
    
    args = sys.argv
    listen_host = ""

    if len(args) > 0:
        if "--debug" in args:
            logging.basicConfig(
                level=logging.DEBUG,
                format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)d :: %(message)s",
            )
            loop.set_debug(True) # Set asyncio loop to debug
            #logging.getLogger("asyncio").setLevel(logging.DEBUG)  # Show debug asyncio logs (disabled in init, uncomment for debugging asyncio)
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s",
            )
    
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

    # Start web servers
    conf_server.confserver_app()    
    task_conf_server = asyncio.create_task(conf_server.start_server())
    bumper.bumperlog.debug("task_conf_server added")        
    await task_conf_server

    conf_server_2.confserver_app()
    task_conf_server2 = asyncio.create_task(conf_server_2.start_server())
    bumper.bumperlog.debug("task_conf_server2 added")
    await task_conf_server2

    # Start MQTT Server
    task_mqtt_server = asyncio.create_task(mqtt_server.broker_coro())
    bumper.bumperlog.debug("task_mqtt_server added")
    await task_mqtt_server

    # Start MQTT Helperbot
    task_mqtt_helperbot = asyncio.create_task(mqtt_helperbot.start_helper_bot())
    bumper.bumperlog.debug("task_mqtt_helperbot added")
    await task_mqtt_helperbot
    
    # Start XMPP Server
    task_xmpp_server = asyncio.create_task(xmpp_server.async_server())
    bumper.bumperlog.debug("task_xmpp_server added")
    await task_xmpp_server

    while True:
        try:
            await asyncio.sleep(30)
            bumper.revoke_expired_tokens()
            #disconnected_clients = bumper.get_disconnected_xmpp_clients()
            #for client in disconnected_clients:
            #    xmpp_server.remove_client_byuid(client["userid"])

        except KeyboardInterrupt:
            bumper.bumperlog.info("Bumper Exiting - Keyboard Interrupt")
            print("Bumper Exiting")
            exit(0)


if __name__ == "__main__":
    asyncio.run(main())
