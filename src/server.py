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
client_users = {}

# Message types
NORMAL = 0

# Create new file to log messages sent to and from server
with open("serverlog.txt", "w") as f:
    f.write("[SERVER] Server started at " + time.strftime("%d/%m/%Y %H:%M:%S"))
    f.write("\n")


# Broadcast message to all clients
def broadcast(msg_type, msg_text, sockets):
    for sock in sockets:
        message.send_msg(msg_type, msg_text + "\n", sock)


# Add messages to log as we wish
def log_message(log_type, message):
    log_time = time.strftime("%H:%M:%S")
    input_string = "[" + log_type + "] " + log_time + ": " + message
    with open("serverlog.txt", "a") as f:
        f.write(input_string + "\n")


# Closes the connection to the client and notifies users where appropriate
def close_connection(client_socket, sockets):
    print("Lost connection to client")
    client_sockets.remove(client_socket)
    if client_socket in client_users:
        broadcast(message.NORMAL, "User {} left the chat".format(client_users[client_socket]), sockets)
        del client_users[client_socket]
    client_socket.close()


# Handles messages passed to the server and takes appropriate action
def handle_message(client_socket, sockets):
    msg_type, data = message.receive_msg_from(client_socket)
    if msg_type == message.USER:
        if data in client_users.values():
            close_connection(client_socket, sockets)
            return
        client_users[client_socket] = data
        log_message("SERVER", "User {} entered the chat".format(data))
        broadcast(message.NORMAL, "User {} entered the chat".format(data), sockets)
    elif msg_type == message.NORMAL:
        out_message = client_users[client_socket] + ": " + data
        broadcast(message.NORMAL, out_message, sockets)
        log_message("CLIENT", out_message)


while True:
    read, _, _ = select.select(client_sockets + [server_sock], [], [])

    for s in read:
        # If the socket to read is the server socket, new connection ready
        if s == server_sock:
            conn, addr = server_sock.accept()
            log_message("SERVER", "Accepted connection from {}".format(addr))
            print("Connceted to {}".format(addr))
            client_sockets.append(conn)
            conn.setblocking(0)
        # Else, a client has data - broadcast it
        else:
            try:
                handle_message(s, client_sockets)
            except RuntimeError:
                close_connection(s, client_sockets)

