import socket
import threading

from .server import Server  # Assuming Server is defined in server.py

class Client:
    # Initialize class-level attributes
    HEADER, SERVER, PORT, DISCONNECT_MESSAGE, FORMAT = None, None, None, None, None

    def __init__(self):
        # Initialize client attributes using the Server class
        self.HEADER = Server.HEADER
        self.SERVER = Server.SERVER
        self.PORT = Server.PORT
        self.DISCONNECT_MESSAGE = Server.DISCONNECT_MESSAGE
        self.FORMAT = Server.FORMAT

        # Create a TCP/IP socket for the client
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Start the server in a separate thread
        self.server = Server()  # Create a server instance
        server_thread = threading.Thread(target=self.server.start)  # Run the server's start method in a thread
        server_thread.start()  # Start the server thread

        # Connect the client to the server
        self.client.connect((self.SERVER, self.PORT))  # Pass the server address (IP and port)

        print("[C][CLIENT CONNECTED] Connected to the server")

    def send(self, message:str) -> None:
        """Send a message to the server."""
        if message.strip() is None or "": return

        # Encode the message and send it to the server
        message = message.encode(self.FORMAT)
        self.client.send(message)

        # Print the sent message for debugging
        print(f"[C][MESSAGE SENT] {message.decode(self.FORMAT)}")

    def disconnect(self):
        """Send a disconnect message to the server."""
        self.send(self.DISCONNECT_MESSAGE)  # Notify the server to disconnect
        self.client.close()  # Close the client socket
        print("[C][CLIENT DISCONNECTED] Connection closed")