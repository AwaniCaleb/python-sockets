import socket


class Client:
    HEADER = 64
    PORT = 9999

    # Use the local machine's IP address for the server by default
    SERVER = socket.gethostbyname(socket.gethostname())

    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!DISCONNECT"

    def __init__(self, server_ip=None, port=None):
        # Initialize client attributes
        self.HEADER = Client.HEADER
        self.SERVER = server_ip if server_ip else Client.SERVER
        self.PORT = port if port else Client.PORT
        self.DISCONNECT_MESSAGE = Client.DISCONNECT_MESSAGE
        self.FORMAT = Client.FORMAT

        # Create a TCP/IP socket for the client
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the client to the server
        self.client.connect((self.SERVER, self.PORT))
        print(f"[C][CLIENT CONNECTED] Connected to the server {self.SERVER}:{self.PORT}")

    def send(self, message:str) -> None:
        """Send a message to the server."""
        # Corrected condition: check for empty or whitespace-only message
        if not message or not message.strip():
            # print("Warning: Attempted to send empty or whitespace message.")
            return

        encoded_message = message.encode(self.FORMAT)
        message_length = len(encoded_message)
        
        # Prepare the header: pad the length with spaces to match HEADER size
        send_length = str(message_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length)) # Pad with spaces

        try:
            self.client.send(send_length) # First, send the length header
            self.client.send(encoded_message)  # Then, send the actual message
            print(f"[C][MESSAGE SENT] {message}") # Print original string

            return True  # Indicate successful send
        except Exception as e:
            print(f"[C][SEND ERROR] Failed to send message '{message}': {e}")
            # Marking the client as disconnected.
            self.client.close() # Close socket

            return False

    def disconnect(self):
        """Send a disconnect message to the server and close the client socket."""
        try:
            self.send(self.DISCONNECT_MESSAGE)  # Notify the server to disconnect
        except Exception as e:
            # If send fails (e.g., connection already broken), just print error
            print(f"[C][DISCONNECT ERROR] Could not send disconnect message: {e}")
        finally:
            self.client.close()  # Always close the client socket
            print("[C][CLIENT DISCONNECTED] Connection closed")