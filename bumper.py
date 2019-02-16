#!/usr/bin/env python3

import logging
import bumper
import sys, socket
import time
import platform


def main():
    args = sys.argv
    
    if len(args) > 0:
        if '--debug' in args:
            logging.basicConfig(level=logging.DEBUG,        
                format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)d :: %(message)s")
        else:
            logging.basicConfig(level=logging.INFO,
                format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s")
                #format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)d :: %(message)s")

    if platform.system() == "Darwin": #If a Mac, use 0.0.0.0 for listening
        listen_host = "0.0.0.0"
    else:
        listen_host = socket.gethostbyname(socket.gethostname())
        #listen_host = "localhost" #Try this if the above doesn't work

    conf_address_443 = (listen_host, 443)
    conf_address_8007 = (listen_host, 8007)
    xmpp_address = (listen_host, 5223)
    mqtt_address = (listen_host, 8883)
    
    xmpp_server = bumper.XMPPServer(xmpp_address)
    mqtt_server = bumper.MQTTServer(mqtt_address,bumper_bots=bumper.bumper_bots_var,bumper_clients=bumper.bumper_clients_var,remove_clients=bumper.bumper_removeclients_var)
    mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address, bumper_bots=bumper.bumper_bots_var,bumper_clients=bumper.bumper_clients_var)
    conf_server = bumper.ConfServer(conf_address_443, usessl=True, bumper_bots=bumper.bumper_bots_var,bumper_clients=bumper.bumper_clients_var, remove_clients=bumper.bumper_removeclients_var,helperbot=mqtt_helperbot)
    conf_server_2 = bumper.ConfServer(conf_address_8007, usessl=False, bumper_bots=bumper.bumper_bots_var,bumper_clients=bumper.bumper_clients_var, helperbot=mqtt_helperbot,remove_clients=bumper.bumper_removeclients_var)
    
    # start xmpp server on port 5223 (sync)
    xmpp_server.run(run_async=True) #Start in new thread

    # start mqtt server on port 8883 (async)    
    mqtt_server.run(run_async=True) #Start in new thread    
    
    time.sleep(1.5) #Wait for broker startup

    # start mqtt_helperbot (async)       
    mqtt_helperbot.run(run_async=True) #Start in new thread

    # start conf server on port 443 (async) - Used for most https calls        
    conf_server.run(run_async=True) #Start in new thread

    # start conf server on port 8007 (async) - Used for a load balancer request    
    conf_server_2.run(run_async=True) #Start in new thread

    while True:
        try:
            time.sleep(0.25)

            # WIP: Remove clients that have disconnected
            remove_clients = bumper.bumper_removeclients_var.get()
            if len(remove_clients) > 0:
                for uid in remove_clients:
                    if uid != "":
                        xmpp_server.remove_client_byuid(uid)  #Remove clients from xmpp server
                        remove_clients.remove(uid)
                
                bumper.bumper_removeclients_var.set(remove_clients)
        
        except KeyboardInterrupt:                
            print("Bumper Exiting")
    
if __name__ == "__main__":
    main()