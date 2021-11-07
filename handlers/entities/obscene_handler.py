from handlers.base_handler import BaseHandler
from lib.objects import Message


class ObsceneHandler(BaseHandler):
    TOTAL_AMOUNT = 3

    def _set_pattern(self):
        self.pattern = 'obscene.warning'

    def _need_data(self) -> bool:
        return True

    def _works_in_chat(self) -> bool:
        return True

    def check_intent(self) -> bool:
        return True

    async def handle(self, message: Message) -> bool:
        await super().handle(message)

        if not self.client_object.is_curator and not self.client_object.is_leader:
            return False

        if message.author.is_curator or message.author.is_leader:
            return False

        user_id = message.from_id

        if user_id not in self.data_handler.data[message.community_id][message.chat_id].keys():
            self.data_handler.data[message.community_id][message.chat_id][user_id] = {
                'amount': 0,
            }

        user_data = self.data_handler.data[message.community_id][message.chat_id][user_id]

        user_data['amount'] += 1

        self.data_handler.data[message.community_id][message.chat_id][user_id] = user_data

        if user_data['amount'] >= self.TOTAL_AMOUNT:
            user_data['amount'] = 0
            self.data_handler.data[message.community_id][message.chat_id][user_id] = user_data
            self.data_handler.save_data()

            await self.client_object.kick(community_id=message.community_id,
                                          user_id=message.from_id, chat_id=message.chat_id)

            await self.client_object.delay_action.wait()

            await self.answer('Да будет кикнут этот злостный нарушитель')

            return True

        self.data_handler.save_data()

        return False
