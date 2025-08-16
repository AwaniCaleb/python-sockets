import socket
import struct
from PacketHeader import PacketHeader

class IpHeader(PacketHeader):
    """
    Represents and builds an IPv4 header.
    """
    def __init__(self, source_address: str, dest_address: str, protocol: int, total_length: int):
        self.source_address = source_address
        self.dest_address = dest_address
        self.protocol = protocol
        self.total_length = total_length
        self.version_ihl = 69
        self.tos = 0
        self.identification = 54321
        self.fragment_offset = 0
        self.time_to_live = 255
    
    def pack(self) -> bytes:
        """
        Packs the IP header with the correct checksum.
        """
        header_checksum = 0
        source_ip = socket.inet_aton(self.source_address)
        dest_ip = socket.inet_aton(self.dest_address)

        # Pack once with a zeroed-out checksum
        ip_header_no_checksum = struct.pack(
            "!BBHHHBBH4s4s",
            self.version_ihl, self.tos,
            self.total_length, self.identification,
            self.fragment_offset, self.time_to_live,
            self.protocol, header_checksum,
            source_ip, dest_ip
        )
        
        # Calculate the checksum
        calculated_checksum = self.calculate_checksum(ip_header_no_checksum)
        
        # Repack with the correct checksum
        ip_header = struct.pack(
            "!BBHHHBBH4s4s",
            self.version_ihl, self.tos,
            self.total_length, self.identification,
            self.fragment_offset, self.time_to_live,
            self.protocol, calculated_checksum,
            source_ip, dest_ip
        )
        
        return ip_header