import socket
import sys
import select
import os
import time
import hashlib
import re
import ssl
from internals import message


class Client:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = self.init_socket()
        self.streams = [self.sock, sys.stdin]
        self.username = ""

    # Initialises client socket
    def init_socket(self):
        # Create and connect socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sslsock = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_SSLv2)
            sslsock.connect((self.host, self.port))
        except socket.error:
            print("Cannot contact server. Is the server online?")
            sys.exit()
        return sslsock

    def verify_login(self, text=""):
        self.draw_ui(text if text else "Login to Chatterbox")
        self.username = raw_input("Enter username: ").strip() + "\n"
        pwd = raw_input("Enter password: ").strip()
        md5_pwd = hashlib.md5(pwd).hexdigest() + "\n"
        message.send_msg(message.USER, self.username, self.sock)
        message.send_msg(message.PASS, md5_pwd, self.sock)
        res, text = message.receive_msg_from(self.sock)
        if res == message.REJECT:
            self.verify_login(text)

    def pretty_print_message(self, message):
        msg_time = time.strftime("%H:%M:%S")
        print msg_time, message

    def parse_input(self, user_input):
        direct_match = re.match(r"^/direct\s(\w+)\s(.*)", user_input)
        if re.search(r"^/join", user_input):
            message.send_msg(message.JOIN, user_input, self.sock)
        elif direct_match:
            message.send_msg(message.DIRECT, user_input, self.sock)
            self.pretty_print_message("You <direct to {}>: {}".format(direct_match.group(1), direct_match.group(2)))
        elif re.search(r"^/quit", user_input):
            self.sock.close()
            sys.exit(0)
        elif re.search(r"^/", user_input):
            message.send_msg(message.COMMAND, user_input, self.sock)
        else:
            message.send_msg(message.NORMAL, user_input, self.sock)
            self.pretty_print_message("You: " + user_input.strip())

    def handle_message(self):
        msg_type, text = message.receive_msg_from(self.sock)
        if msg_type == message.DIRECT:
            self.pretty_print_message(text)
        elif msg_type == message.NORMAL:
            self.pretty_print_message(text)
        elif msg_type == message.COMMAND:
            self.pretty_print_message(text)

    def register(self, err=""):
        if err:
            self.draw_ui(err)
        else:
            self.draw_ui("Registering new user")
        self.username = raw_input("Enter username: ").strip()
        pwd = raw_input("Enter password: ").strip()
        conf_pwd = raw_input("Confirm password: ").strip()
        while conf_pwd != pwd:
            print("Passwords don't match!")
            pwd = raw_input("Enter password: ").strip()
            conf_pwd = raw_input("Confirm password: ").strip()
        md5_pwd = hashlib.md5(pwd).hexdigest() + "\n"
        message.send_msg(message.REGISTER, ":".join([self.username, md5_pwd]), self.sock)
        msg_type, text = message.receive_msg_from(self.sock)

        if msg_type == message.REJECT:
            self.register(text)
        else:
            self.verify_login("Registration successful. Login to your new account")

    def startup(self):
        self.draw_ui("Welcome to Chatterbox")
        print("Would you like to register or sign in?")
        option = raw_input("/register or /login: ")
        try:
            if re.search(r"^/register", option):
                self.register()
            else:
                self.verify_login()
        except RuntimeError:
            self.pretty_print_message("Lost connection to the server")
            sys.exit(0)

    def draw_ui(self, title):
        os.system("clear")
        print("Chatterbox")
        print("-" * 30)
        print(title)
        print("-" * 30)

    def run(self):
        self.startup()
        self.draw_ui("Welcome to Chatterbox, {}!".format(self.username.strip()))
        while True:
            in_stream, out_stream, _ = select.select(self.streams, [], [], 1)
            for src in in_stream:
                # If input stream is stdin, send message
                if src == sys.stdin:
                    msg = sys.stdin.readline()
                    self.parse_input(msg)
                # Else it's the socket, so read it and display it
                else:
                    try:
                        self.handle_message()
                    except RuntimeError:
                        self.pretty_print_message("Lost connection to the server")
                        sys.exit(0)

if __name__ == '__main__':
    client = Client('', 8080)
    client.run()


