#!/usr/bin/env python3

import logging
import bumper

logging.basicConfig(level=logging.INFO,
                        format='%(levelname)-8s %(message)s')

bumper.ConfServer()
bumper.XMPPServer()

try:
	while True:
		pass
except KeyboardInterrupt:
    logging.info('keyboard interrupt')
