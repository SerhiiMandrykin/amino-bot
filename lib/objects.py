from typing import Optional


class Communities:
    """
    Class contains list of communities
    """

    def __init__(self, communities):
        self.communities = communities
        self.items = []
        for item in communities:
            self.items.append(Community.parse_community(item))


class Community:
    """
    Object of a community
    """

    def __init__(self, name, community_id):
        self.name = name
        self.communityId = community_id

    @staticmethod
    def parse_community(item):
        return Community(name=item['name'], community_id=item['ndcId'])

    def __str__(self):
        return self.name


class Chats:
    """
    Class contains list of chats
    """

    def __init__(self, chats):
        self.chats = chats
        self.items = []
        for item in chats:
            self.items.append(Chat.parse_chat(item))


class Chat:
    """
    Object of a chat
    """

    def __init__(self, name, chat_id):
        self.name = name
        self.chatId = chat_id

    @staticmethod
    def parse_chat(item):
        return Chat(name=item['title'], chat_id=item['threadId'])

    def __str__(self):
        return self.name


class Users:
    """
    Class contains list of users
    """

    def __init__(self, users):
        self.users = users
        self.items = []
        for item in users:
            self.items.append(User.parse_user(item))


class User:
    def __init__(self, user_id, nickname, profile_picture, user_level, reputation):
        self.user_id = user_id
        self.nickname = nickname
        self.profile_picture = profile_picture
        self.user_level = user_level
        self.reputation = reputation

    @staticmethod
    def parse_user(item):
        return User(user_id=item['uid'], nickname=item['nickname'], profile_picture=item['icon'],
                    user_level=item['level'], reputation=item['reputation'])


class Message:
    """
    type 0 - simple text
    type 3 -sticker
    mediaValue - picture
    """

    def __init__(self, author: User, message_text: str, message_id: str, from_id: str, chat_id: str,
                 community_id: Optional[str]):
        self.community_id = community_id
        self.chat_id = chat_id
        self.from_id = from_id
        self.message_id = message_id
        self.message_text = message_text
        self.author = author

    @staticmethod
    def parse_message(item, community_id: Optional[str] = None):
        user = User.parse_user(item['author'])
        return Message(author=user, message_text=item['content'], message_id=item['messageId'], from_id=item['uid'],
                       chat_id=item['threadId'], community_id=community_id)
