from lib.bot import Bot

# Initialize the bot
bot = Bot()

if __name__ == '__main__':
    try:
        bot.run()
    except KeyboardInterrupt:
        print("Бот завершил свою работу")
        exit()
