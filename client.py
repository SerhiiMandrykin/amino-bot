import asyncio
import json
import random
import string
import time

import aiohttp

from lib.client_data import ClientData
from lib.devices import Device
from lib.dialogflow_processor import ChatClient
from lib.exceptions import *
from lib.headers import Headers
from lib.objects import *


class Client:
    """
    Global class that does authorizations
    """

    def __init__(self):
        self.headers = Headers().headers
        self.mobile_headers = Headers().mobile_headers
        self.device = Device().create_device()
        self.interface = "https://aminoapps.com/api"
        self.mobile_interface = "https://service.narvii.com/api/v1"
        self.self_id = None
        self.allowed_chats = []
        self.allowed_communities = []
        self.chat_client = ChatClient('bts-amino-umty')
        self.time_delay = 5  # delay in seconds for sending messages
        self.last_action_time = 0

    def get_captcha(self):
        captcha = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + "_-", k=462)).replace("--",
                                                                                                                 "-")
        return captcha

    async def ping(self, data):
        """
        TODO: move message handling to a separate class
        """
        response = json.loads(data)
        community_id = response['o']['ndcId']

        chat_message = Message.parse_message(response['o']['chatMessage'])
        if chat_message.from_id == self.self_id or community_id not in self.allowed_communities \
                or chat_message.chat_id not in self.allowed_chats:
            return

        chat_message.message_text = chat_message.message_text.strip()
        has_trigger = chat_message.message_text.startswith('!')
        chat_message.message_text = chat_message.message_text.replace('!', '').replace('-', '')

        dialogflow_response = self.chat_client.get_response(chat_message.from_id, chat_message.message_text)

        allowed_intents = ['obscene.warning']
        if dialogflow_response.intent not in allowed_intents and not has_trigger:
            return

        time_diff = time.time() - self.last_action_time
        print('Time diff is ' + str(int(time_diff)) + ' seconds')
        if time_diff < self.time_delay:
            print('Waiting for ' + str(self.time_delay - time_diff) + ' seconds')
            await asyncio.sleep(self.time_delay - time_diff)

        self.last_action_time = time.time()

        await self.send_message(community_id=community_id, room_id=chat_message.chat_id,
                                text=dialogflow_response.response_text)

    async def login(self, email, password):
        data = {
            "auth_type": 0,
            "email": email,
            "recaptcha_challenge": self.get_captcha(),
            "recaptcha_version": "v3",
            "secret": password
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.interface}/auth", json=data) as result:
                response = await result.text()
                response = json.loads(response)
                try:
                    self.name = response["result"]["nickname"]
                    self.cookies = result.headers["set-cookie"]
                    self.cookies = self.cookies[0: self.cookies.index(";")]
                    self.self_id = response["result"]["uid"]
                    self.headers["cookie"] = self.cookies
                    self.headers["cookie"] = self.cookies
                    self.mobile_headers["NDCAUTH"] = self.cookies
                    ClientData().data["session"] = self.cookies
                    ClientData().data["name"] = self.name
                    self.loggedIn = True
                except:
                    try:
                        if response["result"][
                            "api:message"] == "Account or password is incorrect! If you forget your password, please " \
                                              "reset it.":
                            raise WrongPassword(response["result"]["api:message"])
                        elif response["result"]["api:message"] == "Invalid email address.":
                            raise WrongEmail(response["result"]["api:message"])
                    except KeyError:
                        raise UnexpectedException(response)

    async def login_to_community(self, communityId):
        data = {
            "ndcId": communityId
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.interface}/join", json=data, headers=self.headers) as result:
                response = await result.text()
                response = json.loads(response)
                if response["code"] == 200:
                    return response["code"]
                else:
                    raise UnexpectedException(response)

    async def get_my_communities(self, start_offset=0, end_offset=10):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.mobile_interface}/g/s/community/joined?v=1&start={start_offset}&size={end_offset}",
                    headers=self.mobile_headers) as result:
                response = await result.json()
                try:
                    response = response["communityList"]
                    communities = Communities(response)
                    return communities
                except:
                    raise UnexpectedException(response)

    async def get_webhook_url(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.interface}/chat/web-socket-url",
                    headers=self.headers) as result:
                response = await result.json()
                try:
                    if response['code'] != 200:
                        raise UnexpectedException(response)

                    return response['result']['url']
                except:
                    raise UnexpectedException(response)

    async def send_message(self, community_id, room_id, text, message_type=0):
        data = {
            "ndcId": f"x{community_id}",
            "threadId": room_id,
            "message": {
                "content": text,
                "mediaType": 0,
                "type": message_type,
                "sendFailed": False,
                "clientRefId": 0
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.interface}/add-chat-message", json=data, headers=self.headers) as result:
                response = await result.text()
                response = json.loads(response)
                if response["code"] == 200:
                    return response["code"]
                else:
                    raise UnexpectedException(response)
