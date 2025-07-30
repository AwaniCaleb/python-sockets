import socket

from time import sleep


class Client():
    """A simple UDP client that sends messages to a server and receives responses."""

    # Server address to connect to
    HOST:str = "localhost"

    # The port number for the client to connect to the server
    PORT:int = 12345

    # Buffer size for receiving data
    BUFFER_SIZE = 1024

    # Address tuple for the server
    ADDR = (HOST, PORT)

    def __init__(self):
        # Create a UDP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send_message(self, message: str):
        """Send a message to the server."""
        try:
            # Send the message to the server
            self.socket.sendto(message.encode(), self.ADDR)
            print(f"Sent message: {message}")

            # Receive a response from the server
            response, _ = self.socket.recvfrom(self.BUFFER_SIZE)
            print(f"Received response: {response.decode()}\n{_}")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Create a client instance
    client = Client()

    # Example messages to send to the server
    messages = [
        "Hello, Server!",
        "How are you?",
        "This is a test message.",
        "Goodbye!",
        "!exit"
    ]

    # Send each message and wait for a response
    for msg in messages:
        sleep(1)  # Sleep for a second between messages
        client.send_message(msg)