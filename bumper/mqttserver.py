#!/usr/bin/env python3

import logging
import asyncio
import os
from hbmqtt.broker import Broker
import hbmqtt
import pkg_resources


class BumperMQTTPlugin:
    def __init__(self, context):
        self.context = context        
        logging.debug('Bumper Plugin Initialized')

    @asyncio.coroutine
    def on_broker_client_connected(self, client_id):
        logging.debug('Bumper Connection: %s connected' % client_id)
        #yield from self.context.broadcast_message('location/%s' % client_id, b'home')

    @asyncio.coroutine
    def on_broker_client_disconnected(self, client_id):
        logging.debug('Bumper Connection: %s disconnected' % client_id)
        #yield from self.context.broadcast_message('location/%s' % client_id, b'not_home')            


class MQTTServer():
    clients = []
    exit_flag = False
    default_config = {}  

    @asyncio.coroutine
    def broker_coro(self):         
        broker = hbmqtt.broker.Broker(config=self.default_config)
        yield from broker.start()  

    def __init__(self, address, run_async=False):
        #The below adds a plugin to the hbmqtt.broker.plugins without having to futz with setup.py
        distribution = pkg_resources.Distribution("hbmqtt.broker.plugins")
        bumper_plugin = pkg_resources.EntryPoint.parse('bumper = bumper.mqttserver:BumperMQTTPlugin', dist=distribution)        
        distribution._ep_map = {"hbmqtt.broker.plugins": {"bumper": bumper_plugin}}
        pkg_resources.working_set.add(distribution)
        #for entry_point in pkg_resources.iter_entry_points("hbmqtt.broker.plugins"):
        #   print(entry_point)
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
                        '' #No plugins == no auth
                    ]
                },
                'broker': {
                    'plugins': [
                        'bumper'
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

