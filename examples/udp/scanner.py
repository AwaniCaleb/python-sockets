import socket


class Scanner():
    """A simple UDP scanner that checks if specific ports on a target host are open."""

    target_host: str = "localhost"  # Target host to scan
    target_ports: list = [42, 53, 67, 123, 161, 162, 3389]  # List of ports to scan

    # List to store the results of the scan
    sockets: list[dict] = []

    def __init__(self, target_host: str = None, target_ports: list = None):
        """Initialize the UDP scanner with a target host and ports to scan."""
        self.target_host = target_host or self.target_host
        self.target_ports = target_ports or self.target_ports

        self.scan()

    def scan(self) -> list[dict]:
        """Scan the target host for open UDP ports and return the results."""

        for port in self.target_ports:
            current_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            current_socket.settimeout(1.0)  # Set a timeout for receiving a response

            status = "Unknown" # Default status
            response_data = None # Default response data

            try:
                # Send a probe message to the target host on the specified port
                message = "scan_probe"
                current_socket.sendto(message.encode(), (self.target_host, port))

                # Wait for a response from the server
                response, addr = current_socket.recvfrom(1024)

                # If a response is received, mark the port as open
                status = "Open/Responding"
                response_data = response.decode()
                print(f"[+] Port {port} is {status} on {self.target_host}. Response: {response_data} from {addr}")

            except socket.timeout:
                # If a timeout occurs, the port is likely closed or filtered
                status = "Filtered/No Response"
                print(f"[-] Port {port} is {status} on {self.target_host}.")

            except socket.error as e:
                # Handle socket errors, such as connection issues
                if e.errno == 10054: # Specific error code for "Connection forcibly closed"
                    status = "Closed (ICMP Port Unreachable)"
                    print(f"[-] Port {port} is {status} on {self.target_host}.")
                else:
                    status = f"Error: {e.errno}" # Catch other socket errors
                    response_data = str(e)
                    print(f"[!] Error with port {port}: {e}")

            except Exception as e:
                # Catch any other unexpected errors
                status = "Error"
                response_data = str(e)
                print(f"[!] General error with port {port}: {e}")
            finally:
                current_socket.close()

            # Store the result for the current port
            self.sockets.append({
                "port": port,
                "is_open": True if "Open" in status else False,
                "response": response_data,
                "status": status
            })

        return self.sockets


if __name__ == "__main__":
    scanner_localhost = Scanner("localhost")

    for item in scanner_localhost.sockets:
        print(f"Port {item['port']}: {item['status']} - Response: {item['response'] if item['response'] else 'N/A'}")
