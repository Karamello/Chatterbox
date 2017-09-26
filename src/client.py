import socket
import sys
import select
from internals import message

# Server variables
host = ''
port = 8080

# Create and connect socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

# Create list on input streams, i.e stdin and the socket
reading = [sock, sys.stdin]

# Message types enum like
NORMAL = 0

while True:
    in_stream, _, _ = select.select(reading, [], [], 1)

    for src in in_stream:
        # If input stream is stdin, send message
        if src == sys.stdin:
            message.send_msg(NORMAL, sys.stdin.readline(), sock)
        # Else it's the socket, so read it and display it
        else:
            msg_type, text = message.receive_msg_from(sock)
            message.print_message(msg_type, text)






