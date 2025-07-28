import socket
import threading


class PortScanner:
    def __init__(self, target_host: str = "localhost"):
        """
        Initializes the PortScanner with a target host.
        """
        self.target_ip = self.resolve_host(target_host)  # Resolve the hostname to an IP address.

        # Define the default range of ports to scan.
        # These can be modified when the PortScanner object is created or before scanning.
        self.start_port = 1
        self.end_port = 1024 # Common ports often fall within this range

        # List to hold open ports found during the scan.
        self.open_ports:list[int] = []

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

    def scan_port(self, port: int) -> bool:
        """
        Scans a single port on the target IP address.
        Attempts to establish a TCP connection to determine if the port is open.
        :param port: The port number to scan.
        :return: True if the port is open, False otherwise.
        """

        # Acquire a semaphore to limit the number of concurrent scans.
        self.scan_semaphore.acquire()

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

            output = {"state": False, "port": port, "error": None}

            if result == 0:
                # If result is 0, the connection was successful, meaning the port is open.
                
                # Acquire the lock to safely modify the open_ports list.
                self.open_ports_lock.acquire()

                try:
                    # Append the open port to the list of open ports.
                    self.open_ports.append(port)
                except Exception as e:
                    # Catch any exceptions that occur while modifying the list.
                    print(f"Error while adding port {port} to open_ports: {e}")
                finally:
                    # Ensure the lock is released after modifying the list.
                    self.open_ports_lock.release()
                
                # Update the output dictionary to indicate the port is open.
                output.update({"state": True, "port": port})
            else:
                # If result is non-zero, the connection failed, meaning the port is closed or filtered.
                # The specific error code can provide more details (e.g., 10061 for Connection Refused, 10035 for operation would block/timeout).
                output.update({"state": False, "port": port, "error": result})
        except socket.gaierror:
            # Handles cases where the hostname (IP address) cannot be resolved.
            output.update({"state": False, "port": port, "error": "Hostname resolution failed"})
        except socket.error as e:
            # Catches other socket-related errors (e.g., network unreachable).
            output.update({"state": False, "port": port, "error": str(e)})
        finally:
            # Ensures the socket is always closed, regardless of whether an error occurred.
            # This releases the system resources used by the socket.
            s.close()

            # Release the semaphore to allow another thread to proceed with its scan.
            self.scan_semaphore.release()

            # Return the result of the port scan (True if open, False if closed).
            return output

    def scan_range(self):
        """
        Scans a range of ports from `self.start_port` to `self.end_port` (inclusive)
        on the target IP address, using threads for concurrency.
        """
        # Create an iterable range of port numbers.
        # The range function's end is exclusive, so we add 1 to include self.end_port.
        port_range = range(self.start_port, self.end_port + 1)

        print(f"\n[*] Starting scan on {self.target_ip} from port {self.start_port} to {self.end_port}...")

        # Initialize a list to hold the thread objects.
        all_threads:list[threading.Thread] = []

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

        self.open_ports.sort()  # Sort the list of open ports for better readability.

        # After all threads have completed, print the results.
        print(f"\n[*] Scan complete on {self.target_ip}. Found {len(self.open_ports)} open ports:")

        if self.open_ports:
            for port in self.open_ports:
                print(f"Port {port} is open.")
        else:
            print(f"No open ports found from {self.start_port} to {self.end_port}.")