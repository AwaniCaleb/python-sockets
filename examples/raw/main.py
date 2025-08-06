import socket
import struct # For packing and unpacking binary data


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

    def create_ip_header(self, source_address: str, dest_address: str) -> bytes:
        """Create an IP header for the packet."""
        version_ihl = 69 # Version 4, IHL 5 (20 bytes) - B
        total_length = 0 # Placeholder for total length - H
        identification = 54321 # Identification number - H
        fragment_offset = 0 # Fragment offset - H
        time_to_live = 255 # TTL - B
        protocol = 6 # TCP protocol - B
        header_checksum = 0 # We'll calculate this later - H

        source_ip = socket.inet_aton(source_address) # Convert source address to binary format - 4s
        dest_ip = socket.inet_aton(dest_address) # Convert destination address to binary format - 4s
        
        # Pack the header with the checksum set to 0.
        ip_header_no_checksum = struct.pack(
            "!BHHHBBH4s4s",
            version_ihl, total_length,
            identification, fragment_offset,
            time_to_live, protocol,
            header_checksum, source_ip,
            dest_ip
        )
        
        # Calculate the checksum for the IP header.
        ip_header_checksum = self.calculate_checksum(ip_header_no_checksum)
        
        # Repack the header with the correct checksum.
        ip_header = struct.pack(
            "!BHHHBBH4s4s",
            version_ihl, total_length,
            identification, fragment_offset,
            time_to_live, protocol,
            ip_header_checksum, source_ip,
            dest_ip
        )
        
        return ip_header

    def calculate_checksum(self, header: bytes) -> int:
        """
        Calculates the IP header checksum.

        The checksum is a simple sum of all the 16-bit words in the header,
        used to detect errors in transit. Very complex,
        but essential for network reliability so we have lots of comments
        """
        # The checksum starts at 0.
        checksum = 0
        
        # We process the header in chunks of 2 bytes at a time.
        # The range() function is perfect for this, as it steps by 2.
        for i in range(0, len(header), 2):
            # We take a 2-byte chunk from the header.
            chunk = header[i:i+2]
            
            # The '!H' format tells struct.unpack to interpret these two bytes
            # as a single 16-bit number, which we then add to our total sum.
            checksum += struct.unpack("!H", chunk)[0]

        # The sum might be too large for a 16-bit number (it "overflows").
        # This loop wraps the overflow back into the sum until it fits.
        # This is a specific requirement of the IP checksum algorithm.
        while (checksum >> 16) > 0:
            # We add the overflow (the bits that are "too big") to the rest of the sum.
            checksum = (checksum & 0xFFFF) + (checksum >> 16)

        # Finally, we take the one's complement of the result.
        # The '~' operator flips all the bits from 0 to 1 and vice-versa.
        # The '& 0xFFFF' part ensures the number stays within 16 bits.
        checksum = ~checksum & 0xFFFF
        
        return checksum