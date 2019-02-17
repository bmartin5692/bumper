#!/usr/bin/env python3

from threading import Thread
import socket, logging, ssl, json
import string
import random
import bumper
import time
from datetime import datetime, timedelta
import asyncio
import contextvars
from aiohttp import web
import uuid

class aiohttp_filter(logging.Filter):
    
    def filter(self, record):
        if record.name == "aiohttp.access" and record.levelno == 20:  #Filters aiohttp.access log to switch it from INFO to DEBUG
            record.levelno = 10
            record.levelname = "DEBUG"             
        
        if record.levelno == 10 and logging.getLogger("confserver").getEffectiveLevel() == 10:
            return True
        else:
            return False

confserverlog = logging.getLogger("confserver")

logging.getLogger("asyncio").setLevel(logging.CRITICAL + 1) #Ignore this logger
logging.getLogger("aiohttp.access").addFilter(aiohttp_filter())

class ConfServer():
    bumper_clients = contextvars.ContextVar
    bumper_bots = contextvars.ContextVar

    def __init__(self, address, usessl=False, bumper_users=contextvars.ContextVar, bumper_bots=contextvars.ContextVar, bumper_clients=contextvars.ContextVar, helperbot=None):
        self.bumper_users = bumper_users
        self.bumper_bots = bumper_bots
        self.bumper_clients = bumper_clients    
        self.helperbot = helperbot
        self.usessl = usessl
        self.address = address  
        self.confthread = None

        
    def run(self, run_async=False):
        try:                        
            if run_async:
                confserverlog.debug("Starting ConfServer Thread: 1")
                self.confthread = Thread(name="ConfServer_{}_Thread".format(self.address[1]),target=self.run_server)
                self.confthread.setDaemon(True)
                self.confthread.start()
                
            else:
                try:
                    self.run_server()
                except KeyboardInterrupt:
                    self.disconnect()

        except Exception as e:
            confserverlog.exception('{}'.format(e))


    def run_server(self):
        logging.info("Starting ConfServer at {}".format(self.address))
        print("Starting ConfServer at {}".format(self.address))
        try:
            loop = asyncio.get_event_loop()
        except:
            loop = asyncio.new_event_loop()
        
        try:
            loop.run_until_complete(self.start_server())
            loop.run_forever()
        except Exception as e:
            confserverlog.exception('{}'.format(e))            
                

    async def start_server(self):              
        try:
            app = web.Application()        
            
            app.add_routes([
                web.get('', self.handle_base),
                web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/login', self.handle_login),
                web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/checkLogin', self.handle_login),            
                web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/logout', self.handle_logout),
                web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/getAuthCode', self.handle_getAuthCode),            
                web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/checkAgreement', self.handle_checkAgreement),
                web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/checkVersion', self.handle_checkVersion),
                web.get('/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/campaign/homePageAlert', self.handle_homePageAlert),

                web.post('/api/users/user.do', self.handle_usersapi),
                web.get('/api/users/user.do', self.handle_usersapi),
                web.post('/api/pim/product/getProductIotMap', self.handle_getProductIotMap),
                web.post('/api/iot/devmanager.do', self.handle_devmanager_botcommand),
                
                web.post('/lookup.do', self.handle_lookup),
            ])    
            #Direct register from app:
            #/{apiversion}/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/user/directRegister
            
            

            runner = web.AppRunner(app)
            await runner.setup()
            
            if self.usessl:
                ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ssl_ctx.load_cert_chain(bumper.server_cert,bumper.server_key)
                site = web.TCPSite(runner, host=self.address[0], port=self.address[1],ssl_context=ssl_ctx)
                
            else:    
                site = web.TCPSite(runner, host=self.address[0], port=self.address[1])
        
            await site.start()
        
        except PermissionError as e:
            if "bind" in e.strerror:
                confserverlog.exception("Error binding confserver, exiting. Try using a different hostname or IP - {}".format(e))        
            exit(1)

        except Exception as e:
            confserverlog.exception('{}'.format(e))            
            exit(1)

    async def handle_base(self, request):              
        try:
            
            text = "Bumper!"
                                                
            return web.json_response(text)
        
        except Exception as e:
            confserverlog.exception('{}'.format(e))                          

    async def handle_login(self, request):  
        
        try:
            user_devid = request.match_info.get('devid', "")
            countrycode = request.match_info.get('country', "us")   
            if not user_devid == "": #Performing basic "auth" using devid, super insecure
                users = self.bumper_users.get()                
                for user in users:
                    if user_devid in user.devices:
                        tmpaccesstoken = ''                    
                        if 'checkLogin' in request.path:    
                            if request.query['accessToken'] in user.tokens and request.query['uid'] == "fuid_{}".format(user.userid):
                                tmpaccesstoken = request.query['accessToken']                        
                        else:
                            if tmpaccesstoken == '':
                                tmpaccesstoken = uuid.uuid4().hex
                                user.add_token(tmpaccesstoken)    
                             
                        body = {
                                "code": "0000",
                                "data": {
                                "accessToken": tmpaccesstoken, #Random chars 32 length
                                "country": countrycode,
                                "email": "null@null.com",
                                "uid": "fuid_{}".format(user.userid),
                                "username": "fusername_{}".format(user.userid),
                                },
                                "msg": "操作成功",
                                "time": bumper.get_milli_time(time.time())
                                }  
                        self.bumper_users.set(users)                        
                        return web.json_response(body)
            
            body = {
                    "code": "1005",
                    "data": None,
                    "msg": "当前密码错误",
                    "time": bumper.get_milli_time(time.time())
                    }                          
                                                        
            return web.json_response(body)

        
        except Exception as e:
            confserverlog.exception('{}'.format(e))              


    async def handle_logout(self, request):                      
        try:            
            user_devid = request.match_info.get('devid', "")
            if not user_devid == "":
                users = self.bumper_users.get()
                for user in users:
                    if user_devid in user.devices:
                        if request.query['uid'] == "fuid_{}".format(user.userid) and request.query['accessToken'] in user.tokens:                                       
                            user.revoke_token(request.query['accessToken'])  
                self.bumper_users.set(users)                                                                                                     
            
            body = {"code": "0000","data": None,"msg": "操作成功", "time": bumper.get_milli_time(time.time())}                       
            
            return web.json_response(body)        

        except Exception as e:
            confserverlog.exception('{}'.format(e))              

    async def handle_getAuthCode(self, request):                      
        try:
            
            user_devid = request.match_info.get('devid', "")
            if not user_devid == "":
                users = self.bumper_users.get()
                for user in users:
                    if user_devid in user.devices and request.query['accessToken'] in user.tokens:                                       
                        countrycode = request.match_info.get('country', "us")   
                        tmpauthcode = "{}_{}".format(countrycode,uuid.uuid4().hex)
                        user.add_authcode(tmpauthcode)  
            
                        body = {
                                "code": "0000",
                                "data": {
                                "authCode": tmpauthcode,
                                "ecovacsUid": request.query['uid']
                                },
                                "msg": "操作成功",
                                "time": bumper.get_milli_time(time.time())
                                }         
                        self.bumper_users.set(users)
                        return web.json_response(body)      
        
            body = {
                    "code": "1005",
                    "data": None,
                    "msg": "当前密码错误",
                    "time": bumper.get_milli_time(time.time())
                    }                          
                                                        
            return web.json_response(body)

        except Exception as e:
            confserverlog.exception('{}'.format(e))              

    async def handle_checkVersion(self, request):              
        try:
            body = {
                    "code": "0000",
                    "data": {
                        "c": None,
                        "img": None,
                        "r": 0,
                        "t": None,
                        "u": None,
                        "ut": 0,
                        "v": None
                    },
                    "msg": "操作成功",
                    "time": bumper.get_milli_time(time.time())
                }        
                                                        
            return web.json_response(body)            

        except Exception as e:
            confserverlog.exception('{}'.format(e))              

    async def handle_checkAgreement(self, request):              
        try:
            body = {
                    "code": "0000",
                    "data": [],
                    "msg": "操作成功",
                    "time": bumper.get_milli_time(time.time())
                
                }     
                                                        
            return web.json_response(body)  

        except Exception as e:
            confserverlog.exception('{}'.format(e))              

    async def handle_homePageAlert(self, request):              
        try:
            nextAlert = bumper.get_milli_time((datetime.now() + timedelta(hours=12)).timestamp())
            
            body = {
                    "code": "0000",
                    "data": {
                        "clickSchemeUrl": None,
                        "clickWebUrl": None,
                        "hasCampaign": "N",
                        "imageUrl": None,
                        "nextAlertTime": nextAlert,
                        "serverTime": bumper.get_milli_time(time.time())
                    },
                    "msg": "操作成功",
                    "time": bumper.get_milli_time(time.time())
                }   
                                                    
            return web.json_response(body)          

        except Exception as e:
            confserverlog.exception('{}'.format(e))              

    async def handle_getProductIotMap(self, request):              
        try:
            body = {"code":0,"data":[{"classid":"dl8fht","product":{"_id":"5acb0fa87c295c0001876ecf","name":"DEEBOT 600 Series","icon":"5acc32067c295c0001876eea","UILogicId":"dl8fht","ota":False,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5acc32067c295c0001876eea"}},{"classid":"02uwxm","product":{"_id":"5ae1481e7ccd1a0001e1f69e","name":"DEEBOT OZMO Slim10 Series","icon":"5b1dddc48bc45700014035a1","UILogicId":"02uwxm","ota":False,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b1dddc48bc45700014035a1"}},{"classid":"y79a7u","product":{"_id":"5b04c0227ccd1a0001e1f6a8","name":"DEEBOT OZMO 900","icon":"5b04c0217ccd1a0001e1f6a7","UILogicId":"y79a7u","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b04c0217ccd1a0001e1f6a7"}},{"classid":"jr3pqa","product":{"_id":"5b43077b8bc457000140363e","name":"DEEBOT 711","icon":"5b5ac4cc8d5a56000111e769","UILogicId":"jr3pqa","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4cc8d5a56000111e769"}},{"classid":"uv242z","product":{"_id":"5b5149b4ac0b87000148c128","name":"DEEBOT 710","icon":"5b5ac4e45f21100001882bb9","UILogicId":"uv242z","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5b5ac4e45f21100001882bb9"}},{"classid":"ls1ok3","product":{"_id":"5b6561060506b100015c8868","name":"DEEBOT 900 Series","icon":"5ba4a2cb6c2f120001c32839","UILogicId":"ls1ok3","ota":True,"iconUrl":"https://portal-ww.ecouser.net/api/pim/file/get/5ba4a2cb6c2f120001c32839"}}]}
            return web.json_response(body)  
        
        except Exception as e:
            confserverlog.exception('{}'.format(e))              

    async def handle_usersapi(self, request):    
        try:

            body = {}
            postbody = {}
            if request.content_type == "application/x-www-form-urlencoded":
                postbody = await request.post()
                
            else:
                postbody = json.loads(await request.text())                  
                       
            todo = postbody['todo']
            if todo == 'FindBest':
                service = postbody['service']
                if service == 'EcoMsgNew':
                    body = {"result":"ok","ip":socket.gethostbyname(socket.gethostname()),"port":5223}
                elif service == 'EcoUpdate':
                    body = {"result":"ok","ip":"47.88.66.164","port":8005}
            elif todo == 'loginByItToken':
                            
                users = self.bumper_users.get()
                for user in users:
                    if postbody['userId'] == "fuid_{}".format(user.userid) and postbody['token'] in user.authcodes:                
                        body = {
                            "resource": postbody["resource"],
                            "result": "ok",
                            "todo": "result",
                            "token": postbody["token"], 
                            "userId": postbody["userId"] 
                            }   

            elif todo == 'GetDeviceList':
                active_bots = self.bumper_bots.get()
                body = {
                        "devices": active_bots,
                        "result": "ok",
                        "todo": "result"
                        }            

            elif todo == 'SetDeviceNick':
                bots = self.bumper_bots.get()
                for bot in bots:
                    if postbody['did'] == bot['did']:
                        bot['nick'] = postbody['nick']    
                        self.bumper_bots.set(bots)                        
                        body = {
                            "result": "ok",
                            "todo": "result",
                            }   

            confserverlog.debug("\r\n POST: {} \r\n Response: {}".format(postbody,body))                                                            
            return web.json_response(body)      

        except Exception as e:
            confserverlog.exception('{}'.format(e))    

    async def handle_lookup(self, request):    
        try:

            body = {}
            postbody = {}
            if request.content_type == "application/x-www-form-urlencoded":
                postbody = await request.post()
                
            else:
                postbody = json.loads(await request.text())
                    
            confserverlog.debug(postbody)
            
            todo = postbody['todo']
            if todo == 'FindBest':
                service = postbody['service']
                if service == 'EcoMsgNew':
                    body = {"result":"ok","ip":socket.gethostbyname(socket.gethostname()),"port":5223}
                elif service == 'EcoUpdate':
                    body = {"result":"ok","ip":"47.88.66.164","port":8005}
                              
            confserverlog.debug("\r\n POST: {} \r\n Response: {}".format(postbody,body))                              
            return web.json_response(body)      

        except Exception as e:
            confserverlog.exception('{}'.format(e))                          

    async def handle_devmanager_botcommand(self, request):
        try:
            json_body = json.loads(await request.text())            
            randomid = ''.join(random.sample(string.ascii_letters,6))
            retcmd = await self.helperbot.send_command(json_body, randomid)
            body = retcmd

            confserverlog.debug("\r\n POST: {} \r\n Response: {}".format(json_body,body))            
            return web.json_response(body)   

        except Exception as e:
            confserverlog.exception('{}'.format(e))  

    def disconnect(self):
        try:
            confserverlog.info('shutting down')        
            if(self.run_async):
                self.confthread.join()
            else:
                self.confthread.disconnect()  
    
        except Exception as e:
            confserverlog.exception('{}'.format(e))      