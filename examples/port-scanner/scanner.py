import socket
import threading


class PortScanner:
    def __init__(self, target_host: str = "localhost", verbose:bool = False):
        """
        Initializes the PortScanner with a target host.
        """
        # Resolve the hostname to an IP address.
        self.target_ip = self.resolve_host(
            target_host
        )

        # Define the default range of ports to scan.
        # These can be modified when the PortScanner object is created or before scanning.
        self.start_port = 1
        self.end_port = 1024

        # Verbose mode determines whether to print detailed output during the scan.
        self.verbose = verbose

        # List to hold open ports found during the scan.
        self.open_ports: list[dict] = []

        # Maximum number of concurrent connections (threads) to use during scanning.
        self.max_connections = 100

        # This semaphore limits the number of concurrent threads to avoid overwhelming the system or network.
        self.scan_semaphore = threading.Semaphore(self.max_connections)

        # A lock to ensure thread-safe access to the open_ports list.
        self.open_ports_lock = threading.Lock()

    def resolve_host(self, host: str) -> str:
        """
        Resolves a hostname to an IP address.
        """
        try:
            # Use socket.gethostbyname() to resolve the hostname to an IP address.
            ip_address = socket.gethostbyname(host)
            return ip_address
        except socket.gaierror:
            print(f"Could not resolve hostname {host}. Exiting.")
            return ""

    def scan_port(self, port: int) -> dict:
        """
        Scans a single port on the target IP address, attempts to grab a banner if open.
        """

        self.scan_semaphore.acquire()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)  # Timeout for connection attempt

        output = {
            "state": False,
            "port": port,
            "error": None,
            "data": None,
        }  # Initialize output

        try:
            result = s.connect_ex((self.target_ip, port))

            if result == 0:
                # Port is open
                print("Open port found:", port)
                output["state"] = True

                banner = "No banner received"  # Default banner if none found or error

                # Set a shorter timeout specifically for the recv operation
                s.settimeout(0.5)

                try:
                    port_data_bytes = s.recv(1024)
                    # Decode the received data dnd remove leading/trailing whitespace/newlines
                    banner = port_data_bytes.decode("utf-8", errors="ignore").strip()
                    if not banner:  # If decoding results in an empty string
                        banner = "No banner received"
                except socket.timeout:
                    # Specific handler for recv timeout
                    banner = "No banner received (timeout)"
                except socket.error as e:
                    # General socket error during recv
                    banner = f"Error receiving banner: {e}"

                output["data"] = banner

                # Acquire the lock to safely modify the open_ports list.
                self.open_ports_lock.acquire()

                try:
                    # Use 'banner' key for clarity
                    self.open_ports.append({"port": port, "banner": banner})
                finally:
                    # Ensure the lock is released after modifying the list.
                    self.open_ports_lock.release()

            else:
                # Port is closed or filtered
                output["error"] = result

                # Print port if verbose is enabled
                if self.verbose:
                    print(f"Closed/Filtered port found: {port}")

        except socket.gaierror:
            # Hostname resolution failed during connect_ex or earlier
            output["error"] = "Hostname resolution failed"
        except socket.error as e:
            # Other socket-related errors during connect_ex
            output["error"] = str(e)
        finally:
            s.close()
            self.scan_semaphore.release()
            return output

    def scan_range(self):
        """
        Scans a range of ports from `self.start_port` to `self.end_port` (inclusive)
        on the target IP address, using threads for concurrency.
        """
        # Create an iterable range of port numbers.
        # The range function's end is exclusive, so we add 1 to include self.end_port.
        port_range = range(self.start_port, self.end_port + 1)

        print(
            f"\n[*] Starting scan on {self.target_ip} from port {self.start_port} to {self.end_port}..."
        )

        # Initialize a list to hold the thread objects.
        all_threads: list[threading.Thread] = []

        try:
            # Iterate through each port in the defined range.
            for port in port_range:
                # Acquire the semaphore before starting a new thread to ensure we don't exceed max_connections.
                # self.scan_semaphore.acquire() # Already called in scan_port method

                # Create a new thread for each port scan.
                # The 'target' is the function to be executed by the thread (self.scan_port).
                # The 'args' is a tuple of arguments to pass to the target function (the current 'port').
                scan_thread = threading.Thread(target=self.scan_port, args=(port,))

                # Start the thread, which will execute self.scan_port concurrently.
                scan_thread.start()

                # Append the thread to the list of threads for tracking.
                all_threads.append(scan_thread)

            for thread in all_threads:
                thread.join()

        except Exception as e:
            # Catch any unexpected errors that might occur during the thread creation or iteration.
            print(f"Something went wrong during the port range scan: {e}")

        # Sort the list of open ports by their port number for better readability.
        self.open_ports.sort(key=lambda x: x['port'])

        # After all threads have completed, print the results.
        print(
            f"\n[*] Scan complete on {self.target_ip}. Found {len(self.open_ports)} open ports:"
        )

        # If there are open ports, print each one.
        if self.open_ports:
            for open_port in self.open_ports:
                print(f"Port {open_port['port']} is open. Banner: {open_port['banner']}") # Changed 'data' to 'banner'
        else:
            print(f"No open ports found from {self.start_port} to {self.end_port}.")
