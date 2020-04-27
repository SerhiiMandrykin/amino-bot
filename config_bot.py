import json
import os

import telebot

import config


def main():
    if not config.LOG_TO_TELEGRAM:
        print('Чтобы использовать телеграм бота вам необходимо включить лог в телеграм в файле config.py')
        exit()

    if not config.BOT_TOKEN or config.BOT_TOKEN == '':
        print('Для начала укажите токен телеграм бота в файле config.py')
        exit()

    print('Чтобы настроить чат, в который бот будет посылать логи, добавьте бота в этот чат')
    print('Это так же может быть и лс')
    print('После этого отправте в нужном чате текст /use_this_chat')
    print('Скрипт автоматически сохранит ID чата')

    bot = telebot.TeleBot(config.BOT_TOKEN)

    @bot.message_handler(commands=['use_this_chat'])
    def use_chat(message):
        bot_config = {'chat_id': message.chat.id}

        with open(os.getcwd() + '/config.json', 'r') as config_file:
            current_config = json.loads(config_file.read())
            current_config['chat_id'] = message.chat.id
            config_file.close()

        with open(os.getcwd() + '/config.json', 'w') as config_file:
            config_file.write(json.dumps(current_config))
            config_file.close()

        bot.send_message(message.chat.id, 'Чат успешно сохранен')

        print()
        print('-----------------------')
        print()
        print('Настройки успешно сохранены')
        print('Если захотите изменить чат, заново запустите этот скрипт')
        print('Если скрипт не остановился - сделайте это вручную )')
        bot.stop_polling()
        exit()

    bot.polling()


if __name__ == '__main__':
    main()
