#!/usr/bin/env python3

import logging
import asyncio
import os
import hbmqtt
from hbmqtt.broker import Broker
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_0, QOS_1, QOS_2
import pkg_resources
import contextvars
import time
from threading import Thread
import ssl
import bumper
import json
from datetime import datetime, timedelta


class MQTTHelperBot():
    Client = MQTTClient()
    def __init__(self, address, run_async=False, bumper_bots=contextvars.ContextVar, bumper_clients=contextvars.ContextVar):
        
        self.address = address
        self.client_id = "helper1@bumper/helper1"       
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

        except Exception as e:
            logging.error('Helperbot: {}'.format(e))
            pass    

    def run_helperbot(self, loop):     
        try:
            asyncio.set_event_loop(loop)                
            self.Client = MQTTClient(client_id=self.client_id, config={'check_hostname':False})      
            loop.run_until_complete(self.start_helper_bot())    
            loop.run_until_complete(self.get_msg()) 
            loop.run_forever() 
        except Exception as e:
            logging.error('Helperbot: {}'.format(e))            
    
    async def start_helper_bot(self):        

        try:
            await self.Client.connect('mqtts://{}:{}/'.format(self.address[0], self.address[1]), cafile=bumper.ca_cert)
            await self.Client.subscribe([
                ('iot/p2p/+/+/+/+/helper1/bumper/helper1/+/+/+',QOS_0),
                ('iot/p2p/+',QOS_0)                
            ])    

        except Exception as e:
            logging.error('Helperbot: {}'.format(e))            
        #except hbmqtt.client.ClientException as ce:
        #    logging.exception("Client exception: %s" % ce)


    async def get_msg(self):
        try:
            while True:
                message = await self.Client.deliver_message()          
            
                #logging.debug("HelperBot MQTT Received Message on Topic: {} - Message: {}".format(message.topic, str(message.payload.decode("utf-8"))))
                cresp = self.command_responses.get()        
                
                #Cleanup "expired messages" > 60 seconds from time
                for msg in cresp:           
                    expire_time = (datetime.fromtimestamp(msg['time']) + timedelta(seconds=10)).timestamp()
                    if time.time() > expire_time:
                        #logging.debug("Pruning Message Time: {}, MsgTime: {}, MsgTime+60: {}".format(time.time(), msg['time'], expire_time))
                        cresp.remove(msg)                                  

                cresp.append({"time": time.time() ,"topic": message.topic,"payload":str(message.data.decode("utf-8"))})
                self.command_responses.set(cresp)                          
                logging.debug("MQTT Command Response List Count: %s" %len(cresp))
        
        except Exception as e:
            logging.error('Helperbot: {}'.format(e))        
        #except hbmqtt.client.ClientException as ce:
        #    logging.error("Client exception: %s" % ce)
   

    async def wait_for_resp(self, requestid):               
        try:
            t_end = (datetime.now() + timedelta(seconds=10)).timestamp()
            while time.time() < t_end:
                await asyncio.sleep(0.1)
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
        
        except Exception as e:
            logging.error('Helperbot: {}'.format(e))            

    async def send_command(self, cmdjson, requestid):
        try:
            ttopic = "iot/p2p/{}/helper1/bumper/helper1/{}/{}/{}/q/{}/{}".format(cmdjson["cmdName"],
                cmdjson["toId"], cmdjson["toType"], cmdjson["toRes"], requestid, cmdjson["payloadType"])
            try:                
                await self.Client.publish(ttopic, str(cmdjson["payload"]).encode(),QOS_0)
            except:
                logging.exception("Exception at send_command")
            
            resp = await self.wait_for_resp(requestid)        
                    
            return resp        

        except Exception as e:
            logging.error('Helperbot: {}'.format(e))
        

class MQTTServer():    
    default_config = {}  
    bumper_clients = []
    bumper_bots = []

    async def broker_coro(self):        
        try: 
            broker = hbmqtt.broker.Broker(config=self.default_config)
            await broker.start()                
        
        except PermissionError as e:
            if "bind" in e.strerror:
                logging.exception("Error binding mqttserver, exiting. Try using a different hostname or IP.\r\n {}".format(e))        
            exit(1)  

        except Exception as e:
            logging.exception('MQTTServer: {}'.format(e))
            exit(1)

    async def active_bot_listing(self):        
        try:       
            while True:
                await asyncio.sleep(5)
                logging.debug('Connected bots: %s' % self.bumper_bots.get())     

        except Exception as e:
            logging.error('MQTTServer: {}'.format(e))                

    def __init__(self, address, run_async=False, bumper_bots=contextvars.ContextVar, bumper_clients=contextvars.ContextVar):
        try:
            #The below adds a plugin to the hbmqtt.broker.plugins without having to futz with setup.py
            distribution = pkg_resources.Distribution("hbmqtt.broker.plugins")
            bumper_plugin = pkg_resources.EntryPoint.parse('bumper = bumper.mqttserver:BumperMQTTServer_Plugin', dist=distribution)        
            distribution._ep_map = {"hbmqtt.broker.plugins": {"bumper": bumper_plugin}}
            pkg_resources.working_set.add(distribution)
            self.bumper_bots = bumper_bots
            self.bumper_clients = bumper_clients        
            # Initialize bot server
            self.default_config = {
                'listeners': {
                    'default': {
                        'type': 'tcp',
                    },
                    'tls1': {
                        'bind': "{}:{}".format(address[0], address[1]),
                        'ssl': 'on',
                        'certfile': bumper.server_cert,
                        'keyfile': bumper.server_key,
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
                'clients':{
                    'connected_bots': bumper_bots,
                    'connected_clients': bumper_clients

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
        
        except Exception as e:
            logging.error('MQTTServer: {}'.format(e))

        #except:
        #    logging.exception("Exception")
        #    pass              
    

    def run_server(self, loop):      
        try:     
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.broker_coro())
            #loop.run_until_complete(self.active_bot_listing())                     
            loop.run_forever()  
        
        except Exception as e:
            logging.error('MQTTServer: {}'.format(e))            

class BumperMQTTServer_Plugin:    
    def __init__(self, context):
        self.context = context        
        try:            
            self.clients = self.context.config['clients']
        except KeyError:
             self.context.logger.warning("'clients' section not found in context configuration")
        except Exception as e:
            logging.error('MQTTServer: {}'.format(e))    

    async def on_broker_client_connected(self, client_id):
        try:
            logging.debug('Bumper Connection: %s connected' % client_id)
            connected_bots = self.clients['connected_bots'].get()      
            connected_clients = self.clients['connected_clients'].get()          
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
                    logging.info("Adding bot to list: {}".format(newbot.asdict()))
                
                self.clients['connected_bots'].set(connected_bots)
            else:
                tmpuserdetail = str(didsplit[1]).split("/")    
                newuser = bumper.VacBotUser()
                newuser.userid = didsplit[0]        
                newuser.realm = tmpuserdetail[0]        
                newuser.resource = tmpuserdetail[1]
                
                clientactive = False
                for client in connected_clients:
                    if client['userid'] == newuser.userid:
                        clientactive = True
                
                if clientactive == False:
                    connected_clients.append(newuser.asdict())
                    logging.info("Adding client to list: {}".format(newuser.asdict()))
                
                self.clients['connected_clients'].set(connected_clients)


            logging.debug('Connected Bots: %s' %self.clients['connected_bots'].get())
            logging.debug('Connected Clients: %s' %self.clients['connected_clients'].get())

        except Exception as e:
            logging.error('MQTTServer: {}'.format(e))            
        


    async def on_broker_client_disconnected(self, client_id):
        try:
            logging.debug('Bumper Connection: %s disconnected' % client_id)
            connected_bots = self.clients['connected_bots'].get()       
            connected_clients = self.clients['connected_clients'].get()               
            didsplit = str(client_id).split("@")
            #If the did is in the list, remove it
            for bot in connected_bots:
                if didsplit[0] == bot['did']:
                    logging.info("Removing bot from list: {}".format(bot['did']))
                    connected_bots.remove(bot)
                    self.clients['connected_bots'].set(connected_bots)

            logging.debug('Connected Bots: %s' %self.clients['connected_bots'].get())

            for client in connected_clients:
                if didsplit[0] == client['userid']:
                    logging.info("Removing client from list: {}".format(client['userid']))
                    connected_clients.remove(client)
                    self.clients['connected_clients'].set(connected_clients)

            logging.debug('Connected Clients: %s' %self.clients['connected_clients'].get())

        except Exception as e:
            logging.error('MQTTServer: {}'.format(e))