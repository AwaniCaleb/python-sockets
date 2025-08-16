import struct
import socket

from .IpHeader import IpHeader
from .PacketHeader import PacketHeader
from .ImcpHeader import IcmpHeader

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

    def create_tcp_header(self, source_port: int, dest_port: int, sequence_number: int, acknowledgment_number: int,) -> bytes:
        offset_res_flags = 80
        window_size = 5840
        tcp_checksum = 0
        urgent_pointer = 0

        tcp_header = struct.pack(
            "!HHLLHHHH",
            source_port, dest_port,
            sequence_number, acknowledgment_number,
            offset_res_flags, window_size,
            tcp_checksum, urgent_pointer,
        )

        return tcp_header

    def create_pseudo_header(self, source_ip: str, dest_ip: str, protocol: int, tcp_length: int) -> bytes:
        # Create a pseudo header for TCP checksum calculation.
        source_ip_binary = socket.inet_aton(source_ip)
        dest_ip_binary = socket.inet_aton(dest_ip)
        zero = 0

        pseudo_header = struct.pack(
            "!4s4sBH",
            source_ip_binary, dest_ip_binary,
            protocol, tcp_length
        )

        return pseudo_header

    def calculate_tcp_checksum(self, tcp_header: bytes, pseudo_header: bytes, user_data: bytes) -> int:
        """"""
        # Calculate the TCP checksum using the pseudo header, TCP header, and user data.
        checksum_data = pseudo_header + tcp_header + user_data

        if len(checksum_data) % 2 != 0:
            # If the length is odd, pad with a zero byte
            checksum_data += b"\x00"
        checksum_sum = 0
        for i in range(0, len(checksum_data), 2):
            # Unpack each 2-byte chunk as an unsigned short
            checksum_sum += struct.unpack("!H", checksum_data[i : i + 2])[0]
        while (checksum_sum >> 16) > 0:
            # Fold the checksum sum to 16 bits
            checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)

        # Finalize the checksum by inverting the bits
        final_checksum = ~checksum_sum & 0xFFFF

        return final_checksum

    def send_packet(self, source_address: str, dest_address: str, message: str, packet_type: str = "icmp", ) -> None:
        user_data = message.encode("utf-8")
        header_payload = b""
        protocol = 0

        if packet_type == "icmp":
            icmp_header_obj = IcmpHeader(id=12345, seq=1)
            header_payload = icmp_header_obj.pack()
            protocol = 1
        elif packet_type == "tcp":
            tcp_length = 20 + len(user_data)
        
            # Create TCP header without checksum for calculation
            tcp_header_no_checksum = self.create_tcp_header(source_port, dest_port, 0, 0)
            
            # Create pseudo-header and calculate TCP checksum
            pseudo_header = self.create_pseudo_header(source_address, dest_address, 6, tcp_length)
            tcp_checksum = self.calculate_tcp_checksum(tcp_header_no_checksum, pseudo_header, user_data)
            
            # Repack TCP header with the correct checksum
            header_payload = struct.pack("!HHLLHHHH", source_port, dest_port, 0, 0, 80, 5840, tcp_checksum, 0)
            protocol = 6 # TCP protocol
            total_packet_length = 20 + len(header_payload) + len(user_data)
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
        packet_sender.send_packet(
            source_address,
            dest_address,
            source_port,
            dest_port,
            message,
            packet_type="icmp",
        )
