import struct
import socket

from .IpHeader import IpHeader
from .PacketHeader import PacketHeader
from .ImcpHeader import IcmpHeader
from .TcpHeader import TcpHeader

class Main:
    def __init__(self, interface: str = "lo"):
        try:
            self.socket = socket.socket(
                socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP
            )
            print("Socket created successfully.")
        except socket.error as e:
            print(f"Socket could not be created. Error: {e}")
            self.socket = None

    def send_packet(self, source_address: str, dest_address: str, message: str, packet_type: str = "icmp", source_port: int = 12345, dest_port: int = 80,) -> None:
        user_data = message.encode("utf-8")
        header_payload = b""
        protocol = 0

        if packet_type == "icmp":
            icmp_header_obj = IcmpHeader(id=12345, seq=1)
            header_payload = icmp_header_obj.pack()
            protocol = 1
        elif packet_type == "tcp":
            tcp_header_obj = TcpHeader(source_port, dest_port)
            header_payload = tcp_header_obj.pack(source_address, dest_address, user_data)
            protocol = 6
            pass
        else:
            raise ValueError("Unsupported packet type. Use 'tcp' or 'icmp'.")

        # Create the IP header
        total_packet_length = 20 + len(header_payload) + len(user_data)

        ip_header_obj = IpHeader(source_address, dest_address, protocol, total_packet_length)
        ip_header = ip_header_obj.pack()

        final_packet = ip_header + header_payload + user_data

        try:
            self.socket.sendto(final_packet, (dest_address, 0))
            print("Packet sent successfully!")
        except Exception as e:
            print(f"Error sending packet: {e}")


if __name__ == "__main__":
    source_address = "127.0.0.1"
    dest_address = "127.0.0.1"
    source_port = 12345
    dest_port = 80
    message = "Hello, raw socket!"

    packet_sender = Main()

    if packet_sender.socket:
        print("\n--- Sending ICMP Packet ---")
        packet_sender.send_packet(
            source_address,
            dest_address,
            message,
            packet_type="icmp",
        )
        print("\n--- Sending TCP Packet ---")
        packet_sender.send_packet(
            source_address,
            dest_address,
            message,
            packet_type="tcp",
            source_port=source_port,
            dest_port=dest_port
        )