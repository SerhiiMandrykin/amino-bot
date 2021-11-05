import json
import os

import telebot

import config


def main():
    if not config.LOG_TO_TELEGRAM:
        print('You need to enable log to telegram in config.py')
        exit()

    if not config.BOT_TOKEN or config.BOT_TOKEN == '':
        print('Please specify the bot token in config.py')
        exit()

    print('Please use command /use_this_chat in the chat where you want to see logs')
    print('The script will automatically save the chat id')

    bot = telebot.TeleBot(config.BOT_TOKEN)

    @bot.message_handler(commands=['use_this_chat'])
    def use_chat(message):
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
        print('Successfully saved')
        print('If you want to change the chat run this script again')
        print('If the script is not stopped - do it manually')
        bot.stop_polling()
        exit()

    bot.polling()


if __name__ == '__main__':
    main()
