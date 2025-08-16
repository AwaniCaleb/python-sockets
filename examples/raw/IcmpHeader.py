import struct
from PacketHeader import PacketHeader

class IcmpHeader(PacketHeader):
    """
    Represents and builds an ICMP header for an echo request.
    """
    def __init__(self, type_code: int = 8, code: int = 0, id: int = 12345, seq: int = 1):
        self.type_code = type_code
        self.code = code
        self.id = id
        self.seq = seq

    def pack(self) -> bytes:
        """
        Packs the ICMP header with the correct checksum.
        """
        # Start with a zeroed-out checksum for calculation
        icmp_header_no_checksum = struct.pack(
            "!BBHHH",
            self.type_code, self.code,
            0, self.id, self.seq
        )
        
        # The ICMP checksum is calculated on the header itself
        calculated_checksum = self.calculate_checksum(icmp_header_no_checksum)
        
        # Repack the header with the correct checksum
        icmp_header = struct.pack(
            "!BBHHH",
            self.type_code, self.code,
            calculated_checksum, self.id, self.seq
        )
        
        return icmp_header