import asyncio
import json
from threading import Thread

import websockets

from Event import Event
from Message import Message
from User import User


class Client:
    def __init__(self, loop):
        self.connection_id = None
        self.loop= loop
        self.hash = None
        self.websocket = None
        self.location_id = 0
        self.ceid = 1
        self.idn = None
        self.ckey = None
        self.cid = None
        self.recieve_loop = None
        self.local_user = User()
        self.remote_user = None
        self.is_started = True
        self.on_message_event = Event()
        self.on_disconnect_event = Event()
        self.on_conversation_start_event = Event()
        self.on_is_typing_event = Event()


        a = 3

    def start_client(self):
        self.loop.run_until_complete(self.connect())



    async def connect(self):
        port = 7002

        uri = "ws://server.6obcy.pl:" + str(port) + "/echoup/websocket"
        async with websockets.connect(uri, ssl=None) as websocket:
            self.websocket = websocket
            while self.is_started:
                message = await websocket.recv()
                await self.on_message(message)



    async def on_message(self, message):
        message = json.loads(message)
        event_name = message['ev_name']
        if event_name == 'cn_acc':
            await self.on_connect(message)
        elif event_name == 'piwo':
            await self.send_pong_message()
        elif event_name == 'rmsg':
            await  self.on_conversation_user_message(message)
        elif event_name == 'styp':
            await self.on_conversation_user_typing(message)
        elif event_name == 'sdis':
            await self.on_conversation_user_disconnected()
        elif event_name == 'talk_s':
            await self.on_conversation_start(message)
        elif event_name == '_distalk':
            await self.on_conversation_user_disconnected()



    async def on_connect(self, message):
        ev_data = message['ev_data']
        self.connection_id = ev_data['conn_id']
        self.hash = ev_data['hash']
        await self.send_connection_info_message()
        await self.send_accept_connection_message()
        await self.send_start_conversation_message()


    async def on_conversation_start(self, message):
        self.ckey = message['ev_data']['ckey']
        self.cid = message['ev_data']['cid']
        self.on_conversation_start_event()
        await self.send_begin_conversation_message()

    async def on_conversation_user_disconnected(self):
        print('disconnected')
        self.on_disconnect_event(self)

    async def on_conversation_user_message(self, message):
        message = message['ev_data']['msg']
        message = Message( self.local_user,message, False)
        await asyncio.sleep(1)
        self.on_message_event(message)
        pass

    async def on_conversation_user_typing(self, message):
        is_typing = message['ev_data']
        self.on_is_typing_event(self.local_user.id, is_typing)
        pass

    def send_typing_message(self, state):
        message = None
        if self.ckey is not None:
            message = '{"ev_name":"_mtyp","ev_data":{"ckey":0, "val": '+ str(state).lower() +'}}';
        else:
            message = '{"ev_name":"_mtyp","ev_data":{"ckey":"'+ str(self.ckey) +'", "val":'+ state.lower() +'}}';
        self.loop.create_task(self.send_message(message))

    async def send_connection_info_message(self):
        message = '{"ev_name":"_cinfo","ev_data":{"mobile":true,"cver":"v2.5","adf":"ajaxPHP","hash":"' + self.hash + '","testdata":{"ckey":0,"recevsent":false}}}'
        await self.send_message(message)

    async def send_accept_connection_message(self):
        message = '{"ev_name":"_owack"}'
        await self.send_message(message)

    async def send_begin_conversation_message(self):
        message = '{"ev_name":"_begacked","ev_data":{"ckey":"'+ str(self.ckey) +'"},"ceid":'+ str(self.ceid) +'}'
        self.ceid = self.ceid + 1
        await self.send_message(message)

    async def send_pong_message(self):
        message = '{ "ev_name": "_gdzie" }'
        await self.send_message(message)

    async def send_start_conversation_message(self):
        message = '{"ev_name":"_sas","ev_data":{"channel":"main","myself":{"sex":0,"loc":' + str(self.location_id) + '},"preferences":{"sex":0,"loc":' + str(self.location_id)+ '}},"ceid":' + str(self.ceid) + '}'
        self.ceid = self.ceid + 1
        await self.send_message(message)



    def compose_message(self, message_content):
        message = None
        if self.idn is not None:
            message = '{"ev_name":"_pmsg","ev_data":{"ckey":"'+ str(self.ckey) +'", "msg":"'+str(message_content)+'", "idn":0},"ceid":'+ str(self.ceid) +'}'
            self.idn = 0
        else:
            message = '{"ev_name":"_pmsg","ev_data":{"ckey":"'+ str(self.ckey) +'", "msg":"'+str(message_content)+'", "idn":'+ str(self.idn) +'},"ceid":'+ str(self.ceid) +'}'
        self.ceid = self.ceid +1
        self.loop.create_task(self.send_message(message))

    async def send_message(self,message):
        await self.websocket.send(message)

    def end_conversation(self):
        self.is_started = False
        self.loop.create_task(self.websocket.close())