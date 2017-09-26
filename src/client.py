import socket
import sys
import select
import time
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

    def run(self):
        self.verify_login()
        while True:
            in_stream, out_stream, _ = select.select(self.streams, [], [], 1)
            for src in in_stream:
                # If input stream is stdin, send message
                if src == sys.stdin:
                    message.send_msg(message.NORMAL, sys.stdin.readline(), self.sock)
                # Else it's the socket, so read it and display it
                else:
                    try:
                        msg_type, text = message.receive_msg_from(self.sock)
                    except RuntimeError:
                        self.pretty_print_message("Lost connection to the server")
                        sys.exit(0)
                    self.pretty_print_message(text)


client = Client('', 8080)
client.run()


