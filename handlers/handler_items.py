from handlers.entities.me_handler import *


class HandlerItems:
    def __init__(self, client_object):
        self.items = [
            MeHandler(client_object)
        ]
