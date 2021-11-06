import json
import os


class HandlersData:
    def __init__(self, class_name: str):
        self.file_path = os.getcwd() + '/data/' + class_name + '.json'
        self.data = {}
        self.file = None

        self._check_folder()

        if os.path.isfile(self.file_path):
            self.read_data()
        else:
            self.save_data()

    def _check_folder(self):
        if not os.path.isdir(os.getcwd() + '/data'):
            os.mkdir(os.getcwd() + '/data')

    def read_data(self):
        with open(self.file_path, 'r') as file:
            self.data = json.loads(file.read())
            file.close()

    def save_data(self):
        with open(self.file_path, 'w') as file:
            file.write(json.dumps(self.data, indent=4))
            file.close()

    def __del__(self):
        self.save_data()
