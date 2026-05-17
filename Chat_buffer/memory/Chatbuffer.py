from collections import defaultdict
from memory.schema import ChatMessage


class ChatBuffer:

    def __init__(self, max_messages: int = 10):

        self.max_messages = max_messages

        # {
        #   user_id: [ChatMessage, ChatMessage]
        # }

        self.sessions = defaultdict(list)

    def add_message(
        self,
        user_id: str,
        message: ChatMessage
    ):

        self.sessions[user_id].append(message)

        self.trim_messages(user_id)

    def trim_messages(self, user_id: str):

        messages = self.sessions[user_id]

        if len(messages) > self.max_messages:

            self.sessions[user_id] = messages[-self.max_messages:]

    def get_messages(self, user_id: str):

        return self.sessions[user_id]

    def clear_session(self, user_id: str):

        self.sessions[user_id] = []

    def build_context(self, user_id: str):

        messages = self.get_messages(user_id)

        context = ""

        for msg in messages:

            context += f"{msg.role}: {msg.content}\n"

     
     
     
     
        return context