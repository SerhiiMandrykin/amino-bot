from typing import Optional

from lib.objects import Message


class BaseHandler:
    def __init__(self, client_object):
        self.client_object = client_object
        self.message: Optional[Message] = None
        self.pattern = ''
        self.is_regular_expression = False
        self.pattern_variables = []
        self._set_pattern()

    def _set_pattern(self):
        pass

    async def handle(self, message: Message):
        self.message = message

    async def answer(self, answer_text: str):
        await self.client_object.send_message(community_id=self.message.community_id, chat_id=self.message.chat_id,
                                              text=answer_text)
