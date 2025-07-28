import socket
import threading


class PortScanner:
    def __init__(self, target_ip: str = "127.0.0.1"):
        """
        Initializes the PortScanner with a target IP address.
        :param target_ip: The IP address of the host to scan. Defaults to localhost (127.0.0.1).
        """
        self.target_ip = target_ip

        # Define the default range of ports to scan.
        # These can be modified when the PortScanner object is created or before scanning.
        self.start_port = 1
        self.end_port = 1024 # Common ports often fall within this range

    def scan_port(self, port: int) -> bool:
        """
        Scans a single port on the target IP address.
        Attempts to establish a TCP connection to determine if the port is open.
        :param port: The port number to scan.
        :return: True if the port is open, False otherwise.
        """
        # Create a new socket for each connection attempt.
        # It's crucial to create a new socket because a closed socket cannot be reused.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set a timeout for the connection attempt.
        # This prevents the scanner from hanging indefinitely on filtered or non-responsive ports.
        s.settimeout(1) # 1 second timeout

        try:
            # Attempt to connect to the target IP and port.
            # connect_ex() returns 0 on success (connection established),
            # or a non-zero error code if the connection fails.
            result = s.connect_ex((self.target_ip, port))

            if result == 0:
                # If result is 0, the connection was successful, meaning the port is open.
                print(f"Port {port} is OPEN")
                return True
            else:
                # If result is non-zero, the connection failed, meaning the port is closed or filtered.
                # The specific error code can provide more details (e.g., 10061 for Connection Refused, 10035 for operation would block/timeout).
                print(f"Port {port} is CLOSED (Error: {result})")
                return False
        except socket.gaierror:
            # Handles cases where the hostname (IP address) cannot be resolved.
            print("Hostname could not be resolved. Exiting.")
            return False
        except socket.error as e:
            # Catches other socket-related errors (e.g., network unreachable).
            print(f"Couldn't connect to server: {e}")
            return False
        finally:
            # Ensures the socket is always closed, regardless of whether an error occurred.
            # This releases the system resources used by the socket.
            s.close()

    def scan_range(self):
        """
        Scans a range of ports from `self.start_port` to `self.end_port` (inclusive)
        on the target IP address.
        """
        # Create an iterable range of port numbers.
        # The range function's end is exclusive, so we add 1 to include self.end_port.
        port_range = range(self.start_port, self.end_port + 1) # Added + 1 to include end_port

        print(f"\n[*] Starting scan on {self.target_ip} from port {self.start_port} to {self.end_port}...")

        try:
            # Iterate through each port in the defined range.
            for port in port_range:
                # Call the scan_port method for each individual port.
                self.scan_port(port)
        except Exception as e:
            # Catch any unexpected errors that might occur during the iteration or individual scans.
            print(f"Something went wrong during the port range scan: {e}")

        print(f"[*] Scan on {self.target_ip} completed.")