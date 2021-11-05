import re

from handlers.handler_items import HandlerItems, BaseHandler
from lib.objects import Message


class MessageProcessor:
    def __init__(self, handler_items: HandlerItems):
        self.handler_items = handler_items

    async def process(self, message: Message) -> bool:
        for item in self.handler_items.items:
            if not issubclass(type(item), BaseHandler):
                continue

            if item.is_regular_expression:
                if re.match(item.pattern, message.message_text, re.IGNORECASE):
                    await item.handle(message)
                    return True

            if message.message_text.lower() == item.pattern:
                await item.handle(message)
                return True

        return False
