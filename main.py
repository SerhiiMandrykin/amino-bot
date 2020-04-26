import logging
import os

from lib.bot import Bot

# Initialize the bot
bot = Bot()

if __name__ == '__main__':
    DIR_LOGS = os.getcwd() + '/logs'

    if not os.path.exists(DIR_LOGS):
        os.mkdir(DIR_LOGS)

    DIR_LEN = len([name for name in os.listdir(DIR_LOGS) if os.path.isfile(os.path.join(DIR_LOGS, name))])

    logging.basicConfig(filename=f"logs/log_{str(DIR_LEN + 1)}.txt", level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%m.%d.%Y %I:%M:%S')
    logging.info('STARTED')
    try:
        bot.run()
    except KeyboardInterrupt:
        print("Бот завершил свою работу")
        logging.info('STOPPED')
        exit()
