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
    LEADER_ROLES = [100, 102]
    CURATOR_ROLES = [101]

    def __init__(self, user_id, nickname, profile_picture, user_level, reputation, is_leader=False, is_curator=False):
        self.user_id = user_id
        self.nickname = nickname
        self.profile_picture = profile_picture
        self.user_level = user_level
        self.reputation = reputation
        self.is_leader = is_leader
        self.is_curator = is_curator

    @staticmethod
    def parse_user(item):
        is_leader = item['role'] in User.LEADER_ROLES
        is_curator = item['role'] in User.CURATOR_ROLES
        return User(user_id=item['uid'], nickname=item['nickname'], profile_picture=item['icon'],
                    user_level=item['level'], reputation=item['reputation'], is_leader=is_leader, is_curator=is_curator)


class Message:
    """
    type 0 - simple text
    type 3 -sticker
    mediaValue - picture
    """

    def __init__(self, author: User, message_text: str, message_id: str, from_id: str, chat_id: str,
                 community_id: Optional[str], has_reply: bool = False, reply_message=None):
        self.community_id = community_id
        self.chat_id = chat_id
        self.from_id = from_id
        self.message_id = message_id
        self.message_text = message_text
        self.author = author
        self.has_reply = has_reply
        self.reply_message: Optional[Message] = reply_message
        self.intent = None

    @staticmethod
    def parse_message(item, community_id: Optional[str] = None):
        user = User.parse_user(item['author'])
        has_reply = False
        reply_message = None
        if 'replyMessage' in item['extensions'].keys():
            has_reply = True
            reply_message = Message.parse_message(item=item['extensions']['replyMessage'], community_id=community_id)

        return Message(author=user, message_text=item['content'], message_id=item['messageId'], from_id=item['uid'],
                       chat_id=item['threadId'], community_id=community_id, has_reply=has_reply,
                       reply_message=reply_message)
