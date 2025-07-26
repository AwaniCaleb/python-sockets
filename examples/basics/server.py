import socket
import threading

class Server:
    # Header size for messages
    HEADER = 64

    # Port to listen on (non-privileged ports are > 1023)
    PORT = 9999

    # Get the local machine's IP address
    SERVER = socket.gethostbyname(socket.gethostname())

    # Address to listen on (server IP and port)
    ADDR = (SERVER, PORT)

    # Encoding format for messages
    FORMAT = 'utf-8'

    # Disconnect message to close the connection
    DISCONNECT_MESSAGE = "!DISCONNECT"

    def __init__(self):
        # Create a TCP/IP socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the address and port   
        self.server.bind(self.ADDR)

        print(f"[S][SERVER INITIALIZED] Server bound to {self.ADDR}")

    def start(self):
        """Start listening for incoming connections."""
        self.server.listen()  # Start listening for connections
        print(f"[S][SERVER LISTENING] Listening on {self.SERVER}:{self.PORT}")

        while True:
            # Wait for a connection
            connection, address = self.server.accept()
            print(f"[S][NEW CONNECTION] {address} connected")

            # Create a new thread for each client connection
            thread = threading.Thread(target=self.handle_client, args=(connection, address))
            thread.start()

            # Print the number of active connections
            print(f"[S][ACTIVE CONNECTIONS] {threading.active_count() - 1}")

    def handle_client(self, connection, address):
        """Handle communication with a connected client."""
        connected = True  # Flag to indicate the connection is active

        while connected:
            try:
                # Receive the message length header
                message_length = connection.recv(self.HEADER).decode(self.FORMAT)

                if message_length:
                    # Receive the actual message
                    message = connection.recv(int(message_length)).decode(self.FORMAT)

                    if message == self.DISCONNECT_MESSAGE:
                        connected = False  # Disconnect if the message is the disconnect signal

                    print(f"[S][{address}] {message}")
            except:
                connected = False  # Handle any errors gracefully

        # Close the connection when done
        connection.close()
        print(f"[S][DISCONNECTED] {address} disconnected")