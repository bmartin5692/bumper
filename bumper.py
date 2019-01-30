#!/usr/bin/env python3

import logging
import bumper
import sys, socket

logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s')

#conf_address = (socket.gethostbyname(socket.gethostname()), 443)
conf_address = ("0.0.0.0", 443)
#xmpp_address = (socket.gethostbyname(socket.gethostname()), 5223)
xmpp_address = ("0.0.0.0", 5223)
#mqtt_address = (socket.gethostbyname(socket.gethostname()), 8883)
mqtt_address = ("0.0.0.0", 8883)

# start conf server (async)
conf_server = bumper.ConfServer(conf_address, usessl=True, run_async=True)
# start mqtt server (async)
mqtt_server = bumper.MQTTServer(mqtt_address, run_async=True)

# start xmpp server (sync)
xmpp_server = bumper.XMPPServer(xmpp_address)

conf_server.disconnect()
