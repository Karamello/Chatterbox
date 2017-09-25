import socket
import message

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8080))
print("Connected to server")

NORMAL = 0
while True:

    data = raw_input("> ")
    print(len(data))
    message.send_msg(NORMAL, data + "\n", sock)

    msgtype, text = message.receive_msg_from(sock)
    message.print_message(msgtype, text)




