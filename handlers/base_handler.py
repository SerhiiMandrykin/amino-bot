from typing import Optional

from lib.handlers_data import HandlersData
from lib.objects import Message


class BaseHandler:
    def __init__(self, client_object):
        self.client_object = client_object
        self.message: Optional[Message] = None
        self.pattern = ''
        self.is_regular_expression = False
        self.pattern_variables = []
        self._set_pattern()
        self.data_handler = None
        if self._need_data():
            self.data_handler = HandlersData(self.__class__.__name__)

    def _need_data(self) -> bool:
        return False

    def _works_in_chat(self) -> bool:
        return False

    def _set_pattern(self):
        pass

    def needs_reply(self):
        return False

    async def handle(self, message: Message):
        self.message = message

        if self._need_data():
            if message.community_id not in self.data_handler.data.keys():
                self.data_handler.data[message.community_id] = {}

            if self._works_in_chat():
                if message.chat_id not in self.data_handler.data[message.community_id].keys():
                    self.data_handler.data[message.community_id][message.chat_id] = {}

    async def answer(self, answer_text: str, needs_reply=False):
        reply_to = None
        if self.needs_reply() or needs_reply:
            reply_to = self.message.message_id

        await self.client_object.send_message(community_id=self.message.community_id, chat_id=self.message.chat_id,
                                              text=answer_text, reply_to=reply_to)
