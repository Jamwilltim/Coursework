import socket
import threading
import sys
import os
from getopt import getopt

os.system("color")

SERVER_SHARED_FILES = os.getenv(
    "SHAREDFILES", "SharedFiles"
)  # Folder to store shared files

if not os.path.exists(SERVER_SHARED_FILES):
    os.makedirs(SERVER_SHARED_FILES)

# Colors for terminal output
RED = "\033[31m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
BRIGHT_RED = "\033[91m"
BRIGHT_GREEN = "\033[92m"
BRIGHT_BLUE = "\033[94m"
BRIGHT_CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"


# Create user class
class User:
    def __init__(self, username, address, socket):
        self.username = username
        self.address = address
        self.socket = socket


# Initialize users dictionary and client threads list
users = {}


# Get the input arguments, for the server this is just the port (-p), with a default value of 8000
def handle_args():
    o = dict(getopt(sys.argv[1:], "p:")[0])
    server_port = int(o.get("-p", 8000))
    start_server(server_port)


def start_server(server_port):
    global server_closing
    server_closing = False
    server_ip = "localhost"

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(
            (server_ip, server_port)
        )  # Bind the socket to the host and the port
        server.listen()  # Listen for incoming connections
        print(f"Server is listening on {server_ip}:{server_port}")

        # Function to listen for the quit command
        quit_thread = threading.Thread(target=listen_for_quit, args=(server,))
        quit_thread.start()

        while True:
            client_socket, addr = server.accept()  # Accept the connection
            print(
                f"{BRIGHT_BLUE}Connection established with {addr[0]}:{addr[1]}{RESET}"
            )

            add_user(client_socket, addr)

            # Create thread to allow multiple clients to connect
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.start()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        server.close()


def listen_for_quit(server):
    while True:
        command = input()
        if command.lower() == "quit":
            global server_closing
            server_closing = True
            for user in users.values():
                user.socket.sendall("Server is closing".encode())
                user.socket.close()
            server.close()
            print(f"{BRIGHT_RED}Server closed{RESET}")
            os._exit(0)


def add_user(client_socket, addr):
    # Receive the username from the client and add to the list of users
    username = client_socket.recv(1024).decode()
    user = User(username, addr, client_socket)
    users[username] = user

    # Send welcome message to the client
    client_socket.send(
        f"{BRIGHT_BLUE}Welcome to the chatroom {username}\n{BRIGHT_CYAN}Enter messages, type '/help' for commands list, or type '/exit' to leave{RESET}".encode()
    )

    # Broadcast the new connection to all users
    broadcast_message(f"{username} has connected", username, BRIGHT_BLUE)


def handle_client(client_socket, addr):
    global server_closing
    username = None
    try:
        # Find the username associated with this client socket
        for user in users.values():
            if user.socket == client_socket:
                username = user.username
                break

        while True:
            request = client_socket.recv(1024).decode()
            if request.startswith("/"):  # Check if the message is a command
                if handle_command(request, client_socket, username):
                    break
            else:  # Broadcast the message to all users
                print(f"{username}: {request}")
                broadcast_message(request, username)

    except (ConnectionResetError, ConnectionAbortedError):
        # Handle forcibly closed connection
        if username and not server_closing:
            broadcast_message(
                f"{username} has left",
                username,
                BRIGHT_RED,
            )
            if username in users:
                del users[username]  # Remove user from active users
    except Exception as e:
        print(f"Error when handling client: {e}")  # Print out any other error
    finally:
        client_socket.close()
        print(
            f"{MAGENTA}Connection to client ({addr[0]}:{addr[1]}) closed ({username}){RESET}"
        )


# Handle the command from the client, returns True if the command is to exit the chatroom and False to keep the chatroom open for the client
def handle_command(request, client_socket, username):
    if request == "/exit":
        client_socket.send(f"{BRIGHT_BLUE}Connection closed{RESET}".encode())
        broadcast_message(
            f"{username} has left",
            username,
            BRIGHT_RED,
        )
        # Remove user from active users
        del users[username]
        return True  # True to break the loop
    elif request.startswith("/whisper"):
        parts = request.split(" ", 2)
        if len(parts) >= 3:
            target_username = parts[1]
            message = parts[2]
            whisper_message(username, target_username, message)
        else:
            client_socket.send(
                f"{BRIGHT_RED}Invalid whisper command\n{WHITE}/whisper <username> <message>{RESET}".encode()
            )
        return False  # False to continue the loop
    elif request == "/files":
        list_files(client_socket)
        return False  # False to continue the loop
    elif request.startswith("/download"):
        parts = request.split(" ", 1)  # Split the command and the filename
        if len(parts) == 2:
            filename = parts[1]
            send_file(client_socket, filename)
        else:
            client_socket.send(
                f"{BRIGHT_RED}Invalid download command\n{WHITE}/download <filename>{RESET}".encode()
            )
        return False  # False to continue the loop
    elif request == "/users":
        client_socket.send(
            f"{BRIGHT_CYAN}Active users ({len(users)}): {YELLOW}{', '.join(users.keys())}{RESET}".encode()
        )
        return False
    elif request == "/help":
        client_socket.send(
            f"{BRIGHT_CYAN}Commands:\n{WHITE}/users{BRIGHT_CYAN} - List all active users in the chatroom\n{WHITE}/whisper <username> <message>{BRIGHT_CYAN} - Send a private message to a user\n{WHITE}/files{BRIGHT_CYAN} - List the number and filenames in the SharedFiles folder\n{WHITE}{WHITE}/download <filename>{BRIGHT_CYAN} - Download a file, will be saved to user directory\n{WHITE}/exit{BRIGHT_CYAN} - Leave the chatroom{RESET}".encode()
        )  # Formatted help message
        return False  # False to continue the loop


def whisper_message(sender_username, target_username, message):
    if target_username in users:  # Check user exists
        target_user = users[target_username]
        try:
            target_user.socket.sendall(
                f"{BRIGHT_GREEN}[Whisper from {sender_username}]:{RESET} {message}".encode()  # Send the encoded message along with a whisper tag showing who the whisper was from
            )
            print(
                f"Whisper from {sender_username} to {target_username}: {message}"
            )  # In the terminal log that the whisper was sent
        except Exception as e:
            print(f"Error sending whisper to {target_username}: {e}")
    else:
        sender_user = users[sender_username]
        try:
            sender_user.socket.sendall(
                f"{BRIGHT_RED}User {target_username} not found{RESET}".encode()
            )  # Send the correct error to the user that sent the whisper, detailing that the user they tried to whisper to does not exist
        except Exception as e:
            print(f"Error sending error message to {sender_username}: {e}")


# Send a message to all users except the current user
def broadcast_message(message, current_user=None, color=None, system=False):
    if system:
        if color:
            message = f"{color}{message}{RESET}"
            for user in users.values():
                user.socket.sendall(message.encode())
        else:
            for user in users.values():
                user.socket.sendall(message.encode())
    for user in users.values():
        if current_user == user.username:
            continue
        try:
            if color:
                user.socket.sendall(f"{color}{message}{RESET}".encode())
            else:
                user.socket.sendall(
                    f"{YELLOW}{current_user}:{RESET} {message}".encode()
                )
        except Exception as e:
            print(f"Error sending message to {user.username}: {e}")


# Send the names, file extensions and sizes of all files in the SharedFiles folder
def list_files(client_socket):
    try:
        files = os.listdir(SERVER_SHARED_FILES)
        if files:
            files_list = "\n".join(
                [
                    f"{file} ({os.path.getsize(os.path.join(SERVER_SHARED_FILES, file))} bytes)"
                    for file in files
                ]
            )
            client_socket.send(
                f"{BRIGHT_CYAN}Shared files ({len(files)} files):\n{WHITE}{files_list}{RESET}".encode()
            )
        else:
            client_socket.send(
                f"{BRIGHT_RED}No files found in the shared folder{RESET}".encode()
            )
    except Exception as e:
        client_socket.send(f"{BRIGHT_RED}Error listing files: {e}{RESET}".encode())


def send_file(client_socket, filename):
    try:
        client_socket.send(f"<START>".encode())
        file_path = os.path.join(SERVER_SHARED_FILES, filename)
        file_size = os.path.getsize(file_path)
        client_socket.send(str(file_size).encode())
        client_socket.send(filename.encode())

        with open(file_path, "rb") as file:
            data = file.read()
            client_socket.sendall(data)
            client_socket.send(b"<END>")

    except FileNotFoundError:
        client_socket.send(f"{BRIGHT_RED}File not found{RESET}".encode())
    except Exception as e:
        client_socket.send(f"{BRIGHT_RED}Error sending file: {e}{RESET}".encode())


if __name__ == "__main__":
    handle_args()
