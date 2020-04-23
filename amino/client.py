import json
from locale import getdefaultlocale as locale
from time import time, timezone

import requests

from amino import community, socket
from amino.lib.util import exceptions, helpers
from amino.lib.util.exceptions import UnknownResponse


class Client():
    def __init__(self, path="device.json", callback=socket.Callbacks, socket_trace=False):
        """
        Build the client.
        path: optional location where the generated device info will be stored
        path is relative to where Client is called from (ie the file in which it's imported) and can be
        """
        try:
            with open(f"{path}", "r") as stream:
                device_info = json.load(stream)

        except (FileNotFoundError, json.decoder.JSONDecodeError):
            device_info = helpers.generate_device_info()
            with open(f"{path}", "w") as stream:
                json.dump(device_info, stream)

        self.api = "https://service.narvii.com/api/v1"
        self.authenticated = False
        self.configured = False
        self.sid = None
        self.nick = "whoami"
        self.user_agent = device_info["user_agent"]
        self.device_id = device_info["device_id"]
        self.device_id_sig = device_info["device_id_sig"]
        self.socket = socket.SocketHandler(self, socket_trace=socket_trace)

        self.callbacks = callback(self)

        self.client_config()

    def login(self, email: str, password: str):
        """
        Send a login request to Amino
        email: email address associated with the account
        password: password associated with the account
        """
        data = json.dumps({
            "email": email,
            "v": 2,
            "secret": f"0 {password}",
            "deviceID": self.device_id,
            "clientType": 100,
            "action": "normal",
            "timestamp": int(time() * 1000)
        })

        headers = self.headers(data=data)
        response = requests.post(f"{self.api}/g/s/auth/login", data=data, headers=headers)

        if response.status_code == 400:
            response = json.loads(response.text)

            if response["api:statuscode"] == 200:
                raise exceptions.FailedLogin

            else:
                raise exceptions.UnknownResponse

        response = json.loads(response.text)
        self.authenticated = True
        self.uid = response["auid"]
        self.secret = response["secret"]
        self.sid = response["sid"]
        self.profile = response["userProfile"]
        self.nick = response["userProfile"]["nickname"]

        self.socket.start()

    def logout(self):
        """
        Send a logout request to amino
        """
        data = json.dumps({
            "deviceID": self.device_id,
            "clinetType": 100,
            "timestamp": int(time() * 1000)
        })

        headers = self.headers(data)

        return requests.post(f"{self.api}/g/s/auth/logout", data=data, headers=headers)

    def __repr__(self):
        """
        Represent the Client by it's nickname
        """
        return self.nick

    def client_config(self):
        """
        Configure the client by sending Amino data about the device id and such.
        sets the class' configured value if the server returns a 200 status_code
        """
        data = json.dumps({
            "deviceID": self.device_id,
            "bundleID": "com.narvii.amino.master",
            "clientType": 100,
            "timezone": -timezone // 1000,
            "systemPushEnabled": True,
            "locale": locale()[0],
            "timestamp": int(time() * 1000)
        })

        headers = self.headers(data)

        response = requests.post(f"{self.api}/g/s/device", headers=headers, data=data)

        if response.status_code == 200:
            self.configured = True

    def headers(self, data=None):
        """
        Macro for generating headers for a request.
        data: string representing what's in the post data of the request we want headers for, or None for a get request
        returns a dict containint generated headers
        """
        headers = {
            "NDCDEVICEID": self.device_id,
            "NDC-MSG-SIG": self.device_id_sig,
            "Accept-Language": "en-US",
            "Content-Type": "application/json; charset=utf-8",
            "User-Agent": self.user_agent,
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "Keep-Alive"
        }

        if data:
            headers["Content-Length"] = str(len(data))

        if self.sid:
            headers["NDCAUTH"] = f"sid={self.sid}"

        return headers

    @property
    def sub_clients(self):
        """
        Generates a dict of SubClients that this client owns.
        returns a dict with endpoint:SubClient objects
        """
        if not self.authenticated:
            raise exceptions.NotLoggedIn

        params = {
            "size": 50,
            "start": 0
        }

        headers = self.headers()
        response = requests.get(f"{self.api}/g/s/community/joined", params=params, headers=headers)

        if response.status_code != 200:
            raise exceptions.UnknownResponse

        response = json.loads(response.text)
        clients = {}

        for data in response["communityList"]:
            profile = response["userInfoInCommunities"][str(data["ndcId"])]["userProfile"]
            clients[data["endpoint"]] = SubClient(profile, self.sid, community.Community(data))

        return clients

    def upload_image_path(self, path, type=None):
        """
        Upload an image that exists on the disk (by propogating the file data to upload_image_raw)
        path: the path to the image, relative to wherever the library was imported from
        type: filetype, defautls to the extension on the image
        Returns the location of the image on amino's servers
        """
        if not type:
            type = path.split('.')[-1]

        raw_image = open(path, "rb").read()
        return self.upload_iamge_raw(raw_image, type=type)

    def upload_image_raw(self, data, type="jpg"):
        """
        Upload raw image data to amino.
        data: raw data of the file
        type: filetype, defaults to jpg
        Returns the location of the image on amono's servers
        """
        headers = self.headers(data)
        headers["Content-Type"] = f"image/{type}"
        response = requests.post(f"{self.api}/g/s/media/upload", data=data, headers=headers)

        if response.status_code != 200:
            raise exceptions.UnknownResponse

        return json.loads(response.text)["mediaValue"]

    def handle_socket_message(self, data):
        return self.callbacks.resolve(data)


class SubClient(Client):
    """
    A representation of a user on an amino.
    This is different than the parent Client, as amino has different account info for each amino that a user has joined
    """

    def __init__(self, user_data, sid, community_obj):
        """
        Build the client.
        user_data: json info with the user info to build the info from
        sid: the client's sid. This is needed for forming any post-login requests (ie all of them)
        community_data: json info representing the community that the client is attached to
        community_obj: an object representing the community that the client is attached to. Takes precedence over community_data
        """
        Client.__init__(self)
        if not community and not community_data:
            raise exceptions.NoCommunity

        self.community = community_obj
        self.uid = user_data["uid"]
        self.nick = user_data["nickname"]
        self.sid = sid

    def peer_search(self, query=None, type="all"):
        """
        Search for peers on this clients amino community.

        query: search search string, or none for an unfiltered search
        type: I don't know, but it's in the api
        """
        headers = self.headers()

        params = {
            "start": 0,
            "size": 25,
            "type": type
        }

        if query:
            params["q"] = query

        response = requests.get(f"{self.api}/x{self.community.id}/s/user-profile", params=params)

        if response.status_code != 200:
            raise exceptions.UnknownResponse

        response = json.loads(response.text)

        return [community.Peer(item, self, community_obj=self.community) for item in response["userProfileList"]]

    def post_blog(self, title, body, *media):
        """
        Create a blog on this client's amino community.
        title: title of the blog
        body: text body of the blog, including replace_strings (see below)
        media: an arbitrary number of MediaItems that will be posted along with the blog
        Will return a post object (or raise an error) when I make one, but for now it returns the request response data
        """
        timestamp = int(time() * 1000)

        if media:
            media_list = []
            for item in media:
                body = body.replace(item.replace_key, f"[IMG={item.replace_key}]")
                media_list.append(item.media_list_item)

        else:
            media_list = None

        data = json.dumps({
            "extensions": {
                "fansOnly": False
            },
            "address": None,
            "content": body,
            "mediaList": media_list,
            "title": title,
            "latitude": 0,
            "longitude": 0,
            "eventSource": "GlobalComposeMenu",
            "timestamp": timestamp
        })

        headers = self.headers(data)

        return requests.post(f"{self.api}/x{self.community.id}/s/blog", headers=headers, data=data)

    def check_in(self):
        data = json.dumps({
            "timezone": -timezone // 1000,
            "timestamp": int(time() * 1000)
        })

        headers = self.headers(data)

        response = requests.post(f"{self.api}/x{self.community.id}/s/check-in", headers=headers, data=data)

        return response

    @property
    def chat_threads(self):
        """
        Get a list of the threads that this client is a part of
        returns a list of Thread objects
        """
        params = {
            "type": "joined-me",
            "start": 0,
        }

        headers = self.headers()

        response = requests.get(f"{self.api}/x{self.community.id}/s/chat/thread", params=params, headers=headers)

        if response.status_code != 200:
            raise UnknownResponse  # placeholder

        response = json.loads(response.text)["threadList"]

        return [community.ChatThread(response[index], self) for index in range(len(response))]

    @property
    def private_chat_threads(self):
        return self.chat_threads()
