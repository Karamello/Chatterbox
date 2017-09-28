import message

class Chatroom:

    def __init__(self, name):
        self.name = name
        self.users = []

    def add_user(self, user):
        self.users.append(user)
        user.chatroom = self.name

    def remove_user(self, user, kick=False):
        self.users.remove(user)
        if self.name != 'default':
            text = "User {} has left the room".format(user.name) if not kick else "User {} was kicked from the room".format(user.name)
            self.broadcast(text)
        user.chatroom = 'default'

    def send_message(self, msg, client_socket):
        broad_range = [x for x in self.users if x.sock != client_socket]
        for user in broad_range:
            message.send_msg(message.NORMAL, msg + "\n", user.sock)

    def contains_user(self, user):
        for u in self.users:
            if u.name == user:
                return u
        return None

    def broadcast(self, msg):
        for user in self.users:
            message.send_msg(message.NORMAL, msg + "\n", user.sock)

    def is_empty(self):
        if self.name == 'default':
            return False
        else:
            return len(self.users) == 0

    def users_in_chat(self):
        return len(self.users)

    def get_user(self, name):
        for user in self.users:
            if user.name == name:
                return user