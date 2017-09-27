import message

class Chatroom:

    def __init__(self, name):
        self.name = name
        self.users = []

    def add_user(self, user):
        self.users.append(user)
        user.chatroom = self.name

    def remove_user(self, user):
        self.users.remove(user)
        user.chatroom = 'default'

    def send_message(self, msg, client_socket):
        broad_range = [x for x in self.users if x.sock != client_socket]
        for user in broad_range:
            message.send_msg(message.NORMAL, msg + "\n", user.sock)
