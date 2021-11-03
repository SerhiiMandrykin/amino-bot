import json

import aiohttp

from lib.client_data import ClientData
from lib.devices import Device
from lib.exceptions import *
from lib.headers import Headers
from lib.objects import *


class SubClient:
    """
    Class contains actions inside a specific community
    """

    def __init__(self, communityId=None):
        self.headers = Headers().headers
        self.mobile_headers = Headers().mobile_headers
        self.device = Device().create_device()
        self.interface = "https://aminoapps.com/api"
        self.mobile_interface = "https://service.narvii.com/api/v1"
        self.communityId = communityId
        self.headers["cookie"] = ClientData().data["session"]
        self.mobile_headers["NDCAUTH"] = ClientData().data["session"]
        self.cookies = ClientData().data["session"]

    async def join_chat(self, chat_id):
        data = {
            "ndcId": f"x{self.communityId}",
            "threadId": chat_id
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.interface}/join-thread", json=data, headers=self.headers) as result:
                response = await result.text()
                response = json.loads(response)
                if response["code"] == 200:
                    return response["code"]
                else:
                    raise UnexpectedException(response)

    async def get_my_chats(self, start_offset=0, end_offset=10):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"{self.mobile_interface}/x{self.communityId}/s/chat/thread?type=joined-me&start={start_offset}&size={end_offset}",
                    headers=self.mobile_headers) as result:
                response = await result.json()
                try:
                    response = response["threadList"]
                    chat = Chats(response)
                    return chat
                except:
                    raise UnexpectedException(response)

    async def chatThreadMessages(self, chatId, size=25):
        data = {
            "ndcId": f"x{self.communityId}",
            "threadId": chatId,
            "size": size
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.interface}/chat-thread-messages", json=data,
                                    headers=self.headers) as result:
                response = await result.text()
                response = json.loads(response)
                if response["code"] == 200:
                    return response["result"]
                else:
                    raise UnexpectedException(response)

    async def get_online_users(self, start_offset=0, end_offset=10):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    f"{self.interface}/chat-thread-messages",
                    headers=self.headers) as result:
                response = await result.json()
                try:
                    response = response["userProfileList"]
                    users = User(response)
                    return users
                except:
                    raise UnexpectedException(response)

    async def start_conversation(self, targetId, text):
        data = {
            "ndcId": self.communityId,
            "inviteeUids": targetId,
            "initialMessageContent": text,
            "type": 0
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.interface}/create-chat-thread", json=data, headers=self.headers) as result:
                response = await result.text()
                response = json.loads(response)
                if response["code"] == 200:
                    return response["code"]
                else:
                    if response["api_status_code"] == 270:
                        raise RequestedApproval(response)
                    elif response["api_status_code"] == 603:
                        raise UserBlocked(response["message"])
                    elif response["api_status_code"] == 1611:
                        raise DisabledInviting(response)
                    else:
                        raise UnexpectedException(response)
