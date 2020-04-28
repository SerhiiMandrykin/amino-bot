import os

import lib.warning as warning
from amino.socket import Callbacks
from lib.logger import log
from lib.obscene import Obscene


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

        with open(os.getcwd() + '/warning.txt', 'r', encoding='UTF-8') as warning_file:
            self.warning_text = warning_file.read()
            warning_file.close()

    def on_text_message(self, data):
        data = data['o']['chatMessage']
        user_id = data['author']['uid']
        user_reputation = data['author']['reputation']
        user_nickname = data['author']['nickname']
        user_level = data['author']['level']
        thread_id = data['threadId']
        message_text = data['content']

        if user_id == self.client.uid:
            return True

        ob = Obscene()

        for i in self.selected_chats:
            if i.uid == thread_id and not ob.is_clear(message_text):
                user_warnings = warning.add(user_id)
                log(f"Пользователь {user_nickname} ({user_warnings}) нарушает правила сообщества в чате {i.title}.")
                i.send_text_message(self.warning_text.replace('{name}', user_nickname).replace('{warnings}', str(user_warnings)))
