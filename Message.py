from datetime import datetime


class Message:
    def __init__(self, author, message, is_remote):
        self.timestamp = datetime.now()
        self.author = author
        self.message = message
        self.is_remote = is_remote
        pass