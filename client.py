import socket
import threading
import os
import sys
import colors
from getopt import getopt

os.system("color")

# ANSI escape sequences for terminal manipulation
CLEAR_LINE = "\033[K"  # Clear from cursor to end of line
CURSOR_UP = "\033[A"  # Move cursor up one line


def handle_args():
    o = dict(getopt(sys.argv[1:], "u:h:p:")[0])

    username = o.get("-u")
    server_ip = o.get("-h", "127.0.0.1")
    server_port = o.get("-p")

    # Make sure that the required arguments are provided
    if not username:
        print(f"{colors.BRIGHT_RED}Error: Username is required{colors.RESET}")
        sys.exit(1)  # If a required argument is missing, exit the program
    if not server_port:
        print(f"{colors.BRIGHT_RED}Error: Server port is required{colors.RESET}")
        sys.exit(1)  # If a required argument is missing, exit the program

    server_port = int(server_port)  # Convert the port to an integer

    user_dir = os.path.join(os.getcwd(), username)

    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    run_client(username, server_port, server_ip, user_dir)  # Run the client


def run_client(username, server_port, server_ip, user_dir):
    # create a socket object
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # establish connection with server
    try:
        client.connect((server_ip, server_port))
    except Exception as e:
        print(f"{colors.BRIGHT_RED}Error: {e}{colors.RESET}")
        sys.exit(1)

    # Function to receive messages from the server
    def receive_messages():
        while True:
            try:
                message = client.recv(1024).decode()
                if message == "Server is closing":
                    sys.stdout.write(f"\r{CLEAR_LINE}")
                    print(
                        f"{colors.BRIGHT_BLUE}Server is closing. Disconnecting...{colors.RESET}"
                    )
                    client.close()
                    os._exit(0)
                    break
                if message == "<START>":
                    download_files(client, user_dir)
                elif message:
                    # Clear the input prompt line before printing the received message
                    sys.stdout.write(f"\r{CLEAR_LINE}")
                    print(message)
                    # Don't reprint the input prompt if the connection is closed
                    if (
                        message
                        == f"{colors.BRIGHT_BLUE}Connection closed{colors.RESET}"
                    ):
                        break
                    # Reprint the input prompt
                    sys.stdout.write("> ")
                    sys.stdout.flush()
                else:
                    break
            except OSError:
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages)
    receive_thread.daemon = (
        True  # Make thread daemon so it exits when main thread exits
    )
    receive_thread.start()
    try:
        client.send(username.encode())  # send username to the server
        while True:
            message = input("> ")
            if message == "/exit":  # Exit the program if the user types /exit
                client.send(message.encode())
                break
            if message == "/wave":
                client.send("\U0001F44B".encode())
                continue
            # Clear the input line and move cursor up
            sys.stdout.write(f"\r{CLEAR_LINE}{CURSOR_UP}{CLEAR_LINE}")
            # Print the formatted message
            print(f"{colors.MAGENTA}You:{colors.RESET} {message}")
            client.send(message.encode())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print(f"{colors.BRIGHT_RED}Closing socket{colors.RESET}")
        client.close()
        receive_thread.join(timeout=1.0)  # Add timeout to prevent hanging


def download_files(client, user_dir):
    try:
        # Receive the file size
        file_size = int(client.recv(1024).decode())
        filename = client.recv(1024).decode()
        print(
            f"{colors.BRIGHT_CYAN}Downloading file {filename} ({file_size} bytes){colors.RESET}"
        )

        file_path = os.path.join(user_dir, filename)

        # Create empty file to write to
        file_bytes = b""
        done = False

        # Temporarily disable the prompt reprinting
        sys.stdout.write("\r")
        sys.stdout.flush()

        while not done:
            data = client.recv(1024)
            if b"<END>" in data:
                file_bytes += data[: data.find(b"<END>")]
                done = True
            else:
                file_bytes += data

        # Write the received bytes to a file
        with open(file_path, "wb") as file:
            file.write(file_bytes)

        print(f"\n{colors.BRIGHT_GREEN}File received: {filename}{colors.RESET}")

    except Exception as e:
        print(f"Error downloading file: {e}")

    # Reprint the input prompt
    sys.stdout.write("> ")
    sys.stdout.flush()


if __name__ == "__main__":
    handle_args()
