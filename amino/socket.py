import json
import threading
import time
import websocket


class SocketHandler():
    def __init__(self, client, socket_trace=False):
        """
        Build the websocket connection.
        client: client that owns the websocket connection.
        """
        websocket.enableTrace(True)
        self.socket_url = "wss://ws1.narvii.com"
        self.client = client
        self.active = False
        self.headers = None
        self.socket = None
        self.socket_thread = None

        websocket.enableTrace(socket_trace)

    def on_open(self):
        pass

    def on_close(self):
        self.active = False

        if self.reconnect:
            self.start()
            print("reopened")

        print("closed")

    def on_ping(self, data):
        self.socket.sock.pong(data)

    def handle_message(self, data):
        self.client.handle_socket_message(data)
        return

    def send(self, data):
        self.socket.send(data)

    def start(self):
        self.headers = {
            "NDCDEVICEID": self.client.device_id,
            "NDCAUTH": f"sid={self.client.sid}"
        }

        self.socket = websocket.WebSocketApp(
            f"{self.socket_url}/?signbody={self.client.device_id}%7C{int(time.time() * 1000)}",
            on_message=self.handle_message,
            on_open=self.on_open,
            on_close=self.on_close,
            on_ping=self.on_ping,
            header=self.headers
        )

        self.socket_thread = threading.Thread(target=self.socket.run_forever, kwargs={"ping_interval": 60})
        self.socket_thread.start()
        self.active = True

    def close(self):
        self.reconnect = False
        self.active = False
        self.socket.close()


class Callbacks:
    def __init__(self, client):
        """
        Build the callback handler.
        This is meant to be subclassed, where desided methods would be redefined.
        client: Client to be used
        """
        self.client = client

        self.methods = {
            1000: self._resolve_chat_message
        }

        self.chat_methods = {
            "0:0": self.on_text_message,
            "0:100": self.on_image_message,
            "0:103": self.on_youtube_message,

            "2:110": self.on_voice_message,

            "3:113": self.on_sticker_message,

            "101:0": self.on_group_member_join,
            "102:0": self.on_group_member_leave,
            "103:0": self.on_chat_invite
        }

    def _resolve_chat_message(self, data):
        """
        Resolves to a chat method based on the data's `chatMessage > type`  and `chatMessage > mediaType` parameter.
        if there is no `mediaType`, then the default fallback value `0` will be used
        returns the return value of the appropriate method
        """

        key = f"{data['o']['chatMessage']['type']}:{data['o']['chatMessage'].get('mediaType', 0)}"
        return self.chat_methods.get(key, self.default)(data)

    def resolve(self, data):
        """
        Resolves to a method based on the data's `t` parameter.
        returns the return value of the appropriate method
        """
        data = json.loads(data)
        return self.methods.get(data["t"], self.default)(data)

    def on_text_message(self, data):
        """
        Called when a text chat message is received.
        """
        pass

    def on_image_message(self, data):
        pass

    def on_youtube_message(self, data):
        pass

    def on_voice_message(self, data):
        pass

    def on_sticker_message(self, data):
        pass

    def on_group_member_join(self, data):
        pass

    def on_group_member_leave(self, data):
        pass

    def on_chat_invite(self, data):
        pass

    def default(self, data):
        """
        Called when the parameter `t` is not matched.
        """
        pass
