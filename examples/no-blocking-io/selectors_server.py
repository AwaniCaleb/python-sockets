import sys
import socket
import selectors

class Server():
    """
    A simple non-blocking TCP server that handles multiple clients
    concurrently using the `selectors` module for I/O multiplexing.
    """
    DEFAULT_HOST = '127.0.0.1'
    DEFAULT_PORT = 65432

    def __init__(self, host: str = None, port: int = None) -> None:
        """
        Initializes the server with a host and port.
        """
        # Main server socket for listening to new connections
        self.socket = None

        self.selector = selectors.DefaultSelector()
        
        # Set host and port, using defaults if not provided
        self.host = host if host else self.DEFAULT_HOST
        self.port = port if port else self.DEFAULT_PORT

    def start(self):
        """
        Starts the non-blocking server and begins monitoring for connections.
        """
        # Create a new TCP/IP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set the main socket to non-blocking mode.
        self.socket.setblocking(False)

        self.addr = (self.host, self.port)

        try:
            # Bind the socket to the specified host and port
            self.socket.bind(self.addr)
        except socket.error as error:
            # Gracefully handle a bind error (e.g., port already in use)
            print(f"Bind failed. \nError Code: {str(error[0])} \nMessage: {str(error[1])}")
            sys.exit()
        
        # Put the socket in a listening state, with a backlog of 5 pending connections
        self.socket.listen(5)

        self.selector.register(self.socket, selectors.EVENT_READ)

        print(f"Server listening on {self.host}:{self.port}")

