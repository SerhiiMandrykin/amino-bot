import asyncio

from client import Client
from lib.socket_handler import SocketHandler
from lib.user_credentials import UserCredentialsGetter
from sub_client import SubClient


async def run():
    user_credentials = UserCredentialsGetter().get_user_credentials()

    client_object = Client()
    await client_object.login(user_credentials.login, user_credentials.password)
    coo = await client_object.get_my_communities()

    print("Choose a community to work in (you can choose only one for now): ")
    i = 1
    for item in coo.items:
        print(str(i) + ' - ' + str(item.name))
        i += 1

    coo_id = input('You chose: ')
    if not coo_id or not coo_id.isnumeric():
        print('Please provide a correct value')
        exit()

    coo_id = int(coo_id) - 1

    print('You chose ' + str(coo.items[coo_id].name))

    coo_id = coo.items[coo_id].communityId

    client_object.allowed_communities.append(coo_id)

    print()
    print('Now choose chats to monitor')
    print('You can choose more than one chat')
    print('Please type it one by one')
    print('Type nothing if you are done')

    sub_client = SubClient(coo_id)
    chats = await sub_client.get_my_chats()

    i = 1
    for item in chats.items:
        print(str(i) + ' - ' + str(item.name))
        i += 1

    while True:
        chat_id = input('Your chose: ')
        if not chat_id:
            break

        if not chat_id.isnumeric():
            print('Please enter a valid number')
            continue

        chat_id = int(chat_id) - 1
        print('You added ' + str(chats.items[chat_id].name) + ' to the monitoring list')

        chat_id = chats.items[chat_id].chatId

        client_object.allowed_chats.append(chat_id)

    if client_object.allowed_chats:
        print('Done')
    else:
        print('You chose no chats. Working in a webhook mode.')

    websocket_url = await client_object.get_webhook_url()
    s_h = SocketHandler(client_object, websocket_url)
    s_h.start()


if __name__ == '__main__':
    asyncio.run(run())
