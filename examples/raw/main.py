# Comments by GitHub Copilot
import socket
import struct

class Main():
    """
    This class is responsible for creating and sending a raw network packet.
    I am building the packet manually, byte by byte, which is what a raw socket allows. PAY ATTENTION!!!
    """
    def __init__(self, interface: str = 'lo'):
        """
        Initializes the Main class and creates a raw socket.
        
        Args:
            interface (str): The network interface to bind the socket to.
                             'lo' is the loopback interface, which is good for testing
                             on your own machine.
        """
        try:
            # I create a raw socket.
            # socket.AF_INET: I am using the IPv4 protocol.
            # socket.SOCK_RAW: I am creating a raw socket, which gives us
            #                  full control over the packet headers.
            # socket.IPPROTO_IP: I tell Windows to build the IP header for us.
            #                    On Linux, I would use socket.IPPROTO_TCP for TCP packets.
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
            print("Socket created successfully.")
        except socket.error as e:
            print(f"Socket could not be created. Error: {e}")
            self.socket = None

    def calculate_checksum(self, header: bytes) -> int:
        """
        Calculates the IP header checksum.

        The checksum is a simple sum of all the 16-bit words in the header,
        used to detect errors in transit.
        """
        # The checksum starts at 0.
        checksum = 0
        
        # I process the header in chunks of 2 bytes at a time.
        for i in range(0, len(header), 2):
            # I take a 2-byte chunk from the header.
            chunk = header[i:i+2]
            
            # The '!H' format tells struct.unpack to interpret these two bytes
            # as a single 16-bit number, which I then add to the total sum.
            checksum += struct.unpack("!H", chunk)[0]

        # The sum might be too large for a 16-bit number (it "overflows").
        # This loop wraps the overflow back into the sum until it fits.
        # This is a specific requirement of the IP checksum algorithm.
        while (checksum >> 16) > 0:
            # I add the overflow (the bits that are "too big") to the rest of the sum.
            checksum = (checksum & 0xFFFF) + (checksum >> 16)

        # Finally, I take the one's complement of the result.
        # The '~' operator flips all the bits from 0 to 1 and vice-versa.
        # The '& 0xFFFF' part ensures the number stays within 16 bits.
        checksum = ~checksum & 0xFFFF
        
        return checksum

    def create_ip_header(self, source_address: str, dest_address: str) -> bytes:
        """
        Creates an IP header for the packet.
        The IP header is the "outer box" that gets the packet to the right computer.
        """
        # Define the values for each field in the IP header
        version_ihl = 69 # Version 4, IHL (Internet Header Length) 5 (20 bytes)
        total_length = 0 # This is a placeholder; I'll update it later
        identification = 54321
        fragment_offset = 0
        time_to_live = 255
        protocol = 6 # The number for the TCP protocol
        header_checksum = 0 # I must set this to 0 when I calculate the checksum

        # Convert human-readable IP addresses to 4-byte binary format
        source_ip = socket.inet_aton(source_address)
        dest_ip = socket.inet_aton(dest_address)
        
        # Pack the header initially with a checksum of 0.
        ip_header_no_checksum = struct.pack(
            "!BHHHBBH4s4s", # The format string matching the variables
            version_ihl, total_length,
            identification, fragment_offset,
            time_to_live, protocol,
            header_checksum, source_ip,
            dest_ip
        )
        
        # Calculate the correct checksum using the header with a zeroed-out checksum.
        calculated_checksum = self.calculate_checksum(ip_header_no_checksum)
        
        # Pack the header a second time with the correct checksum value.
        ip_header = struct.pack(
            "!BHHHBBH4s4s",
            version_ihl, total_length,
            identification, fragment_offset,
            time_to_live, protocol,
            calculated_checksum, source_ip,
            dest_ip
        )
        
        return ip_header

    def create_tcp_header(self, source_port: int, dest_port: int, sequence_number: int, acknowledgment_number: int) -> bytes:
        """
        Creates a TCP header.
        This is the "inner box" that gets the message to the right application.
        """
        # Define the values for each field in the TCP header
        # '!HHLLHHHH' is the format string: H=16-bit, L=32-bit
        # I set the checksum to 0 for now so I can calculate it later.
        
        offset_res_flags = 80 # A simple value for an ACK packet
        window_size = 5840
        tcp_checksum = 0 # Placeholder for now
        urgent_pointer = 0

        # Pack the TCP header using the format string and variables
        tcp_header = struct.pack(
            "!HHLLHHHH",
            source_port, dest_port,
            sequence_number, acknowledgment_number,
            offset_res_flags, window_size,
            tcp_checksum, urgent_pointer
        )

        return tcp_header
    
    def create_pseudo_header(self, source_ip: str, dest_ip: str, protocol: int, tcp_length: int) -> bytes:
        """
        Creates the pseudo-header required for the TCP checksum calculation.
        This is a temporary "scratch paper" that is not sent with the packet.
        """
        # I need to get the IP addresses as 4-byte binary data
        source_ip_binary = socket.inet_aton(source_ip)
        dest_ip_binary = socket.inet_aton(dest_ip)
        
        # I also need a zero byte and the protocol number, plus the TCP length
        zero = 0
        
        # Pack all the pieces into the pseudo-header.
        # Format string is '!4s4sBH': 4s=4-byte string, B=1-byte, H=2-byte.
        pseudo_header = struct.pack(
            "!4s4sBH",
            source_ip_binary,
            dest_ip_binary,
            protocol,
            tcp_length
        )

        return pseudo_header

    def calculate_tcp_checksum(self, tcp_header: bytes, pseudo_header: bytes, user_data: bytes) -> int:
        """
        Calculates the TCP checksum using the pseudo-header, TCP header, and data.
        """
        # Combine all the pieces I need to checksum
        checksum_data = pseudo_header + tcp_header + user_data
        
        # Pad with a null byte if the length is odd to ensure a 16-bit checksum
        if len(checksum_data) % 2 != 0:
            checksum_data += b'\x00'

        checksum_sum = 0
        
        # Run the checksum algorithm (same as for the IP header)
        for i in range(0, len(checksum_data), 2):
            checksum_sum += struct.unpack("!H", checksum_data[i:i+2])[0]

        # Handle overflow
        while (checksum_sum >> 16) > 0:
            checksum_sum = (checksum_sum & 0xFFFF) + (checksum_sum >> 16)

        # Take the one's complement
        final_checksum = ~checksum_sum & 0xFFFF
        
        return final_checksum

    def send_packet(self, source_address: str, dest_address: str, source_port: int, dest_port: int, message: str) -> None:
        """
        Assembles and sends a complete raw packet.
        This function brings all the previous functions together.
        """
        # The data I want to send
        user_data = message.encode('utf-8')
        tcp_length = 20 + len(user_data) # TCP header is 20 bytes long
        
        # Create the IP header
        ip_header = self.create_ip_header(source_address, dest_address)
        
        # Create a TCP header with the checksum set to 0.
        # I need this version to calculate the correct checksum.
        tcp_header_no_checksum = self.create_tcp_header(source_port, dest_port, 0, 0)
        
        # Create the pseudo-header
        pseudo_header = self.create_pseudo_header(source_address, dest_address, 6, tcp_length)
        
        # Calculate the TCP checksum
        tcp_checksum = self.calculate_tcp_checksum(tcp_header_no_checksum, pseudo_header, user_data)
        
        # Repack the TCP header with the correct checksum
        # I create the final TCP header here, with the correct checksum value
        tcp_header = struct.pack(
            "!HHLLHHHH",
            source_port, dest_port,
            0, 0, # Using 0 for sequence and ack for this simple example
            80, 5840,
            tcp_checksum, 0
        )
        
        # Combine all the pieces to form the final packet
        # Order is crucial: IP header -> TCP header -> user data
        final_packet = ip_header + tcp_header + user_data
        
        # Send the packet!
        try:
            self.socket.sendto(final_packet, (dest_address, 0))
            print("Packet sent successfully!")
        except Exception as e:
            print(f"Error sending packet: {e}")

if __name__ == '__main__':
    source_address = "127.0.0.1"
    dest_address = "127.0.0.1"
    source_port = 12345
    dest_port = 80
    message = "Hello, raw socket!"

    # Create an instance of our class
    packet_sender = Main()

    # Call the send_packet method to assemble and send the packet
    packet_sender.send_packet(source_address, dest_address, source_port, dest_port, message)