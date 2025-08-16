import socket
import struct
from PacketHeader import PacketHeader


class TcpHeader(PacketHeader):
    """
    Represents and builds a TCP header.
    """

    def __init__(self, source_port: int, dest_port: int, seq_num: int = 0, ack_num: int = 0):
        self.source_port = source_port
        self.dest_port = dest_port
        self.seq_num = seq_num
        self.ack_num = ack_num
    
    def _create_pseudo_header(self, source_ip: str, dest_ip: str, tcp_length: int) -> bytes:
        """
        Creates a pseudo-header for the TCP checksum calculation.
        This is a private helper method.
        """
        source_ip_binary = socket.inet_aton(source_ip)
        dest_ip_binary = socket.inet_aton(dest_ip)

        protocol = 6 # TCP

        pseudo_header = struct.pack(
            "!4s4sBH",
            source_ip_binary, dest_ip_binary,
            protocol, tcp_length
        )

        return pseudo_header
    
    def pack(self, source_ip: str, dest_ip: str, user_data: bytes) -> bytes:
        """
        Packs the TCP header with the correct checksum.
        """
        tcp_header_length = 20 # TCP header is always 20 bytes long
        user_data_length = len(user_data)
        tcp_length = tcp_header_length + user_data_length

        # Start with a zeroed-out checksum for calculation
        tcp_header_no_checksum = struct.pack(
            "!HHLLHHHH",
            self.source_port, self.dest_port,
            self.seq_num, self.ack_num,
            (tcp_header_length << 4) + 0, # Data offset and flags - Still don't know what exactly is happening there but aiit
            5840, # Window size
            0, # Checksum placeholder
            0 # Urgent pointer
        )

        # Create the pseudo-header
        pseudo_header = self._create_pseudo_header(source_ip, dest_ip, tcp_length)

        # Combine everything for the checksum calculation
        checksum_data = pseudo_header + tcp_header_no_checksum + user_data

        # Calculate the checksum using the inherited method
        tcp_checksum = self.calculate_checksum(checksum_data)

        # Repack with the correct checksum
        tcp_header = struct.pack(
            "!HHLLHHHH",
            self.source_port, self.dest_port,
            self.seq_num, self.ack_num,
            (tcp_header_length << 4) + 0, # Data offset and flags
            5840, # Window size
            tcp_checksum, # The correct checksum
            0 # Urgent pointer
        )

        return tcp_header