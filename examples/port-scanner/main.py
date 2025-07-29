import argparse
import threading

# Import the PortScanner class from the scanner module
from scanner import PortScanner


def main():
    """
    Main function to run the port scanner application.
    It handles command-line argument parsing, initializes the scanner,
    and starts the scanning process.
    """

    # 1. Argument Parsing Setup
    # --------------------------------------------------------------------------
    # Create an ArgumentParser object. This object will hold all the information
    # needed to parse the command line into Python data types.
    # The 'description' argument provides a brief help message shown when
    # you runs the script with -h or --help.
    parser = argparse.ArgumentParser(description="A multi-threaded TCP Port Scanner Tool")

    # Add arguments that the script will accept from the command line.

    # --target / -t: Specifies the host (IP address or hostname) to scan.
    # 'type=str' ensures the input is treated as a string.
    # 'default="localhost"' sets a default value if the argument is not provided.
    # 'help' provides a description for the argument in the help message.
    parser.add_argument(
        "-t", "--target", type=str, default="localhost",
        help="Target host to scan (e.g., 'example.com' or '192.168.1.1'). Defaults to 'localhost'."
    )

    # --start-port / -sp: Defines the starting port for the scan range.
    # 'type=int' ensures the input is an integer.
    parser.add_argument(
        "-sp", "--start-port", type=int, default=1,
        help="Starting port for the scan range. Defaults to 1."
    )

    # --end-port / -ep: Defines the ending port for the scan range.
    # 'type=int' ensures the input is an integer.
    parser.add_argument(
        "-ep", "--end-port", type=int, default=1024,
        help="Ending port for the scan range (inclusive). Defaults to 1024."
    )

    # --max-connections / -mc: Limits the number of concurrent connections (threads).
    # This prevents overwhelming the target or the scanning machine.
    # 'type=int' for an integer value.
    parser.add_argument(
        "-mc", "--max-connections", type=int, default=100,
        help="The maximum number of concurrent connections (threads) to use during scanning. Defaults to 100."
    )

    # --verbose / -v: Enables verbose output, showing status for all ports.
    # 'action='store_true'' means this argument is a boolean flag. If it's present
    # on the command line, args.verbose will be True; otherwise, False.
    parser.add_argument(
        "-v", "--verbose", action='store_true',
        help="Enable verbose output. Prints the status of every port (open, closed, or filtered) as it's scanned."
    )

    # --output / -o: Specifies an output file for scan results.
    # 'type=str': Expects a string value (the filename).
    # 'nargs='?'': This is crucial. It means the argument is optional.
    #   - If `-o filename.txt` is given, args.output will be "filename.txt".
    #   - If just `-o` is given (without a filename), `const` value is used.
    # 'const='auto_generate'': The value assigned to `args.output` if `-o` is present
    #   but no value is provided (e.g., `python main.py -o`).
    # 'default=None': The value assigned to `args.output` if `-o` is not present at all.
    parser.add_argument(
        "-o", "--output", type=str, nargs='?', const='auto_generate', default=None,
        help="Specify an output file to save results (e.g., results.txt). If just '-o' is used without a filename, a timestamped file will be created automatically in a 'port-scanner_results' directory."
    )

    # Parse the arguments provided by you from the command line.
    args = parser.parse_args()

    # 2. PortScanner Initialization
    # --------------------------------------------------------------------------
    # Create an instance of the PortScanner class.
    # Pass the parsed target host, verbose flag, and output file path to its constructor.
    # The PortScanner will resolve the hostname to an IP address during its initialization.
    scanner = PortScanner(args.target, args.verbose, args.output)

    # Check if the target host was successfully resolved to an IP address.
    # The resolve_host method in PortScanner returns an empty string if resolution fails.
    if not scanner.target_ip:
        print("[!] Exiting: Target host could not be resolved. Please check the hostname or IP address.")
        return # Exit the script if the target is invalid.

    # 3. Configure Scanner Parameters
    # --------------------------------------------------------------------------
    # Set the port range and maximum concurrent connections based on the parsed arguments.
    # These properties are set directly on the scanner instance.
    scanner.start_port = args.start_port
    scanner.end_port = args.end_port
    scanner.max_connections = args.max_connections

    # Crucial: Re-initialize the semaphore in the scanner.
    # The semaphore is responsible for limiting concurrent threads.
    # It must be re-initialized here because 'max_connections' might have been
    # changed by the command-line argument, overriding its default value set in __init__.
    scanner.scan_semaphore = threading.Semaphore(scanner.max_connections)

    # 4. Start the Scan
    # --------------------------------------------------------------------------
    # Call the scan_range method to begin the port scanning process.
    # This method orchestrates the creation of threads and manages the scan.
    scanner.scan_range()


# 5. Script Entry Point
# --------------------------------------------------------------------------
# This block ensures that the main() function is called only when the script
# is executed directly (not when it's imported as a module into another script).
if __name__ == "__main__":
    main()