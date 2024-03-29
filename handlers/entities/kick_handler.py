from handlers.base_handler import BaseHandler
from lib.objects import Message


class KickHandler(BaseHandler):
    REQUESTS_AMOUNT = 3
    TOTAL_AMOUNT = 3

    def _set_pattern(self):
        self.pattern = 'кик'

    def _need_data(self) -> bool:
        return True

    def _works_in_chat(self) -> bool:
        return True

    async def handle(self, message: Message) -> bool:
        await super().handle(message)

        if not message.has_reply:
            answer_text = "Вы должны ответить на сообщение пользователя которого хотите выкинуть из чата."
            await self.answer(answer_text, needs_reply=True)
            return True

        if message.from_id == message.reply_message.from_id:
            answer_text = "Себя кикать нельзя."
            await self.answer(answer_text, needs_reply=True)
            return True

        kick_user = message.reply_message.author.user_id

        if kick_user == self.client_object.self_id:
            await self.answer('Меня нельзя кикать...', needs_reply=True)
            return True

        if not self.client_object.is_curator and not self.client_object.is_leader:
            await self.answer('К сожалению, мне нужны права куратора или лидера чтобы я мог выкинуть из чата.',
                              needs_reply=True)
            return True

        if message.reply_message.author.is_curator or message.reply_message.author.is_leader:
            await self.answer('Я не могу выгнать из чата куратора или лидера.', needs_reply=True)
            return True

        if kick_user not in self.data_handler.data[message.community_id][message.chat_id].keys():
            self.data_handler.data[message.community_id][message.chat_id][kick_user] = {
                'amount': 0,
                'total_amount': 0,
                'reporters': []
            }

        user_data = self.data_handler.data[message.community_id][message.chat_id][kick_user]

        if message.from_id in user_data['reporters']:
            answer_text = f"Вы можете использовать " \
                          f"эту функцию только один раз на один запрос."

            await self.answer(answer_text, needs_reply=True)
            return True

        user_data['amount'] += 1
        user_data['reporters'].append(message.from_id)

        self.data_handler.data[message.community_id][message.chat_id][kick_user] = user_data

        if user_data['amount'] >= self.REQUESTS_AMOUNT:
            user_data['amount'] = 0
            user_data['total_amount'] += 1
            user_data['reporters'] = []
            self.data_handler.data[message.community_id][message.chat_id][kick_user] = user_data
            self.data_handler.save_data()
            await self.client_object.kick(community_id=message.community_id,
                                          user_id=message.reply_message.author.user_id, chat_id=message.chat_id)

            answer_text = f"{str(message.reply_message.author.nickname)} кикнут(а) {user_data['total_amount']}. " \
                          f"После {self.TOTAL_AMOUNT} пользователь будет кикнут без возможности вернуться обратно " \
                          f"в чат."

            await self.client_object.delay_action.wait()

            await self.answer(answer_text)

            return True

        self.data_handler.save_data()

        answer_text = f"{str(message.reply_message.author.nickname)} уже имеет {user_data['amount']} запросов " \
                      f"на кик из чата. Пользователь будет кикнут когда количество запросов будет " \
                      f"равно {self.REQUESTS_AMOUNT}."

        await self.answer(answer_text)
        return True
