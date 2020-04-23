from amino.community import Message
from amino.socket import Callbacks
import json


class MessageHandler(Callbacks):
    def __init__(self, client, selected_chats):
        """
        Build the callback handler.
        This is meant to be subclassed, where desided methods would be redefined.
        client: Client to be used
        """
        self.client = client

        self.methods = {
            1000: self._resolve_chat_message
        }

        self.chat_methods = {
            "0:0": self.on_text_message,
            "0:100": self.on_image_message,
            "0:103": self.on_youtube_message,

            "2:110": self.on_voice_message,

            "3:113": self.on_sticker_message,

            "101:0": self.on_group_member_join,
            "102:0": self.on_group_member_leave,
            "103:0": self.on_chat_invite
        }

        self.selected_chats = selected_chats

    def on_text_message(self, data):
        print("Получено новое сообщение")
        # self.message = Message(data, self.client)
        # print(self.message.uid, self.message.content, self.message._author, self.message._thread_id)
