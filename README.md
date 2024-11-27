# Terminal Based IM App
Created in Python 3.12.0, this application comes with a server and client component. When launched it allows for messaging functionality and downloading files to a client machine from a SharedFIles folder stored on the server.

It uses the python `socket` library.

## Setup
1. Clone the repository:
```
git clone "https://github.com/Jamwilltim/IM-App"
```
2. Create a SharedFiles folder in the root directory of your project and populate it with the files you want available to be shared.
```
.
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
