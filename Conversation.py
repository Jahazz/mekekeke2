import asyncio
import threading
import uuid
from datetime import datetime

from Client import Client
from threading import Thread
from multiprocessing.pool import ThreadPool
import sched, time
from Event import Event


class Conversation:
    def __init__(self, conversation_timeout, port):
        pool = ThreadPool(processes=2)

        self.port = port
        self.conversation_timeout = conversation_timeout
        self.id = uuid.uuid4()
        self.on_client_message = Event()
        self.on_conversation_end = Event()
        self.client1 = None
        self.client2 = None
        self.setup_clients()
        self.client1.remote_user = self.client2.local_user
        self.client2.remote_user = self.client1.local_user
        self.is_conversation_running = True
        self.conversation_start_time = datetime.now()
        self.conversation_end_time = None
        self.last_message_time = time.time()
        threading.Timer(1.0, self.check_timeout).start()

    def check_timeout(self):
        if time.time() - self.last_message_time >= self.conversation_timeout:
            self.end_conversation("timeout")
        if self.is_conversation_running:
            threading.Timer(1.0, self.check_timeout).start()

    def send_message_from_console(self):
        message = input()
        self.client1.send_message(message)
        self.client2.send_message(message)
        self.send_message_from_console()

    def setup_clients(self):
        self.client1 = self.setup_client()
        self.client2 = self.setup_client()
        Thread(target=self.client1.start_client).start()
        Thread(target=self.client2.start_client).start()

    def setup_client(self):
        client = Client(asyncio.new_event_loop())
        client.on_message_event.append(self.on_message)
        client.on_disconnect_event.append(self.on_disconnect)
        client.on_conversation_start_event.append(self.on_conversation_start)
        client.on_is_typing_event.append(self.on_is_typing)
        return client

    def on_conversation_start(self):
        if self.client1.cid is not None and self.client2.cid is not  None:
            print("conversation_start")
            if self.client1.cid == self.client2.cid:
                self.end_conversation("Same conversation")

    def on_message(self, message):
        if not message.is_remote:
            print(str(message.author.id)+":"+message.message)
            self.on_client_message(message)
            if message.author.id == self.client1.local_user.id:
                self.client2.compose_message(message.message)
            else:
                self.client1.compose_message(message.message)
            self.last_message_time = time.time()

    def on_is_typing(self, author_id, state):
        if author_id == self.client1.local_user.id:
            self.client2.send_typing_message(state)
        else:
            self.client1.send_typing_message(state)


    def on_disconnect(self, client):
        self.end_conversation("Ended by "+str(client.local_user.id))

    def end_conversation(self, reason):
        self.is_conversation_running = False
        self.client1.end_conversation()
        self.client2.end_conversation()
        self.conversation_end_time = datetime.now()
        self.on_conversation_end(reason, self)
