import threading

from Conversation import Conversation
from Database import Database
class ConversationManager:
    def __init__(self):
        self.database = Database()
        self.database.connect("localhost",3306,"root","","mekekeke")
        port_number = 1024
        for x in range(1):
            threading.Thread(target=self.new_conversation, args = (port_number,)).start()
            port_number = port_number + 1

    def new_conversation(self, port):
        conversation = Conversation(300, port)
        conversation.on_client_message.append(self.log_message)
        conversation.on_conversation_end.append(self.on_conversation_end)
        self.log_new_conversation(conversation)

    def on_conversation_end(self,reason, conversation):
        self.new_conversation(conversation.port)
        self.log_conversation_end(reason, conversation)

    def log_conversation_end(self,reason, conversation):
        conversation_id = str(conversation.id)
        conversation_end_time = str(conversation.conversation_end_time)
        query = "UPDATE Conversations SET `end_time` = '"+conversation_end_time+"', `end_reason` = '"+reason+"' WHERE conversation_id = '"+conversation_id+"';"
        self.database.insert_query(query)

    def log_new_conversation(self,conversation):
        conversation_id = str(conversation.id)
        conversation_start_time = str(conversation.conversation_start_time)
        user_1_id = str(conversation.client1.local_user.id)
        user_2_id = str(conversation.client2.local_user.id)
        query = "INSERT INTO Conversations (conversation_id, first_user_id, second_user_id, start_time) VALUES ('" + conversation_id + "','" + user_1_id + "','" + user_2_id + "','" + conversation_start_time + "');"
        self.database.insert_query(query)

    def log_message(self,message):
        message_content = str(message.message)
        message_author_id = str(message.author.id)
        message_timestamp = str(message.timestamp)
        query = "INSERT INTO Messages (author_id, timestamp, message) VALUES ('" + message_author_id + "','" + message_timestamp + "','" + message_content + "');"
        self.database.insert_query(query)