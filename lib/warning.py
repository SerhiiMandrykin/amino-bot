import json
import os


def add(uid):
    data_file_path = os.getcwd() + '/users_data.json'

    if not os.path.exists(data_file_path):
        with open(data_file_path, 'w', encoding='UTF-8') as data_file:
            data_file.write(json.dumps({}))
            data_file.close()

    with open(data_file_path, 'r', encoding='UTF-8') as data_file:
        users_data = json.loads(data_file.read())
        data_file.close()

    if uid not in users_data:
        users_data[uid] = {'warnings': 1}
    else:
        users_data[uid]['warnings'] += 1

    with open(data_file_path, 'w', encoding='UTF-8') as data_file:
        data_file.write(json.dumps(users_data))
        data_file.close()

    return users_data[uid]['warnings']
