import socket
import ssl


class Client():
    SERVER_HOST = 'localhost'  # The server's hostname or IP address
    SERVER_PORT = 9999  # The port used by the server

    ADDR = (SERVER_HOST, SERVER_PORT) 

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_running = False 
        self.secure_socket = None

    def start(self):
        # Create an SSLContext object with the purpose of connecting to a server.
        self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)

        # Load the server's certificate to verify its identity.
        self.context.load_verify_locations(cafile="./id/cert.pem")

        # Wrap the socket with the secure context.
        self.secure_socket = self.context.wrap_socket(self.socket, server_hostname=self.SERVER_HOST)

        # Connect to the server using the secure socket.
        self.secure_socket.connect(self.ADDR)
        
        print(f"Connected securely to {self.SERVER_HOST}:{self.SERVER_PORT}")

        # Set the running state to True to indicate the client is active.
        self.is_running = True