import select
import socket
import time
import re
from internals import message, user as u, chatroom


class Server:

    def __init__(self, port):
        self.host = ''
        self.port = port
        self.server_sock = self.init_socket(self.host, self.port)
        self.client_sockets = []
        self.client_users = {}
        self.init_logging()
        self.chatrooms = {}
        self.start_time = time.time()

    # Initialises server socket
    def init_socket(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.setblocking(0)
        sock.listen(1)
        return sock

    # Initialises logging server side
    def init_logging(self):
        # Create new file to log messages sent to and from server
        with open("serverlog.txt", "w") as f:
            f.write("[SERVER] Server started at " + time.strftime("%d/%m/%Y %H:%M:%S"))
            f.write("\n")

    # Server-wide broadcast message to clients
    def broadcast(self, msg_type, msg_text, client_socket=None):
        broad_range = [x for x in self.client_sockets if x != client_socket]
        for sock in broad_range:
            message.send_msg(msg_type, msg_text + "\n", sock)

    # Add messages to log as we wish
    def log_message(self, log_type, message):
        log_time = time.strftime("%H:%M:%S")
        input_string = "[" + log_type + "] " + log_time + ": " + message
        with open("serverlog.txt", "a") as f:
            f.write(input_string + "\n")

    # Closes the connection to the client and notifies users where appropriate
    def close_connection(self, client_socket):
        print("Lost connection to client")
        self.client_sockets.remove(client_socket)
        if client_socket in self.client_users:
            user = self.client_users[client_socket]
            self.broadcast(message.NORMAL, "User {} left the chat".format(user.name))
            self.log_message("SERVER", "User {} left the chat".format(user.name))
            self.chatrooms[user.chatroom].remove_user(user)
            del self.client_users[client_socket]
        client_socket.close()

    # Authenticates a user against our registered database
    def authenticate_user(self, username, password):
        with open("users.txt", "r") as f:
            for line in f:
                user, pwd = line.strip().split(":")
                if username == user and pwd == password:
                    return True

    # Handles logging in a user and adding them to the chat
    def user_login(self, user, pwd, client_socket):
        for log_user in self.client_users.values():
            if user == log_user.name:
                message.send_msg(message.REJECT, "User is already logged in\n", client_socket)
                self.log_message("SERVER", "User {} is already logged in".format(user))
                return 0
        if self.authenticate_user(user, pwd):
            new_user = u.User(user, False, client_socket)
            self.chatrooms['default'].add_user(new_user)
            self.client_users[client_socket] = new_user
            self.log_message("SERVER", "User {} entered the chat".format(user))
            self.broadcast(message.NORMAL, "User {} entered the chat".format(user))
        else:
            message.send_msg(message.REJECT, "Couldn't authenticate user {}\n".format(user), client_socket)
            self.log_message("SERVER", "Failed login for user {}".format(user))

    # Joins a user to a chatroom. Creates chatroom if doesn't exist and deletes if empty.
    def join_chatroom(self, data, client_socket):
        match = re.match(r"^/join\s(\w+)", data)
        user = self.client_users[client_socket]
        if match:
            chat = user.chatroom
            self.log_message("CLIENT", "User {} left room {}".format(user.name, chat))
            self.chatrooms[chat].remove_user(user)
            if self.chatrooms[chat].is_empty():
                del self.chatrooms[chat]
            room = match.group(1)
            if room in self.chatrooms:
                self.chatrooms[room].add_user(user)
            else:
                new_room = chatroom.Chatroom(room)
                new_room.add_user(user)
                self.chatrooms[room] = new_room
            self.chatrooms[room].broadcast("User {} has entered the room #{}".format(user.name, room))
            self.log_message("CLIENT", "User {} joined room {}".format(user.name, room))

    # Handles direct messaging between users across chatrooms
    def direct_message(self, data, client_socket):
        match = re.match(r"^/direct\s(\w+)\s(.*)", data)
        user = self.client_users[client_socket]
        if match:
            target = match.group(1)
            msg = match.group(2)
            out_message = "{} <direct>: {}".format(user.name, msg)
            send_to = self.find_socket_by_name(target)
            self.log_message("CLIENT", "{} to {} <direct>: {}".format(user.name, target, msg))
            if send_to:
                message.send_msg(message.DIRECT, out_message + "\n", send_to)
            else:
                message.send_msg(message.NORMAL, "User {} is not online\n".format(target), client_socket)

    # Given a user's name, returns their socket for direct communication
    def find_socket_by_name(self, name):
        for chat in self.chatrooms:
            match = self.chatrooms[chat].contains_user(name)
            if match:
                return match.sock

    # Parses a string to find a users command to execute
    def parse_command(self, data, client_socket):
        match = re.match(r"^/(\w+)\s?(.*)", data)
        if match:
            self.exec_command(match.group(1), match.group(2), client_socket)

    # Executes a users command if it exists
    def exec_command(self, command, args, client_socket):
        if command == 'uptime':
            up = time.strftime("%H:%M:%S", time.gmtime(self.uptime()))
            message.send_msg(message.COMMAND, "Server uptime is {} seconds\n".format(up), client_socket)
        elif command == 'rooms':
            message.send_msg(message.COMMAND, "Chatrooms available: {}\n".format(self.list_chatrooms()), client_socket)
        elif command == 'users':
            if args:
                d_parse = re.search(r"^(\w+)", args)
                if d_parse:
                    message.send_msg(message.COMMAND, "Users online in #{}: {}\n".format(args, self.list_users_in_room(args)), client_socket)
            else:
                message.send_msg(message.COMMAND, "Users online: {}\n".format(self.list_users()), client_socket)
        elif command == 'help':
            message.send_msg(message.COMMAND, "Server commands: \n{}\n".format(self.build_help()), client_socket)

    # Registers a new user into our database
    def register_user(self, data, client_socket):
        username = data.split(" ")[0]
        match = False
        with open("users.txt", "r+a") as f:
            for line in f:
                user, _ = line.strip().split(":")
                if username.strip() == user:
                    match = True
                    message.send_msg(message.REJECT, "Username already registered\n", client_socket)
                    break
            if not match:
                f.write("\n")
                f.write(data)
                self.log_message("SERVER", "User {} registered to server".format(username))
                message.send_msg(message.OK, "\n", client_socket)

    # Handles messages passed to the server and takes appropriate action
    def handle_message(self, client_socket):
        msg_type, data = message.receive_msg_from(client_socket)
        if msg_type == message.USER:
            msg_type, pwd = message.receive_msg_from(client_socket)
            if msg_type == message.PASS:
                self.user_login(data, pwd, client_socket)
        elif msg_type == message.NORMAL:
            user = self.client_users[client_socket]
            chat = self.chatrooms[user.chatroom]
            out_message = "{}: {}".format(user.name, data)
            chat.send_message(out_message, client_socket)
            self.log_message("CLIENT in " + chat.name, out_message)
        elif msg_type == message.JOIN:
            self.join_chatroom(data, client_socket)
        elif msg_type == message.DIRECT:
            self.direct_message(data, client_socket)
        elif msg_type == message.COMMAND:
            self.parse_command(data, client_socket)
        elif msg_type == message.REGISTER:
            self.register_user(data, client_socket)

    # Returns the server uptime
    def uptime(self):
        return time.time() - self.start_time

    # Returns a string list of chatrooms in the format name(num of users online)
    def list_chatrooms(self):
        temp = []
        for chat in self.chatrooms.keys():
            num_users = self.chatrooms[chat].users_in_chat()
            temp.append("{}({})".format(chat, num_users))
        return ", ".join(temp)

    def list_users(self):
        online = []
        for user in self.client_users.values():
            online.append(user.name)
        return ", ".join(online)

    def list_users_in_room(self, room):
        online = []
        if room in self.chatrooms.keys():
            for user in self.chatrooms[room].users:
                online.append(user.name)
            return ", ".join(online)
        else:
            return "Chatroom doesn't exist"

    def build_help(self):
        cmd_str = []
        cmd_str.append("/uptime - Show server uptime")
        cmd_str.append("/rooms - List available chatrooms and show how many users in each")
        cmd_str.append("/users - List all users online")
        cmd_str.append("/users <chatroom> - List all users in chatroom")
        cmd_str.append("/help - This help dialog")
        return "\n".join(cmd_str)
    # Main loop
    def run(self):
        self.chatrooms['default'] = chatroom.Chatroom('default')
        while True:
            read, _, _ = select.select(self.client_sockets + [self.server_sock], [], [])

            for s in read:
                # If the socket to read is the server socket, new connection ready
                if s == self.server_sock:
                    conn, addr = self.server_sock.accept()
                    self.log_message("SERVER", "Accepted connection from {}".format(addr))
                    print("Connceted to {}".format(addr))
                    self.client_sockets.append(conn)
                    conn.setblocking(0)
                # Else, a client has data - broadcast it
                else:
                    try:
                        self.handle_message(s)
                    except RuntimeError:
                        self.close_connection(s)

if __name__ == '__main__':
    server = Server(8080)
    server.run()