import socket
import message

host = ''
port = 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((host, port))
sock.listen(1)
conn, addr = sock.accept()

NORMAL = 0

print("Connceted to {}".format(addr))
while True:

    msgtype, data = message.receive_msg_from(conn)
    message.print_message(msgtype, data)
    message.send_msg(NORMAL, data + "\n", conn)


