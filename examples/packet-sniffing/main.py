from scapy.all import IP, ICMP, sniff, TCP, UDP


class PacketSniffer:
    """
    A simple packet sniffer class that uses Scapy to create and manipulate network packets.
    """

    def __init__(self, interface: str = None):
        """This initializes the PacketSniffer with an optional network interface."""

        self.interface = interface
        if self.interface:
            print(f"PacketSniffer initialized on interface: {self.interface}")
        else:
            print("PacketSniffer initialized without a specific interface.")
        

    def start_sniffing(self, count: int = 5, filter: str = None):
        """
        This method starts sniffing packets on the specified interface.
        """
        print(f"Starting to sniff {count} packets on interface: {self.interface if self.interface else 'default'}")

        # Start sniffing packets
        packet_list = sniff(iface=self.interface, count=count, prn=lambda x: self.process_packet(x), store=True, filter= filter if filter is not None else "")

        # Print the summary of the sniffed packets
        print(f"Sniffed {len(packet_list)} packets:")

        return packet_list
    
    def process_packet(self, packet):
        """This method processes each packet and prints the source and destination IP addresses if available."""

        default_value = "Unknown"
        src_ip, dst_ip, src_port, dst_port = [default_value] * 4

        # Check if the packet has IP layer
        if IP in packet:
            # Extract source and destination IP addresses
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
        
        if TCP in packet:
            # Check if the packet has a source and destination port
            src_port = packet[TCP].sport if hasattr(packet[TCP], 'sport') else None
            dst_port = packet[TCP].dport if hasattr(packet[TCP], 'dport') else None
        elif UDP in packet:
            # Check if the packet has a source and destination port
            src_port = packet[UDP].sport if hasattr(packet[UDP], 'sport') else None
            dst_port = packet[UDP].dport if hasattr(packet[UDP], 'dport') else None

        print(f"Packet from {src_ip}:{src_port} to {dst_ip}:{dst_port}")

if __name__ == "__main__":
    # Example usage
    sniffer = PacketSniffer()
    sniffer.start_sniffing(count=1, filter="udp port 53")