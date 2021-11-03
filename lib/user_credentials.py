import json
import os
from typing import NamedTuple


class UserCredentials(NamedTuple):
    login: str
    password: str


class UserCredentialsGetter:
    """
    This class will provide you with user credentials and save it
    """
    def __init__(self):
        self.file_path = os.getcwd() + '/user_credentials.json'

    def file_exists(self) -> bool:
        return os.path.isfile(self.file_path)

    def save_user_credentials(self, login: str, password: str):
        file_content = {
            'login': login,
            'password': password
        }

        with open(self.file_path, 'w') as file:
            file.write(json.dumps(file_content, indent=4))
            file.close()

    def get_user_credentials(self):
        if self.file_exists():
            with open(self.file_path, 'r') as file:
                file_content = json.loads(file.read())
                file.close()

            return UserCredentials(file_content['login'], file_content['password'])

        login = input('Please enter your Amino login: ')
        password = input('Please enter Amino password: ')

        self.save_user_credentials(login, password)

        return UserCredentials(login=login, password=password)
