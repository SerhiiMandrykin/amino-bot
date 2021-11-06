from handlers.entities.me_handler import *
from handlers.entities.kick_handler import KickHandler


class HandlerItems:
    def __init__(self, client_object):
        self.items = [
            MeHandler(client_object),
            KickHandler(client_object)
        ]
