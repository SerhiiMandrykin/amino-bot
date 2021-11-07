import json
import random
import string
import time

import aiohttp

from handlers.handler_items import HandlerItems
from lib.client_data import ClientData
from lib.delay_action import DelayAction
from lib.devices import Device
from lib.dialogflow_processor import ChatClient
from lib.exceptions import *
from lib.headers import Headers
from lib.message_processor import MessageProcessor
from lib.objects import *


class ClientObject:
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
        self.handler_items = HandlerItems(self)
        self.message_processor = MessageProcessor(self.handler_items)
        self.is_leader = False
        self.is_curator = False
        self.delay_action = DelayAction()

    def get_captcha(self):
        captcha = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + "_-", k=462)).replace("--",
                                                                                                                 "-")
        return captcha

    async def process_self_status(self):
        result = await self.visit_user(community_id=str(self.allowed_communities[0]), user_id=self.self_id)
        self_role = result['userProfile']['role']

        self.is_leader = self_role in User.LEADER_ROLES
        self.is_curator = self_role in User.CURATOR_ROLES

    async def ping(self, data):
        response = json.loads(data)
        community_id = response['o']['ndcId']

        chat_message = Message.parse_message(response['o']['chatMessage'], str(community_id))
        if chat_message.from_id == self.self_id or community_id not in self.allowed_communities \
                or chat_message.chat_id not in self.allowed_chats:
            return

        chat_message.message_text = chat_message.message_text.strip()
        has_trigger = chat_message.message_text.startswith('!')
        chat_message.message_text = chat_message.message_text.replace('!', '').replace('-', '')

        dialogflow_response = self.chat_client.get_response(chat_message.from_id, chat_message.message_text)

        chat_message.intent = dialogflow_response.intent

        allowed_intents = ['obscene.warning']
        if dialogflow_response.intent not in allowed_intents and not has_trigger:
            return

        await self.delay_action.wait()

        if await self.message_processor.process(chat_message):
            return

        await self.send_message(community_id=community_id, chat_id=chat_message.chat_id,
                                text=dialogflow_response.response_text, reply_to=chat_message.message_id)

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

                if 'api:statuscode' in response['result'].keys() \
                        and int(response['result']['api:statuscode']) in [216, 213, 200]:
                    raise WrongPassword(response["result"]["api:message"])

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

    async def send_message(self, community_id, chat_id, text, message_type=0, reply_to: str = None):
        data = {
            "ndcId": f"x{community_id}",
            "threadId": chat_id,
            "message": {
                "content": text,
                "mediaType": 0,
                "type": message_type,
                "sendFailed": False,
                "clientRefId": 0
            }
        }

        if reply_to is not None:
            data['message']['replyMessageId'] = reply_to

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.interface}/add-chat-message", json=data, headers=self.headers) as result:
                response = await result.text()
                response = json.loads(response)
                if response["code"] == 200:
                    return response["code"]
                else:
                    raise UnexpectedException(response)

    async def kick(self, community_id: str, user_id: str, chat_id: str, allow_rejoin: bool = True):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                    f"{self.mobile_interface}/x{community_id}/s/chat/thread/{chat_id}/member"
                    f"/{user_id}?allowRejoin={str(int(allow_rejoin))}",
                    headers=self.mobile_headers) as result:
                response = await result.json()
                return response

    async def visit_user(self, community_id: str, user_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.mobile_interface}/x{community_id}/s/user-profile/{user_id}?action=visit",
                    headers=self.mobile_headers) as result:
                response = await result.json()

                if 'userProfile' not in response.keys():
                    raise UnexpectedException(response)

                return response

    async def get_chat_thread(self, community_id: str, chat_id: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.mobile_interface}/x{community_id}/s/chat/thread/{chat_id}",
                    headers=self.mobile_headers) as result:
                response = await result.json()

                return response

    async def warn(self, community_id: str, user_id: str, title: str = 'Custom', reason: str = None):
        data = {
            "uid": user_id,
            "title": None,
            "content": None,
            "attachedObject": {
                "objectId": user_id,
                "objectType": 0
            },
            "penaltyType": 0,
            "adminOpNote": {},
            "noticeType": 7,
            "timestamp": int(time.time() * 1000)
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.mobile_interface}/x{community_id}/s/notice", json=data,
                                    headers=self.mobile_headers) as result:
                response = await result.json()
                print(response)
                if response["code"] == 200:
                    return response
                else:
                    raise UnexpectedException(response)
