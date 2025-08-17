from scapy.all import IP, ICMP, sniff


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
        

    def start_sniffing(self, count=5):
        """
        This method starts sniffing packets on the specified interface.
        """
        print(f"Starting to sniff {count} packets on interface: {self.interface if self.interface else 'default'}")

        # Start sniffing packets
        packet_list = sniff(iface=self.interface, count=count, prn=lambda x: x.summary(), store=True)

        # Print the summary of the sniffed packets
        print(f"Sniffed {len(packet_list)} packets:")

        return packet_list

if __name__ == "__main__":
    # Example usage
    sniffer = PacketSniffer()
    sniffer.start_sniffing(count=100)