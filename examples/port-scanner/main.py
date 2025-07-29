import argparse
import threading

from scanner import PortScanner


def main():
    """Main function to run the port scanner"""

    # Create an argument parser
    parser = argparse.ArgumentParser(description="Port Scanner Tool")

    # Add an argument for the target host
    parser.add_argument("-t", "--target", type=str, default="localhost", help="Target host to scan (default: localhost)")
    
    # Add an argument for the start port
    parser.add_argument("-sp", "--start-port", type=int, default=1, help="Start port for scanning (default: 1)")

    # Add an argument for the end port
    parser.add_argument("-ep", "--end-port", type=int, default=1024, help="End port for scanning (default: 1024)")

    # Add an argument for the max connections
    parser.add_argument("-mc", "--max-connections", type=int, default=100, help="The maximum number of concurrent connections  (default: 100)")

    # Add an argument for the verbose
    parser.add_argument("-v", "--verbose", action='store_true', help="Print the status of every port as it's scanned (default: False)")

    # Parse the arguments
    args = parser.parse_args()

    # Create an instance of PortScanner with the target host
    scanner = PortScanner(args.target, args.verbose)

    if not scanner.target_ip:
        # If target_ip is an empty string, it means resolution failed
        print("[!] Exiting: Target host could not be resolved.")
        return # Exit

    # Set the port range and max connections from the parsed arguments
    scanner.start_port = args.start_port
    scanner.end_port = args.end_port
    scanner.max_connections = args.max_connections
    
    # Crucial: Re-initialize the semaphore with the new max_connections value
    scanner.scan_semaphore = threading.Semaphore(scanner.max_connections)

    # Scan a range of ports
    scanner.scan_range()


if __name__ == "__main__":
    main()