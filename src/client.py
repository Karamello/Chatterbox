import socket
import sys
import select
import time
from internals import message


# Server variables
host = ''
port = 8080

# Create and connect socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

# Get username and send to server
username = raw_input("Enter username: ")
username = username.strip() + "\n"
message.send_msg(message.USER, username, sock)

# Create list on input streams, i.e stdin and the socket
reading = [sock, sys.stdin]


def pretty_print_message(message):
    msg_time = time.strftime("%H:%M:%S")
    print msg_time, message


while True:
    in_stream, _, _ = select.select(reading, [], [], 1)

    for src in in_stream:
        # If input stream is stdin, send message
        if src == sys.stdin:
            message.send_msg(message.NORMAL, sys.stdin.readline(), sock)
        # Else it's the socket, so read it and display it
        else:
            try:
                msg_type, text = message.receive_msg_from(sock)
            except RuntimeError:
                pretty_print_message("Lost connection to the server")
                sys.exit(0)
            pretty_print_message(text)





