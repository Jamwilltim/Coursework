# Terminal Based IM App

Created in Python 3.12.0, this application comes with a server and client component. When launched it allows for messaging functionality and downloading files to a client machine from a SharedFIles folder stored on the server.

## Setup

1. Clone the repository:

```bash
git clone "https://github.com/Jamwilltim/IM-App"
```

2. Create a SharedFiles folder in the root directory of your project and populate it with the files you want available to be shared.

```
./
|__SharedFiles
|  |__example.txt
|  |__exapmle.jpg
|  |__etc
|__.gitignore
|__README.md
|__client.py
|__colors.py
|__server.py
```

3. Make sure the `SERVER_SHARED_FILES` variable is correctly set (at the top of the `server.py` file, it defaults to:

```python
SERVER_SHARED_FILES = "./SharedFiles"
```

### Running the Program

To run the program, start the `server.py` first then clients can connect via launching the `client.py` file.
Make sure to change the `-p` option it will default to `8000` if not provided.

```bash
py server.py -p port_number
```

The username (`-u`) and port_number (`-p`) are required options, you cannot join the server without providing them, the hostname (`-h`) will default to `127.0.0.1`

```bash
py client.py -u username -h hostname -p port_number
```

## Commands

Whilst in the application you can enter commands into both sides of the terminal (_server_ and _client_).

### Client

All commands in the _client_ side start with a `/` character

-   `/help` - Display a list of all client-side commands
-   `/exit` - Close instance of _client_ and leave the server
-   `/users` - List all of the users currently logged onto the server
-   `/wave` - Sends a waving emoji (👋) to everyone in the server
-   `/whisper <username> <message>` - Send a message to one specific user
-   `/files` - List all the files in the _SharedFiles_ folder, and their size in bytes
-   `/download <filename>` - Download the file with name `<filename>` and save to `./<username>`

### Server

The only command on the server side is `quit` which disconnects all clients from the server and then quits the application
