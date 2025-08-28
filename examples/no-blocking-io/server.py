import sys
import socket
import select


class Server():
    DEFAULT_HOST = socket.gethostbyname(socket.gethostname())
    DEFAULT_PORT = 65432

    def __init__(self, host: str = None, port: int = None) -> None:
        self.socket = None

        self.host = host if host else self.DEFAULT_HOST
        self.port = port if port else self.DEFAULT_PORT
        
    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)

        self.addr = (self.host, self.port)

        try:
            self.socket.bind(self.addr)
        except socket.error as error:
            print(f"Bind failed. \nError Code: {str(error[0])} \nMessage: {str(error[1])}")
            sys.exit()
        
        self.socket.listen()

        print(f"Server listening on {self.host}:{self.port}")