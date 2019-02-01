#!/usr/bin/env python3

import logging
import asyncio
import os
import hbmqtt
from hbmqtt.broker import Broker
import pkg_resources
import contextvars
import time
from threading import Thread
import ssl
from paho.mqtt.client import Client as ClientMQTT
from paho.mqtt import publish as MQTTPublish
from paho.mqtt import subscribe as MQTTSubscribe
import bumper
import json
from datetime import datetime, timedelta


class BumperMQTTPlugin:    
    def __init__(self, context):
        self.context = context        
        try:
            self.bots = self.context.config['bots']
        except KeyError:
             self.context.logger.warning("'bots' section not found in context configuration")
            

    async def on_broker_client_connected(self, client_id):
        logging.debug('Bumper Connection: %s connected' % client_id)
        connected_bots = self.bots['connected_bots'].get()                
        didsplit = str(client_id).split("@")
        #If this isn't a fake user (fuid) then add as a bot
        if not (str(didsplit[0]).startswith("fuid") or str(didsplit[0]).startswith("helper")):
            tmpbotdetail = str(didsplit[1]).split("/")        
            newbot = bumper.VacBotDevice()
            newbot.did = didsplit[0]        
            newbot.vac_bot_device_class = tmpbotdetail[0]
            newbot.resource = tmpbotdetail[1]
            botactive = False
            for bot in connected_bots:
                if bot['did'] == newbot.did:
                    botactive = True
            
            if botactive == False:
                connected_bots.append(newbot.asdict())
            
            self.bots['connected_bots'].set(connected_bots)

        logging.debug('Connected Bots: %s' %self.bots['connected_bots'].get())

    async def on_broker_client_disconnected(self, client_id):
        logging.debug('Bumper Connection: %s disconnected' % client_id)
        connected_bots = self.bots['connected_bots'].get()                
        didsplit = str(client_id).split("@")
        #If the did is in the list, remove it
        for bot in connected_bots:
            if didsplit[0] == bot['did']:
                logging.debug("Removing bot from list: {}".format(bot))
                connected_bots.remove(bot)
                self.bots['connected_bots'].set(connected_bots)

        logging.debug('Connected Bots: %s' %self.bots['connected_bots'].get())

class MQTTHelperBot(ClientMQTT):

    def __init__(self, address, run_async=False, bumper_clients=contextvars.ContextVar):
        ClientMQTT.__init__(self)        

        self.address = address
        self._client_id = "helper1@bumper/helper1"
        
        self.command_responses = contextvars.ContextVar('command_responses', default=[])

        try:            
            if run_async: 
                hloop = asyncio.new_event_loop()                
                logging.debug("Starting MQTT HelperBot Thread: 1")
                helperbot = Thread(name="MQTTHelperBot_Thread",target=self.run_helperbot, args=(hloop,))
                helperbot.setDaemon(True)
                helperbot.start()                    
                
            else:
                self.run_helperbot()

        except:
            logging.exception("Exception")
            pass    

    def run_helperbot(self, loop):           
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(self.start_helper_bot())      
        loop.run_forever() 
    
    async def start_helper_bot(self):        
        #self._on_log = self.on_log #This provides more logging than needed, even for debug
        self._on_message = self.get_msg
        self._on_connect = self.on_connect        

        #TODO: This is pretty insecure and accepts any cert, maybe actually check?
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        self.tls_set_context(ssl_ctx)
        self.tls_insecure_set(True)

        self.connect(self.address[0], self.address[1])
        self.loop_start()        
        

    def on_connect(self, client, userdata, flags, rc):        
        if rc != 0:
            logging.error("HelperBot - error connecting with MQTT Return {}".format(rc))
            raise RuntimeError("HelperBot - error connecting with MQTT Return {}".format(rc))
                 
        else:
            logging.debug("HelperBot - Connected with result code "+str(rc))
            logging.debug("HelperBot - Subscribing to all")        

        
            self.subscribe('iot/p2p/+/+/+/+/helper1/bumper/helper1/+/+/+', qos=0)
            self.subscribe('iot/p2p/+', qos=0)
                                                      

    def get_msg(self, client, userdata, message):
        #logging.debug("HelperBot MQTT Received Message on Topic: {} - Message: {}".format(message.topic, str(message.payload.decode("utf-8"))))
        cresp = self.command_responses.get()        
        
        #Cleanup "expired messages" > 60 seconds from time
        for msg in cresp:           
            expire_time = (datetime.fromtimestamp(msg['time']) + timedelta(seconds=10)).timestamp()
            if time.time() > expire_time:
                #logging.debug("Pruning Message Time: {}, MsgTime: {}, MsgTime+60: {}".format(time.time(), msg['time'], expire_time))
                cresp.remove(msg)                                  

        cresp.append({"time": time.time() ,"topic": message.topic,"payload":str(message.payload.decode("utf-8"))})
        self.command_responses.set(cresp)                          
        logging.debug("MQTT Command Response List Count: %s" %len(cresp))

    async def wait_for_resp(self, requestid):               
        t_end = (datetime.now() + timedelta(seconds=10)).timestamp()
        while time.time() < t_end:
            await asyncio.sleep(0.3)
            responses = self.command_responses.get()   
            if len(responses) > 0:    
                for msg in responses:
                    topic = str(msg['topic']).split("/")
                    if (topic[6] == "helper1" and topic[10] == requestid):
                        logging.debug('VacBot MQTT Response: Topic: %s Payload: %s' % (msg['topic'], msg['payload']))
                        if topic[11] == "j":
                            resppayload = json.loads(msg['payload'])
                        else:                            
                            resppayload = str(msg['payload'])
                        resp = {
                            "id": requestid,
                            "ret": "ok",
                            "resp": resppayload
                        }
                        cresp = self.command_responses.get()
                        cresp.remove(msg)                    
                        self.command_responses.set(cresp)                             
                        return resp

        return { "id": requestid, "errno": "timeout", "ret": "fail" }

    async def send_command(self, cmdjson, requestid):
        ttopic = "iot/p2p/{}/helper1/bumper/helper1/{}/{}/{}/q/{}/{}".format(cmdjson["cmdName"],
        cmdjson["toId"], cmdjson["toType"], cmdjson["toRes"], requestid, cmdjson["payloadType"])
        self.publish(ttopic, str(cmdjson["payload"]))

        resp = await self.wait_for_resp(requestid)        
             
        return resp
        

class MQTTServer():    
    default_config = {}  
    bumper_clients = []

    async def broker_coro(self):         
        broker = hbmqtt.broker.Broker(config=self.default_config)        
              
        await broker.start()  

        logging.debug("Removing Plugin: broker_sys")
        broker.plugins_manager.plugins.remove(broker.plugins_manager.get_plugin('broker_sys'))

        logging.debug("Removing Plugin: topic_taboo")
        broker.plugins_manager.plugins.remove(broker.plugins_manager.get_plugin('topic_taboo'))
        
        logging.debug("Removing Plugin: packet_logger_plugin")
        broker.plugins_manager.plugins.remove(broker.plugins_manager.get_plugin('packet_logger_plugin'))

        logging.debug("Started Broker and Removed Plugins")
                

    async def active_bot_listing(self):               
        while True:
            await asyncio.sleep(5)
            logging.debug('Connected bots: %s' % self.bumper_clients.get())     

    def __init__(self, address, run_async=False, bumper_clients=contextvars.ContextVar):
        
        #The below adds a plugin to the hbmqtt.broker.plugins without having to futz with setup.py
        distribution = pkg_resources.Distribution("hbmqtt.broker.plugins")
        bumper_plugin = pkg_resources.EntryPoint.parse('bumper = bumper.mqttserver:BumperMQTTPlugin', dist=distribution)        
        distribution._ep_map = {"hbmqtt.broker.plugins": {"bumper": bumper_plugin}}
        pkg_resources.working_set.add(distribution)
        #for entry_point in pkg_resources.iter_entry_points("hbmqtt.broker.plugins"):
        #   print(entry_point)

        self.bumper_clients = bumper_clients
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
                'topic-check': {
                    'enabled': False
                },
                'bots':{
                    'connected_bots': bumper_clients
                }
            }
            if run_async:
                sloop = asyncio.new_event_loop()                
                logging.debug("Starting MQTTServer Thread: 1")
                mqttserver = Thread(name="MQTTServer_Thread",target=self.run_server, args=(sloop,))
                mqttserver.setDaemon(True)
                mqttserver.start()                   
                
            else:
                self.run_server()

        except:
            logging.exception("Exception")
            pass              
    

    def run_server(self, loop):           
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.broker_coro())
        #loop.run_until_complete(self.active_bot_listing())                     
        loop.run_forever()  

