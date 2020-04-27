import json
import logging
import os

import telebot

import config


def log(text):
    """
    logging method
    """
    print(text)

    if config.LOG_TO_TELEGRAM:
        bot = telebot.TeleBot(config.BOT_TOKEN)

        with open(os.getcwd() + '/config.json') as config_file:
            current_config = json.loads(config_file.read())
            config_file.close()

        bot.send_message(current_config['chat_id'], text)

    logging.info(text)
