import config
import telebot
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from dict import dictionary
import functions

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

functions.remove_self_messages(browser)

lastMessageAuthor = "null"
textToUser = "Привет, {}. Ты, наверное, ещё не знаешь, но в нашем сообществе маты запрещены. Пожалуйста, не матерись больше. В ином случае мы будем вынуждены выдать тебе предупреждение, а в случае дальнейшего нарушения - бан."
botText = "Замечен мат в чате!\n\nУчастник: {}\nТекст: {}"

pattern = dictionary.split(',')

tick = 0

delay = 2
checkedMessages = []
iterations_ = 10
checkedMessagesBuffer = 15
while True:
    try:
        time.sleep(2)
        tick += 1

        # Каждую минуту обновлять iframe, так как поток сообщений может залагать
        if tick >= 60 / delay:
            tick = 0
            browser.switch_to.default_content()
            browser.find_element_by_css_selector('div[data-url="' + config.AMINO_CONFIG + '"]').click()
            browser.switch_to.frame(browser.find_element_by_tag_name("iframe"))

        messages = browser.find_elements_by_css_selector('.message-content .text-msg p')
        authors = browser.find_elements_by_css_selector('p.author-name')

        print("Checking...")

        j = 0
        k = -1
        for mess in messages:

            if iterations_ != 0 and j >= iterations_:
                break

            functions.remove_self_messages(browser)

            message = messages[k].text
            author = authors[k].text
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

            if message + author in checkedMessages:
                print("No new messages")
                break

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
                    
            if is_clear == 1:
                print("The message is clear")

            if message.lower().find('бот') != -1 and message.lower().find('позови') != -1 and message.lower().find(
                    'админ') != -1:
                text_ = "Хорошо, {}, сейчас позову администрацию. Надеюсь, это действительно важно..".format(author)
                text__ = "Администрация!\nУчастник {} просит вас зайти в чат.".format(author)

                tI = browser.find_element_by_class_name('text-input')
                tI.click()
                tI.send_keys(text_)

                time.sleep(0.4)

                browser.find_element_by_class_name('send-button').click()

                bot.send_message(config.CHAT_ID, text__)

            if config.enableBotTalking and message.lower().find('бот') != -1:
                message_ = message.lower().replace('бот', '')
                tI = browser.find_element_by_class_name('text-input')
                tI.click()
                tI.send_keys(functions.detect_intent_texts(config.dialogflowProjectId, 'abcde', message_))

                time.sleep(0.2)

                browser.find_element_by_class_name('send-button').click()

            checkedMessages.append(message + author)

            if len(checkedMessages) > checkedMessagesBuffer:
                del checkedMessages[0]

            j += 1
            k += -1
    except Exception:
        pass
