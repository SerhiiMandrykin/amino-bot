from handlers.base_handler import BaseHandler
from lib.objects import Message


class UserStatisticHandler(BaseHandler):
    def _set_pattern(self):
        self.pattern = 'стат'

    async def handle(self, message: Message):
        await super().handle(message)
