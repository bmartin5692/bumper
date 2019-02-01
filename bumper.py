#!/usr/bin/env python3

import logging
import bumper
import sys, socket
import time


args = sys.argv
if len(args) > 0:
    if '--debug' in args:
        logging.basicConfig(level=logging.DEBUG,        
            format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s")
    else:
        logging.basicConfig(level=logging.INFO,
            format="[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s")

#conf_address = (socket.gethostbyname(socket.gethostname()), 443)
conf_address = ("0.0.0.0", 443)
#xmpp_address = (socket.gethostbyname(socket.gethostname()), 5223)
xmpp_address = ("0.0.0.0", 5223)
#mqtt_address = (socket.gethostbyname(socket.gethostname()), 8883)
mqtt_address = ("0.0.0.0", 8883)

# A default bot could be set here to automatically add it as available
# dbot = bumper.VacBotDevice("did", "class", "resource", "name","nick" )
# bclient = bumper.bumper_clients_var
# bclienttemp = bclient.get()
# bclienttemp.append(dbot.asdict())
# bclient.set(bclienttemp)

# start mqtt server (async)
mqtt_server = bumper.MQTTServer(mqtt_address, run_async=True,bumper_clients=bumper.bumper_clients_var)
time.sleep(1.5) #Wait for broker startup
# start mqtt server (async)
mqtt_helperbot = bumper.MQTTHelperBot(mqtt_address, run_async=True,bumper_clients=bumper.bumper_clients_var)
# start conf server (async)
conf_server = bumper.ConfServer(conf_address, usessl=True, run_async=True, bumper_clients=bumper.bumper_clients_var, helperbot=mqtt_helperbot)
# start xmpp server (sync)
xmpp_server = bumper.XMPPServer(xmpp_address)

