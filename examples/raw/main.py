import socket


class Main():
    """Main class for the raw socket interactions."""
    HOST = 'localhost'
    PORT = 12345

    def __init__(self, host: str = None, port: int = None):
        """Initialize the Main class with optional host and port."""
        # Set the host and port, using defaults if not provided
        self.host = host or self.HOST
        self.port = port or self.PORT

        # Create a raw socket for ICMP packets
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, 1)