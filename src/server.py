import socket
import select
from internals import message

host = ''
port = 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((host, port))
sock.setblocking(0)
sock.listen(1)

sockets = [sock]

NORMAL = 0


while True:
    read, _, _ = select.select(sockets, [], [])

    for s in read:
        if s == sock:
            conn, addr = sock.accept()
            print("Connceted to {}".format(addr))
            sockets.append(conn)
            conn.setblocking(0)
        else:
            msgtype, data = message.receive_msg_from(s)
            message.print_message(msgtype, data)
            message.send_msg(NORMAL, data + "\n", s)


