#!/usr/bin/env python3

import logging
import asyncio
import os
from hbmqtt.broker import Broker
import hbmqtt

class MQTTServer():
    clients = []
    exit_flag = False
    default_config = {}

    @asyncio.coroutine
    def broker_coro(self):    
        broker = hbmqtt.broker.Broker(config=self.default_config, plugin_namespace=".")
    
        yield from broker.start()   

    def __init__(self, address, run_async=False):
        try:            
            # Initialize bot server
            self.default_config = {
                'listeners': {
                    'default': {
                        'type': 'tcp',
                    },
                    'tls1': {
                        'bind': "{}:{}".format(address[0], address[1]),
                        'ssl': 'on',
                        'certfile': './certs/cert.pem',
                        'keyfile': './certs/key.pem',
                    },
                },
                'sys_interval': 10,
                'auth': {
                    'allow-anonymous': True,
                    'password-file': os.path.join(os.path.dirname(os.path.realpath(__file__)), "passwd"),
                    'plugins': [
                        'VacBotAuth'
                    ]
                },
                'topic-check': {
                    'enabled': False
                }
            }
            if run_async:
                self.run()
        finally:
            print("Done")     

    def run(self):
        formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=formatter)
        eloop = asyncio.get_event_loop().run_until_complete(self.broker_coro())        
        asyncio.get_event_loop().run_forever()

