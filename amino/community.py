from time import time

import json
import requests

from amino.lib.util import exceptions


class Community():
    api = "https://service.narvii.com/api/v1"

    def __init__(self, community_data):
        """
        Build the community
        community_data: json info representing the community to be objectified
        """
        self.api = Community.api
        self.name = community_data["name"]
        self.endpoint = community_data["endpoint"]
        self.url = community_data["link"]
        self.id = community_data["ndcId"]

    @classmethod
    def from_ndcid(cls, ndcid):
        response = requests.get(f"{cls.api}/g/s-x{ndcid}/community/info")

        if response.status_code != 200:
            raise exceptions.UnknownResponse

        return cls(json.loads(response))

    @property
    def member_count(self):
        """
        Param: Get the number of members in this community
        returns the member count for the community
        """
        response = requests.get(f"{self.api}/g/s-x{self.id}/community/info")

        if response.status_code != 200:
            raise exceptions.UnknownResponse

        return json.loads(response.text)["community"]["membersCount"]

    def __repr__(self):
        """
        Represent the community with it's name
        """
        return f"{self.name}"


class Peer():
    api = "https://service.narvii.com/api/v1"

    def __init__(self, user_data, client, community_obj):
        """
        Build the peer.
        user_data: json representing the peer
        client: logged in client or sub_client who the peer belongs to
        community_obj: an object representing the community that the peer is attached to
        """
        self.api = Peer.api
        self.community = community_obj
        self.client = client
        self.uid = user_data["uid"]
        self.nick = user_data["nickname"]
        self._data = user_data

    def __repr__(self):
        """
        Represent the client with it's nickname
        """
        return self.nick

    def set_community_obj(self, community_obj):
        """
        Set a community object after the fact
        """
        self.community = community_obj
        return self

    def get_pm_thread(self):
        """
        Request the pm channel for a peer from amino.
        If there is one (both users have accepted the chat) a Thread is returned
        If there is not one, None is returned
        lazy: the lazy parameter to be passed on to the Thread constructor in the event that a thread exists
        """
        params = {
            "type": "exist-single",
            "cv": "1.2",
            "q": self.uid
        }

        headers = self.client.headers()

        response = requests.get(f"{self.client.api}/x{self.community.id}/s/chat/thread", params=params, headers=headers)

        if response.status_code == 200:
            return ChatThread(json.loads(response.text)["threadList"][0], self.client)

        elif json.loads(response.text).get("api:statuscode", False) == 1600:
            return None

        else:
            raise exceptions.UnknownResponse

    def request_chat(self, message=None):
        """
        Ask a user to open a chat with them.
        message: message to send with the request, or None
        """
        if not self.community:
            raise exceptions.NoCommunity

        data = {
            "type": 0,
            "inviteeUids": [self.uid],
            "timestamp": int(time() * 1000)
        }

        if message:
            data["initialMessageContent"] = message

        data = json.dumps(data)
        headers = self.client.headers(data)

        response = requests.post(f"{self.client.api}/x{self.community.id}/s/chat/thread", data=data, headers=headers)

        if response["api:statuscode"] == 1611:
            raise exceptions.ChatRequestsBlocked

        return response

    def send_text_message(self, message, allow_new=True):
        """
        Send a message to a user.
        message: message to send to the peer
        allow_new: if there is no open thread we will send an open_thread request
        """
        thread = self.get_pm_thread()

        if not thread:
            if allow_new:
                return self.request_chat(message=message)
            raise exceptions.NoChatThread

        return thread.send_text_message(message)

        timestamp = int(time() * 1000)

        data = json.dumps({
            "type": 0,
            "content": message,
            "attachedObject": None,
            "timestamp": timestamp,
            "clientRefId": int(timestamp / 10 % 1000000000)
        })

        headers = self.client.headers(data)

        return requests.post(
            f"{self.client.api}/x{self.community.id}/s/chat/thread/{self.uid}/message",
            data=data,
            headers=headers
        )


class ChatThread():
    def __init__(self, data, client):
        """
        Build the client.
        """
        self.api = "https://service.narvii.com/api/v1"
        self.client = client
        self.uid = data["threadId"]
        self.title = data['title']
        self._community_id = data["ndcId"]
        self._members_data = data["membersSummary"]  # create a Peer object for each item in the list
        self.member_count = len(self._members_data)

    def __repr__(self):
        return self.title

    @property
    def community(self):
        response = requests.get(f"{self.api}/g/s-x{self._community_id}/community/info")

        if response.status_code != 200:
            raise exceptions.UnknownResponse

        response = json.loads(response.text)
        return Community(response["community"])

    @property
    def members(self):
        _members = [Peer(self._members_data[index], self.client, self.community) for index in
                    range(len(self._members_data))]
        return list(filter(lambda x: x.uid != self.client.uid, _members))

    def send_text_message(self, message):
        timestamp = int(time() * 1000)

        data = json.dumps({
            "type": 0,
            "content": message,
            "attachedObject": None,
            "timestamp": timestamp,
            "clientRefId": int(timestamp / 10 % 1000000000)
        })

        headers = self.client.headers(data)

        return requests.post(
            f"{self.client.api}/x{self._community_id}/s/chat/thread/{self.uid}/message",
            data=data,
            headers=headers
        )


class Message:
    """
    Build a message.
    """
    api = "https://service.narvii.com/api/v1"

    def __init__(self, data, client):
        self.client = client
        self.uid = data["chatMessage"]["messageId"]
        self.created = data["chatMessage"]["createdTime"]
        self.content = data["chatMessage"]["content"]

        self._community_id = data["ndcId"]
        self._author = data["chatMessage"]["author"]
        self._thread_id = data["chatMessage"]["threadId"]

    @property
    def community(self):
        return Community.from_ndcid(self._community_id)

    @property
    def author(self):
        return Peer(self._author, client, self.community)

    def mark_as_delivered(self):
        timestamp = int(time() * 1000)

        ws_data = json.dumps({
            "o": {
                "ndcId": self._community_id,
                "threadId": self._thread_id,
                "messageId": self.uid,
                "markHasRead": False,
                "createdTime": self.created,
                "id": str(int(time() % 100000000 / 1.5))
            },
            "t": 1001
        })

        self.client.socket.send(ws_data)

    def mark_as_read(self):
        timestamp = int(time() * 1000)

        ws_data = json.dumps({
            "o": {
                "ndcId": self._community_id,
                "threadId": self._thread_id,
                "messageId": self.uid,
                "markHasRead": True,
                "createdTime": self.created,
                "id": str(int(time() % 100000000 / 1.5))
            },
            "t": 1001
        })

        self.client.socket.send(ws_data)

        data = json.dumps({
            "messageId": self.uid,
            "createdTime": self.created,
            "timestamp": timestamp
        })

        headers = self.client.headers(data)

        result = requests.post(f"{self.api}/x{self._community_id}/s/chat/thread/{self._thread_id}/mark-as-read",
                               headers=headers, data=data)

        return result

    def reply(self, message):
        timestamp = int(time() * 1000)

        data = json.dumps({
            "type": 0,
            "content": message,
            "attachedObject": None,
            "timestamp": timestamp,
            "clientRefId": int(timestamp / 10 % 1000000000)
        })

        headers = self.client.headers(data)

        return requests.post(
            f"{self.client.api}/x{self._community_id}/s/chat/thread/{self._thread_id}/message",
            data=data,
            headers=headers
        )
