import time
import re
import message


class Commander:

    def __init__(self, server):
        self.start_time = time.time()
        self.server = server

    def exec_command(self, command, args, client_socket):
        if command == 'uptime':
            up = time.strftime("%H:%M:%S", time.gmtime(self.uptime()))
            message.send_msg(message.COMMAND, "Server uptime is {} seconds\n".format(up), client_socket)
        elif command == 'rooms':
            message.send_msg(message.COMMAND, "Chatrooms available: {}\n".format(self.list_chatrooms()), client_socket)
        elif command == 'users':
            if args:
                d_parse = re.search(r"^(\w+)", args)
                if d_parse:
                    message.send_msg(message.COMMAND, "Users online in #{}: {}\n".format(args, self.list_users_in_room(args)), client_socket)
            else:
                message.send_msg(message.COMMAND, "Users online: {}\n".format(self.list_users()), client_socket)
        elif command == 'help':
            user = self.server.client_users[client_socket]
            message.send_msg(message.COMMAND, "Server commands: \n{}\n".format(self.build_help(user.is_admin)), client_socket)
        elif command == 'kick':
            self.server.kick_user(client_socket, args)

    # Returns the server uptime
    def uptime(self):
        return time.time() - self.start_time

    # Returns a string list of chatrooms in the format name(num of users online)
    def list_chatrooms(self):
        temp = []
        for chat in self.server.chatrooms.keys():
            num_users = self.server.chatrooms[chat].num_users_in_chat()
            temp.append("{}({})".format(chat, num_users))
        return ", ".join(temp)

    # Returns a string list of users online, comma separated
    def list_users(self):
        online = []
        for user in self.server.client_users.values():
            online.append(user.name)
        return ", ".join(online)

    # Returns a string list of users in a given room, comma separated
    def list_users_in_room(self, room):
        online = []
        if room in self.server.chatrooms.keys():
            for user in self.server.chatrooms[room].users:
                online.append(user.name)
            return ", ".join(online)
        else:
            return "Chatroom doesn't exist"

    # Returns the list of commands applicable to a user, including admin if appropriate
    def build_help(self, admin=False):
            cmd_str = ["/uptime - Show server uptime"]
            cmd_str.append("/rooms - List available chatrooms and show how many users in each")
            cmd_str.append("/join <name> - Join a chatroom called <name> - created if doesn't exist")
            cmd_str.append("/direct <username> - Send a direct message to a user if they are online")
            cmd_str.append("/users - List all users online")
            cmd_str.append("/users <chatroom> - List all users in chatroom")
            cmd_str.append("/quit - Quit the program")
            cmd_str.append("/help - This help dialog")
            if admin:
                cmd_str.append("--- ADMIN COMMANDS ---")
                cmd_str.append("/kick room <username> - Kicks user from room back to default")
                cmd_str.append("/kick server <username> - Kicks user from server")
            return "\n".join(cmd_str)
