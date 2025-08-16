import struct

class PacketHeader:
    """
    Base class for all network packet headers.
    It contains common functionality like checksum calculation.
    """
    def calculate_checksum(self, header: bytes) -> int:
        """
        Calculates the checksum for a given header.
        """
        checksum = 0
        
        if len(header) % 2 != 0:
            header += b'\x00'

        for i in range(0, len(header), 2):
            chunk = header[i:i+2]
            checksum += struct.unpack("!H", chunk)[0]

        while (checksum >> 16) > 0:
            checksum = (checksum & 0xFFFF) + (checksum >> 16)

        checksum = ~checksum & 0xFFFF
        
        return checksum