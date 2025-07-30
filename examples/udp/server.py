import socket


class Server():
    """A simple UDP server that listens for messages and echoes them back."""

    # Server address
    HOST = 'localhost'

    # Server port
    PORT = 12345

    # Buffer size for receiving data
    BUFFER_SIZE = 1024

    def __init__(self):
        # Set up the server address and port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.HOST, self.PORT))

    def start(self):
        # Added a print statement for confirmation
        print(f"UDP Server listening on {self.HOST}:{self.PORT}")

        # Main loop to listen for incoming messages
        while True:
            # Receiving data from the client
            data, address = self.socket.recvfrom(self.BUFFER_SIZE)

            # Decoding and printing
            print(f"[i] Received from {address}: {data.decode()}")

            # Echoing the received message back to the client
            response = f"[i] We received your data: {data.decode()}"

            # Sending the response back to the client
            self.send(response, address)

    def send(self, message:str, address:str):
        try:
            # Sending a message to the specified address
            self.socket.sendto(message.encode(), address)

            # Added a print statement for confirmation
            print(f"[i] Sent to {address}: {message}")
        except Exception as e:
            # Print an error message if sending fails
            print(f"[!] Error sending message: {e}")