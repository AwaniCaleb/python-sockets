import socket
from scapy.all import IP, TCP, sr1

class PortScanner():
    DEFAULT_TARGET = socket.gethostbyname(socket.gethostname())
    DEFAULT_PORT = 80

    def __init__(self, target: str, port: int):
        self.socket = None
        self.target = target if target else self.DEFAULT_TARGET
        self.port = port if port else self.DEFAULT_PORT

    def scan_port(self):
        target_ip = IP(dst=self.target)
        tcp_packet = TCP(dport=self.port, flags="S")

        syn_packet = target_ip / tcp_packet

        response = sr1(syn_packet, timeout=1)

        