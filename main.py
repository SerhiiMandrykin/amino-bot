import config
import telebot
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

# Не думаю, что нужно объяснять
bot = telebot.TeleBot(config.BOT_TOKEN)

# Я выбрал хром, вы можете выбрать любой другой
browser = webdriver.Chrome(ChromeDriverManager().install())

print("Opening Amino...")

browser.get('https://aminoapps.com')

time.sleep(1)

print("Loading data set...")

# Закрытые окна о cookie
browser.find_element_by_css_selector('.close.pointer').click()

# Кнопка авторизоватся
browser.find_element_by_class_name('nav-user').click()

print("Trying to find a login button")

time.sleep(1.5)

print("The button has been found")

browser.find_element_by_class_name('signin-email').click()

time.sleep(0.3)

print("Authorization...")

mailInput = browser.find_element_by_css_selector('input[name="email"]')
mailInput.click()
mailInput.send_keys(config.LOGIN)

time.sleep(0.8)

passInput = browser.find_element_by_css_selector('input[name="password"]')
passInput.click()
passInput.send_keys(config.PASSWORD)

time.sleep(0.6)

browser.find_element_by_css_selector('button[type="submit"]').click()

time.sleep(6)

print("Successfully logged in")

# Выбор амино
browser.find_element_by_css_selector('div[data-url="' + config.AMINO_CONFIG + '"]').click()

time.sleep(4)

# Переходим к чатам, так как они в iframe, нужно переключится на контент iframe
browser.switch_to.frame(browser.find_element_by_tag_name("iframe"))
# browser.switch_to.default_content() - чтобы вернутся к основному контенту

lastMessageAuthor = "null"
textToUser = "Привет, {}. Ты, наверное, ещё не знаешь, но в нашем сообществе маты запрещены. Пожалуйста, не матерись больше. В ином случае мы будем вынуждены выдать тебе предупреждение, а в случае дальнейшего нарушения - бан."
botText = "Замечен мат в чате!\n\nУчастник: {}\nТекст: {}"

pattern = "бля|сук|дебил|долб|далб|пизд|пздц|пізд|бл*|ебал|хуй|хуя|йоп|йоб|ебан|ху*|еба|ёб|выеб|выёб|хер|блять|фак|наеб|оху|ебен|хуё".split(
    "|")

tick = 0

# 10 итераций - одна секунда
second_tick = 10
while True:
    time.sleep(0.1)
    tick += 1

    # Каждую минуту обновлять iframe, так как поток сообщений может залагать
    if tick == second_tick * 60:
        tick = 0
        browser.switch_to.default_content()
        browser.find_element_by_css_selector('div[data-url="' + config.AMINO_CONFIG + '"]').click()
        browser.switch_to.frame(browser.find_element_by_tag_name("iframe"))

    try:
        messages = browser.find_elements_by_css_selector('.message-content .text-msg p')
        authors = browser.find_elements_by_css_selector('p.author-name')

        print("Checking...")
        message = messages[-1].text
        author = authors[-1].text
        author = author.strip()

        # Убираем эможди с ника, так как не все поддерживаются, может бросить исключение
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   "]+", flags=re.UNICODE)
        author = emoji_pattern.sub(r'', author)

        if not author:
            author = "---"

        if message + author == lastMessageAuthor:
            print("No new messages")
            continue

        is_clear = 1
        for i in range(len(pattern)):
            if message.lower().find(pattern[i]) != -1:
                is_clear = 0
                textToUser_ = textToUser.format(author)
                botText_ = botText.format(author, message)
                bot.send_message(config.CHAT_ID, botText_)

                tI = browser.find_element_by_class_name('text-input')
                tI.click()
                tI.send_keys(textToUser_)

                time.sleep(0.4)

                browser.find_element_by_class_name('send-button').click()
                break

        if is_clear == 1:
            print("The message is clear")

        if message.lower().find('бот') != -1 and message.lower().find('позови') != -1 and message.lower().find('админ') != -1:
            text_ = "Хорошо, {}, сейчас позову администрацию. Надеюсь, это действительно важно..".format(author)
            text__ = "Администрация!\nУчастник {} просит вас зайти в чат.".format(author)

            tI = browser.find_element_by_class_name('text-input')
            tI.click()
            tI.send_keys(text_)

            time.sleep(0.4)

            browser.find_element_by_class_name('send-button').click()

            bot.send_message(config.CHAT_ID, text__)

        lastMessageAuthor = message + author

    except Exception:
        pass
