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
        ip_header_checksum = self.calculate_ip_checksum(ip_header_no_checksum)
        
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

    def create_tcp_header(self, source_port: int, dest_port: int, sequence_number: int, ack_number: int) -> bytes:
        """Create a TCP header for the packet."""
        # TCP header fields in network byte order
        source_port = source_port  # Source port - H (2 bytes/16 bits)
        dest_port = dest_port  # Destination port - H (2 bytes/16 bits)
        sequence_number = sequence_number  # Sequence number - L (4 bytes/32 bits)
        ack_number = ack_number  # Acknowledgment number - L (4 bytes/32 bits)
        # TCP header flags and options
        offset_reserved_flags = 80 # Data offset (5 * 4 = 20 bytes), reserved (0), flags (0x02 for SYN) - H
        window_size = 5840
        tcp_checksum = 0
        urgent_pointer = 0

        tcp_header = struct.pack(
            "!HHLLHHHH",
            source_port, dest_port,
            sequence_number, ack_number,
            offset_reserved_flags, window_size,
            tcp_checksum, urgent_pointer
        )

        return tcp_header

    def calculate_ip_checksum(self, header: bytes) -> int:
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
    
    def calculate_tcp_checksum(self, tcp_header: bytes, pseudo_header: bytes, user_data: bytes) -> int:
        """
        Calculates the TCP checksum using the pseudo-header, TCP header, and data.
        """
        # Combine the headers and data.
        checksum_data = pseudo_header + tcp_header + user_data
        
        # Pad with a null byte if the length is odd.
        if len(checksum_data) % 2 != 0:
            checksum_data += b'\x00'

        checksum_sum = 0
        
        # Run the checksum algorithm.
        for i in range(0, len(checksum_data), 2):
            # Extract 2 bytes at a time.
            chunk = checksum_data[i:i+2]
            # Unpack the chunk as a 16-bit unsigned integer.
            if len(chunk) == 2:
                value = struct.unpack("!H", chunk)[0]  
            else:
                # If the chunk is only 1 byte, pad it with a zero byte.
                value = struct.unpack("!H", chunk + b'\x00')[0]
            # Add the value to the checksum sum.
            checksum_sum += value          

        # Handle overflow
        while (checksum_sum >> 16) > 0:
            checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)

        # Take the one's complement
        final_checksum = ~checksum_sum & 0xFFFF
        
        return final_checksum

    def create_pseudo_header(self, source_address: str, dest_address: str, protocol: int, tcp_length: int) -> bytes:
        """Create a pseudo header for TCP checksum calculation."""
        # Pseudo header fields in network byte order
        source_ip = socket.inet_aton(source_address) # 4s
        dest_ip = socket.inet_aton(dest_address) # 4s
        protocol = protocol # Protocol number (6 for TCP) - B
        tcp_length = tcp_length # Length of TCP header and data - H

        # Pack the pseudo header.
        pseudo_header = struct.pack(
            "!4s4sBH",
            source_ip, dest_ip,
            protocol, tcp_length
        )

        return pseudo_header