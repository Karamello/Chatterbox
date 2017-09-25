import socket
import sys
import select
from internals import message

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8080))
print("Connected to server")

reading = [sock, sys.stdin]

NORMAL = 0
while True:
    read, _, _ = select.select(reading, [], [], 1)

    for s in read:
        if s == sys.stdin:
            message.send_msg(NORMAL, sys.stdin.readline(), sock)
        else:
            msgtype, text = message.receive_msg_from(sock)
            message.print_message(msgtype, text)






