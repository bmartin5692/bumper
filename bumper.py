#!/usr/bin/env python3

import logging
import bumper
import sys, socket
import time
import platform

bumperlog = logging.getLogger("bumper")
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

    # A default bot could be set here to automatically add it as available
    # dbot = bumper.VacBotDevice("did", "class", "resource", "name","nick" )
    # bclient = bumper.bumper_bots_var
    # bclienttemp = bclient.get()
    # bclienttemp.append(dbot.asdict())
    # bclient.set(bclienttemp)

    if platform.system() == "Darwin":
        listen_host = "0.0.0.0"
    else:
        listen_host = socket.gethostbyname(socket.gethostname())
        #listen_host = "localhost" #Try this if the above doesn't work

    conf_address_443 = (listen_host, 443)
    conf_address_8007 = (listen_host, 8007)
    xmpp_address = (listen_host, 5223)
    mqtt_address = (listen_host, 8883)

    # start mqtt server on port 8883 (async)
    startmqttserver = "Starting MQTT Server at {}".format(mqtt_address)    
    bumperlog.info("{}".format(startmqttserver))
    print("{}".format(startmqttserver))
    mqtt_server = bumper.MQTTServer(mqtt_address, run_async=True,bumper_bots=bumper.bumper_bots_var,bumper_clients=bumper.bumper_clients_var)
    time.sleep(1.5) #Wait for broker startup

    # start mqtt_helperbot (async)
    bumperlog.info("Starting MQTT HelperBot")
    print("Starting MQTT HelperBot")
    mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address, run_async=True,bumper_bots=bumper.bumper_bots_var,bumper_clients=bumper.bumper_clients_var)

    # start conf server on port 443 (async) - Used for most https calls
    startconf443 = "Starting Main ConfServer at {}".format(conf_address_443)
    bumperlog.info("{}".format(startconf443))
    print("{}".format(startconf443))
    conf_server = bumper.ConfServer(conf_address_443, usessl=True, run_async=True,bumper_bots=bumper.bumper_bots_var,bumper_clients=bumper.bumper_clients_var, helperbot=mqtt_helperbot)

    # start conf server on port 8007 (async) - Used for a load balancer request
    startconf8007 = "Starting LoadBalancer ConfServer at {}".format(conf_address_8007)
    bumperlog.info("{}".format(startconf8007))
    print("{}".format(startconf8007))    
    conf_server_2 = bumper.ConfServer(conf_address_8007, usessl=False, run_async=True,bumper_bots=bumper.bumper_bots_var,bumper_clients=bumper.bumper_clients_var, helperbot=mqtt_helperbot)

    # start xmpp server on port 5223 (sync)
    startxmpp = "Starting XMPP Server at {}".format(xmpp_address)
    bumperlog.info("{}".format(startxmpp))
    print("{}".format(startxmpp))
    xmpp_server = bumper.XMPPServer(xmpp_address)

if __name__ == "__main__":
    main()