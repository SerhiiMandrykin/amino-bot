from handlers.entities.me_handler import *
from handlers.entities.kick_handler import KickHandler
from handlers.entities.obscene_handler import ObsceneHandler


class HandlerItems:
    def __init__(self, client_object):
        self.items = [
            MeHandler(client_object),
            KickHandler(client_object),
            ObsceneHandler(client_object)
        ]
