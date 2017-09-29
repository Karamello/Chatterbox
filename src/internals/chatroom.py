import message

class Chatroom:

    def __init__(self, name):
        self.name = name
        self.users = []

    # Adds a user to the chatroom
    def add_user(self, user):
        self.users.append(user)
        user.chatroom = self.name

    # Removes a user from the chatroom. Optional kick parameter changes message sent to other clients.
    def remove_user(self, user, kick=False):
        self.users.remove(user)
        if self.name != 'default':
            text = "User {} has left the room".format(user.name) if not kick else "User {} was kicked from the room".format(user.name)
            self.broadcast(text)
        user.chatroom = 'default'

    # Sends a message to users in the chatroom
    def send_message(self, msg, client_socket):
        broad_range = [x for x in self.users if x.sock != client_socket]
        for user in broad_range:
            message.send_msg(message.NORMAL, msg + "\n", user.sock)

    # Returns whether a user exists in this chatroom
    def contains_user(self, user):
        for u in self.users:
            if u.name == user:
                return u
        return None

    # Broadcasts a message to this chatroom only
    def broadcast(self, msg):
        for user in self.users:
            message.send_msg(message.NORMAL, msg + "\n", user.sock)

    # Returns whether or not the chatroom is empty for deletion
    def is_empty(self):
        if self.name == 'default':
            return False
        else:
            return len(self.users) == 0

    # Returns the number of users that are in the chat
    def num_users_in_chat(self):
        return len(self.users)

    # Returns a user object given a name for this chatroom
    def get_user(self, name):
        for user in self.users:
            if user.name == name:
                return user