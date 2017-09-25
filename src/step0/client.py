import socket
import message


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8080))
print("Connected to server")
while True:

    data = raw_input("> ")
    print(len(data))
    message.send_msg(0, data + "\n", sock)



