import json
import os

from amino.client import Client
from lib.MessageHandler import MessageHandler


class Bot:
    """
    The main class
    """

    def __init__(self):
        """
        Initializing method
        """

        self.client = Client()

        # Check if config file exists
        if not os.path.exists(os.getcwd() + '/config.json'):
            print("Для начала нужно ввести данные для авторизации")
            self.login = input("Введите ваш логин: ")
            self.password = input("Введите ваш пароль: ")

            with open(os.getcwd() + '/config.json', 'w', encoding='UTF-8') as config_file:
                config_file.write(json.dumps({'login': login, 'password': password}))
                config_file.close()

            print("Файл конфигурации успешно создан")
        else:
            with open(os.getcwd() + '/config.json') as config_file:
                data = json.loads(config_file.read())
                config_file.close()

            self.login = data['login']
            self.password = data['password']

    def run(self):
        self.log_in()
        self.choose_amino()
        self.choose_chats()

        self.client.callbacks = MessageHandler(self.client, self.selected_chats)

    def log_in(self):
        """
        Logging in to an account and choosing amino, chats
        """

        print("Пытаюсь войти в Амино...")
        self.client.login(self.login, self.password)
        if self.client.authenticated:
            print("Авторизация прошла успешно")
        else:
            print("Ошибка авторизации! Проверьте правильно ли вы ввели данные")
            print("Удалите файл config.json для повторного ввода")
            exit()

    def choose_amino(self):
        """
        Choosing an amino to work with
        """

        # Get amino list
        amino_list = []
        c = 1
        aminos = {}
        for i in self.client.sub_clients:
            aminos[c] = i
            print(str(c) + ". " + i)

            c += 1

        self.selected_amino = aminos[int(input("Выберите одно из амино: "))]

        print(f"Вы выбрали {self.selected_amino}")
        print()

    def choose_chats(self):
        """
        Choosing chats of amino to monitor
        """
        self.chats = self.client.sub_clients[self.selected_amino].chat_threads
        c = 0
        for i in self.chats:
            if not i.title:
                continue

            print(str(c) + '. ' + i.title)
            c += 1

        selected_chats = input("Окей, теперь выбери чаты через запятую (например 0,2,3): ").split(',')
        self.selected_chats = []
        for i in selected_chats:
            self.selected_chats.append(self.chats[int(i)])

            print("Начинаю мониторить чат " + self.chats[int(i)].title)
