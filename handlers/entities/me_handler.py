from handlers.base_handler import BaseHandler
from lib.objects import Message


class MeHandler(BaseHandler):
    def _set_pattern(self):
        self.pattern = 'я'

    def needs_reply(self):
        return True

    async def handle(self, message: Message):
        await super().handle(message)

        answer_text = f"Имя: {str(message.author.nickname)}\n" \
                      f"Репутация: {message.author.reputation}\n" \
                      f"Уровень: {message.author.user_level}"

        await self.answer(answer_text)
