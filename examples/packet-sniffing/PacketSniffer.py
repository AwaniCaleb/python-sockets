from scapy.all import IP, ICMP, sniff, TCP, UDP, DNSQR


class PacketSniffer:
    """
    A simple packet sniffer class that uses Scapy to create and manipulate network packets.
    """

    def __init__(self, interface: str = None):
        """
        This initializes the PacketSniffer with an optional network interface.
        :param interface: The network interface to sniff on (e.g., 'eth0', 'Wi-Fi').
                          If not specified, Scapy will use the default interface.
        """
        self.interface = interface
        if self.interface:
            print(f"PacketSniffer initialized on interface: {self.interface}")
        else:
            print("PacketSniffer initialized without a specific interface.")
        

    def start_sniffing(self, count: int = 5, filter: str = None):
        """
        This method starts sniffing packets on the specified interface.
        :param count: The number of packets to capture.
        :param filter: A BPF (Berkeley Packet Filter) string to filter the packets.
                       This allows capturing only specific traffic (e.g., "tcp port 80").
        """
        print(f"Starting to sniff {count} packets on interface: {self.interface if self.interface else 'default'}")

        # Start sniffing packets using the sniff() function.
        # iface: Specifies the network interface.
        # count: The total number of packets to capture before stopping.
        # prn: A callback function that is executed for every packet captured.
        #      We use a lambda function here to call our process_packet method.
        # store: Set to True to store the captured packets in a list.
        # filter: Applies the BPF filter to only capture packets of interest.
        packet_list = sniff(iface=self.interface, count=count, prn=lambda x: self.process_packet(x), store=True, filter= filter if filter is not None else "")

        # Print a summary of the sniffing session.
        print(f"Sniffed {len(packet_list)} packets:")

        return packet_list
    
    def process_packet(self, packet):
        """
        This method processes each packet and prints the source and destination details if available.
        It acts as the callback function for the sniff() method.
        """

        default_value = "Unknown"
        src_ip, dst_ip, src_port, dst_port = [default_value] * 4

        # Check if the packet has an IP layer.
        if IP in packet:
            # Extract the source and destination IP addresses from the IP layer.
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
        
        # Check if the packet has a TCP layer and extract the ports.
        if TCP in packet:
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
        # If it's not TCP, check for a UDP layer and extract the ports.
        elif UDP in packet:
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
        
        # Print the general packet information.
        print(f"Packet from {src_ip}:{src_port} to {dst_ip}:{dst_port}")

        # Check if the packet has a DNS query layer (DNSQR).
        # This is an application-layer check to find specific traffic.
        if DNSQR in packet:
            # Print a custom message for DNS queries, including the domain name.
            print(f"DNS Query detected from {src_ip} for: {packet[DNSQR].qname.decode()}")


if __name__ == "__main__":
    # Create an instance of the PacketSniffer class.
    sniffer = PacketSniffer()
    # Start sniffing, capturing 10 DNS packets (udp port 53 is the DNS filter).
    sniffer.start_sniffing(count=10, filter="udp port 53")