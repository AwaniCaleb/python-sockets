import argparse, sys
from flooder import Flooder

def main():
    """
    Main entry point for the UDP Flooder application.
    Handles command-line arguments and initiates the flooding process.
    """
    parser = argparse.ArgumentParser(
        description="UDP Flooder Tool for Offensive Security.",
        formatter_class=argparse.RawTextHelpFormatter # help text formatting
    )

    parser.add_argument("-th", "--target-host", type=str, help="The target IP address or hostname to flood (e.g., 127.0.0.1 or example.com)")
    parser.add_argument("-tp", "--target-port", type=int, help="The target port number to flood (e.g., 80 or 53)")
    parser.add_argument("-m", "--message", type=str, default="ATTACK!", help="The message payload to send in each UDP packet.\nDefault: 'ATTACK!'")
    parser.add_argument("-c", "--count", type=int, default=-1, help="Number of packets to send. Use -1 for infinite (default).")

    args = parser.parse_args()

    try:
        flooder = Flooder(
            target_host=args.target_host,
            target_port=args.target_port,
            message=args.message
        )
        
        flooder.start(packet_count=args.count)

    except ValueError as ve:
        print(f"[!] Configuration Error: {ve}")
        sys.exit(1) # Exit with an error code for invalid configuration
    except Exception as e:
        print(f"[!] An unexpected error occurred: {e}")
        sys.exit(1) # Exit with an error code for general errors


if __name__ == "__main__":
    main()
