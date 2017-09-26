import socket
import select
from internals import message
import time

# Server variables
host = ''
port = 8080

# Create socket
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Allow socket to reuse address
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind socket and listen for incoming connections
server_sock.bind((host, port))
server_sock.setblocking(0)
server_sock.listen(1)

# Maintain list of client sockets only
client_sockets = []

# Message types
NORMAL = 0

# Create new file to log messages sent to and from server
with open("serverlog.txt", "w") as f:
    f.write("[SERVER] Logging started at " + time.strftime("%H:%M:%S"))
    f.write("\n")


# Broadcast message to all clients
def broadcast(msg_type, msg_text, sockets):
    for sock in sockets:
        message.send_msg(msg_type, msg_text + "\n", sock)


while True:
    read, _, _ = select.select(client_sockets + [server_sock], [], [])

    for s in read:
        # If the socket to read is the server socket, new connection ready
        if s == server_sock:
            conn, addr = server_sock.accept()
            print("Connceted to {}".format(addr))
            client_sockets.append(conn)
            conn.setblocking(0)
        # Else, a client has data - broadcast it
        else:
            msg_type, data = message.receive_msg_from(s)
            with open("serverlog.txt", "a") as f:
                log_time = time.strftime("%H:%M:%S")
                f.write("[CLIENT] " + log_time + ": " + data)
                f.write("\n")
            message.print_message(msg_type, data)
            broadcast(msg_type, data, client_sockets)


