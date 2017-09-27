import socket
import sys
import select
import time
import re
from internals import message


class Client:

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = self.init_socket()
        self.streams = [self.sock, sys.stdin]
        self.username = raw_input("Enter username: ").strip() + "\n"
        self.pwd = raw_input("Enter password: ").strip() + "\n"

    def init_socket(self):
        # Create and connect socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        return sock

    def verify_login(self):
        message.send_msg(message.USER, self.username, self.sock)
        message.send_msg(message.PASS, self.pwd, self.sock)

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


    def run(self):
        self.verify_login()
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


