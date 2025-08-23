import socket

# sr1 stands for "send and receive one".
from scapy.all import IP, TCP, sr1

class PortScanner():
    """
    A simple port scanner class that uses Scapy to determine if a port is open, closed, or filtered.
    """
    # Define default values for the target and port if they are not provided.
    DEFAULT_TARGET = socket.gethostbyname(socket.gethostname())
    DEFAULT_PORT = 80

    def __init__(self, target: str = None, port: int = None):
        """
        Initializes the PortScanner with a target IP and a port to scan.
        :param target: The IP address or hostname to scan.
        :param port: The port number to scan on the target.
        """
        # Assign the target and port, using defaults if necessary.
        self.target = target if target else self.DEFAULT_TARGET
        self.port = port if port else self.DEFAULT_PORT

    def scan_port(self):
        """
        This method performs a single port scan on the initialized target and port.
        It crafts a SYN packet, sends it, and analyzes the response.
        """
        # Create the IP layer of the packet with the destination set to our target.
        target_ip = IP(dst=self.target)

        # Create the TCP layer of the packet.
        # dport: Sets the destination port to the one we want to scan.
        # flags="S": Sets the SYN flag, indicating this is a connection request.
        tcp_packet = TCP(dport=self.port, flags="S")

        # Combine the IP and TCP layers using the '/' operator to build the complete packet.
        syn_packet = target_ip / tcp_packet

        # Send the packet and wait for a response.
        # sr1(): Sends the packet and returns the first response.
        # timeout=1: Sets a 1-second timeout for the response.
        response = sr1(syn_packet, timeout=1, verbose=0) # verbose=0 suppresses the output

        # If response is None, it means no packet was received (possible timeout).
        if not response: 
            print(f"Oops! Possible timeout error. The port {self.port} might be filtered.")
        # If the response contains a SYN/ACK ("SA") flag, the port is open.
        elif response[TCP].flags == "SA":
            print(f"✅ The port {self.port} is open.")
        # If the response contains a RST/ACK ("RA") flag, the port is closed.
        elif response[TCP].flags == "RA":
            print(f"❌ The port {self.port} is closed.")