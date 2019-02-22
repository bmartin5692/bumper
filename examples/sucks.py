#!/usr/bin/env python3

from sucks import *


class BumperVacBot(VacBot):
    def __init__(self, server_address):
        self.server_address = server_address
        vacuum = {"did": "none", "class": "none"}
        super().__init__("sucks", "ecouser.net", "", "", vacuum, "")

    def connect_and_wait_until_ready(self):
        logging.info("connecting")
        self.xmpp.connect(self.server_address)
        self.xmpp.process()
        self.xmpp.wait_until_ready()


logging.basicConfig(level=logging.DEBUG, format="%(levelname)-8s %(message)s")
server_address = ("xxx.xxx.xxx.xxx", 5223)

# Initialize
vacbot = BumperVacBot(server_address)

# Connect
vacbot.connect_and_wait_until_ready()

# Send a command
vacbot.run(Clean())
