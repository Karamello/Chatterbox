import socket
import select
import time
from internals import message


class Server:

    def __init__(self, port):
        self.host = ''
        self.port = port
        self.server_sock = self.init_socket(self.host, self.port)
        self.client_sockets = []
        self.client_users = {}
        self.init_logging()

    def init_socket(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.setblocking(0)
        sock.listen(1)
        return sock

    def init_logging(self):
        # Create new file to log messages sent to and from server
        with open("serverlog.txt", "w") as f:
            f.write("[SERVER] Server started at " + time.strftime("%d/%m/%Y %H:%M:%S"))
            f.write("\n")

    # Broadcast message to all clients
    def broadcast(self, msg_type, msg_text):
        for sock in self.client_sockets:
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
            self.broadcast(message.NORMAL, "User {} left the chat".format(self.client_users[client_socket]))
            self.log_message("SERVER", "User {} left the chat".format(self.client_users[client_socket]))
            del self.client_users[client_socket]
        client_socket.close()

    def authenticate_user(self, username, password):
        with open("users.txt", "r") as f:
            for line in f:
                user, pwd = line.strip().split(" ")
                if username == user and pwd == password:
                    return True

    def user_login(self, user, pwd, client_socket):
        if user in self.client_users.values():
            self.close_connection(client_socket)
            self.log_message("SERVER", "User {} is already logged in".format(user))
        else:
            if self.authenticate_user(user, pwd):
                self.client_users[client_socket] = user
                self.log_message("SERVER", "User {} entered the chat".format(user))
                self.broadcast(message.NORMAL, "User {} entered the chat".format(user))
            else:
                self.log_message("SERVER", "Failed login for user {}".format(user))
                self.close_connection(client_socket)

    # Handles messages passed to the server and takes appropriate action
    def handle_message(self, client_socket):
        msg_type, data = message.receive_msg_from(client_socket)
        if msg_type == message.USER:
            msg_type, pwd = message.receive_msg_from(client_socket)
            if msg_type == message.PASS:
                self.user_login(data, pwd, client_socket)
        elif msg_type == message.NORMAL:
            out_message = self.client_users[client_socket] + ": " + data
            self.broadcast(message.NORMAL, out_message)
            self.log_message("CLIENT", out_message)

    def run(self):
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

server = Server(8080)
server.run()