#!/usr/bin/env python3

import logging
import asyncio
import os
from hbmqtt.broker import Broker
import hbmqtt

default_config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '0.0.0.0:1883',
        },
        'tls1': {
            'bind': '0.0.0.0:8883',
            'ssl': 'on',
            #'cafile': '/some/cafile',
            #'capath': '/some/folder',
            #'capath': 'certificate data',
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

class BaseAuthPlugin:
    def __init__(self, context):
        self.context = context
        try:
            self.auth_config = self.context.config['auth']
        except KeyError:
            self.context.logger.warning("'auth' section not found in context configuration")

    def authenticate(self, *args, **kwargs):
        if not self.auth_config:
            # auth config section not found
            self.context.logger.warning("'auth' section not found in context configuration")
            return False
        return True

class VacBotAuth(BaseAuthPlugin):
    def __init__(self, context):
        super().__init__(context)

    @asyncio.coroutine
    def authenticate(self, *args, **kwargs):
        authenticated = super().authenticate(*args, **kwargs)
        if authenticated:
            allow_anonymous = self.auth_config.get('allow-anonymous', True)  # allow anonymous by default
            if allow_anonymous:
                authenticated = True
                self.context.logger.debug("Authentication success: config allows anonymous")
            else:
                try:
                    session = kwargs.get('session', None)
                    authenticated = True if session.username else False
                    if self.context.logger.isEnabledFor(logging.DEBUG):
                        if authenticated:
                            self.context.logger.debug("Authentication success: session has a non empty username")
                        else:
                            self.context.logger.debug("Authentication failure: session has an empty username")
                except KeyError:
                    self.context.logger.warning("Session informations not available")
                    authenticated = False
        return authenticated

@asyncio.coroutine
def broker_coro():    
    broker = hbmqtt.broker.Broker(config=default_config, plugin_namespace=".")
    
    print(broker.plugins_manager)
    yield from broker.start()


if __name__ == '__main__':
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=formatter)
    eloop = asyncio.get_event_loop().run_until_complete(broker_coro())
    
    asyncio.get_event_loop().run_forever()