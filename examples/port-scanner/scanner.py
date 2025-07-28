import socket
import threading


class PortScanner:
    def __init__(self, target_ip: str = "127.0.0.1"):
        """
        Initializes the PortScanner with a target IP.
        """
        self.target_ip = target_ip

    def scan_port(self, port: int) -> bool:
        """
        Scans a single port on the target IP.
        Returns True if the port is open, False otherwise.
        """
        # Create a new socket for each connection attempt. Closed socket cannot be reused
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Set a timeout to avoid hanging on ports that are filtered or closed
        s.settimeout(1)

        try:
            # Try to connect to a port. Returns 0 on success, or an error code on failure
            result = s.connect_ex((self.target_ip, port))

            if result == 0:
                print(f"Port {port} is OPEN")  # Port is open if connect_ex returns 0
                return True
            else:
                # Print the error code
                print(f"Port {port} is CLOSED (Error: {result})")
                return False
        except socket.gaierror:
            print("Hostname could not be resolved. Exiting.")
            return False
        except socket.error as e:
            print(f"Couldn't connect to server: {e}")
            return False
        finally:
            # Always close the socket
            s.close()