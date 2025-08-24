import sys, os
from PacketSniffer import PacketSniffer
from PortScanner import PortScanner

def main():
    """
    An interactive runner for the Scapy examples.
    Allows the user to choose between running the Packet Sniffer or the Port Scanner.
    """
    # Check for root privileges, as Scapy often requires them for raw socket access.
    # Note: This is a simple check and might not be foolproof on all OSes.
    # A more robust solution might use `os.geteuid()` on Unix-like systems.
    # For this educational repo, a simple check is sufficient.
    if sys.platform != "win32" and os.geteuid() != 0:
        print("\n[!] This script may require root privileges to run correctly.")
        print("Please try running with 'sudo'.\n")
        # Depending on strictness, you might want to exit here.
        sys.exit(1)

    while True:
        print("\n--- Scapy Examples Runner ---")
        print("Please choose an example to run:")
        print("  1. Packet Sniffer")
        print("  2. Port Scanner (Scapy-based)")
        print("  q. Quit")

        choice = input("Enter your choice (1, 2, or q): ").strip().lower()

        if choice == '1':
            run_packet_sniffer()
            break
        elif choice == '2':
            run_port_scanner()
            break
        elif choice == 'q':
            print("Exiting.")
            break
        else:
            print("\n[!] Invalid choice. Please try again.")

def run_packet_sniffer():
    """
    Initializes and runs the Packet Sniffer example.
    """
    print("\n--- Running Packet Sniffer ---")
    try:
        # You can customize the interface, count, and filter here if needed.
        sniffer = PacketSniffer()
        print("Starting to sniff 10 packets on the default interface...")
        print("Filter: udp port 53 (DNS)\n")
        sniffer.start_sniffing(count=10, filter="udp port 53")
        print("\nSniffing complete.")
    except Exception as e:
        print(f"\n[!] An error occurred while running the packet sniffer: {e}")
        print("Please ensure you are running with sufficient privileges (e.g., 'sudo').")

def run_port_scanner():
    """
    Initializes and runs the Scapy-based Port Scanner example.
    """
    print("\n--- Running Port Scanner (Scapy-based) ---")
    try:
        target_host = input("Enter the target host (e.g., scanme.nmap.org): ").strip()

        # Validate if the user entered a host
        if not target_host:
            print("[!] Target host cannot be empty.")
            return

        port_str = input("Enter the port to scan (e.g., 80): ").strip()

        # Validate if the port is a valid integer
        try:
            port = int(port_str)
            if not (1 <= port <= 65535):
                raise ValueError("Port out of range.")
        except ValueError:
            print("[!] Invalid port. Please enter a number between 1 and 65535.")
            return

        print(f"\nScanning {target_host} on port {port}...")
        scanner = PortScanner(target=target_host, port=port)
        scanner.scan_port()
        print("\nScan complete.")

    except Exception as e:
        print(f"\n[!] An error occurred while running the port scanner: {e}")
        print("Please ensure you are running with sufficient privileges (e.g., 'sudo').")

if __name__ == "__main__":
    main()