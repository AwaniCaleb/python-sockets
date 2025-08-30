import sys
import socket
import selectors

class Server():
    """
    A non-blocking TCP server that handles multiple clients concurrently
    using the modern `selectors` module for efficient I/O multiplexing.
    """
    DEFAULT_HOST = '127.0.0.1'
    DEFAULT_PORT = 65432

    def __init__(self, host: str = None, port: int = None) -> None:
        """
        Initializes the server with a host, port, and a selector object.
        """
        self.socket = None

        # Object for monitoring all sockets
        self.selector = selectors.DefaultSelector()

        self.host = host if host else self.DEFAULT_HOST
        self.port = port if port else self.DEFAULT_PORT

    def start(self):
        """
        Sets up and starts the non-blocking server.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setblocking(False)

        self.addr = (self.host, self.port)

        try:
            self.socket.bind(self.addr)
        except socket.error as error:
            print(f"Bind failed. \nError Code: {str(error[0])} \nMessage: {str(error[1])}")
            sys.exit()

        self.socket.listen(5)
        # Register the main server socket with the selector for read events.
        # This tells the selector to notify when a new connection is ready to be accepted.
        self.selector.register(self.socket, selectors.EVENT_READ)
        
        print(f"Server listening on {self.host}:{self.port}")

        # The main event loop
        while True:
            # selector.select() blocks until one or more registered sockets have a pending event.
            events = self.selector.select(timeout=None)
            for key, mask in events:
                sock = key.fileobj
                # If the ready socket is our main server socket, it means a new client is connecting.
                if sock is self.socket:
                    self.accept(sock)
                # Otherwise, it's an existing client socket with data to be read.
                else:
                    self.read(sock)

    def accept(self, sock: socket.socket):
        """
        Accepts a new client connection and registers the new client socket with the selector.
        """
        try:
            # accept() returns a new socket object for the client and its address.
            conn, addr = sock.accept()
            print(f"Accepted connection from {addr}")
            
            # The new client socket must be set to non-blocking
            conn.setblocking(False)
            
            # Register the *new* client socket for read events.
            self.selector.register(conn, selectors.EVENT_READ)
        except Exception as e:
            print(f"Error accepting connection: {e}")

    def read(self, conn: socket.socket):
        """
        Reads data from a client socket and echoes it back. Handles client disconnections.
        """
        try:
            # Attempt to receive data from the client
            data = conn.recv(1024)
            if data:
                message = data.decode()
                print(f"Received message: {message}")

                # Echo the message back to the client
                conn.sendall(data)
            else:
                # An empty recv result means the client has closed the connection gracefully.
                print(f"Closing connection from {conn.getpeername()}")

                # Unregister the socket from the selector
                self.selector.unregister(conn)

                conn.close()

        except BlockingIOError:
            # This is an expected and safe error to ignore in non-blocking code.
            pass
        except Exception as e:
            # Handle any other errors and clean up the socket.
            print(f"Error handling client data: {e}")

            self.selector.unregister(conn)
            conn.close()