import socket
import threading
import os
from datetime import datetime


class PortScanner:
    """
    A multi-threaded TCP Port Scanner.

    This class provides functionality to scan a range of TCP ports on a target host,
    identify open ports, grab banners from open services, and optionally output
    results to a file. It uses threading and a semaphore to manage concurrent connections.
    """

    def __init__(self, target_host: str = "localhost", verbose: bool = False, output_file_path: str = None):
        """
        Initializes the PortScanner with a target host and scan settings.

        :param target_host: The hostname or IP address of the target. Defaults to "localhost".
        :param verbose: If True, prints status for every port scanned (open, closed, filtered).
        :param output_file_path: The path to a file where results should be saved.
                                 Can be None (no output file), a specific path, or 'auto_generate'
                                 to trigger automatic filename generation.
        """
        # Store the provided target host string.
        self.target_host = target_host

        # Resolve the hostname to an IP address immediately upon initialization.
        # This handles DNS resolution upfront and stores the IP.
        self.target_ip = self.resolve_host(self.target_host)

        # Default range of ports to scan. These can be overridden via main.py arguments.
        self.start_port = 1
        self.end_port = 1024

        # Verbose mode flag. True means more detailed real-time output.
        self.verbose = verbose

        # Store the provided output file path. This will be None, a path string, or 'auto_generate'.
        self.output_file_path = output_file_path

        # List to store information about open ports. Each item will be a dictionary
        # containing the port number and any grabbed banner.
        self.open_ports: list[dict] = []

        # Maximum number of concurrent connections/threads.
        # This is the initial default, but can be updated by main.py's arguments.
        self.max_connections = 100

        # A threading.Semaphore limits the number of active threads.
        # It's initialized here with a default, but critically, it's re-initialized
        # in main.py after potentially receiving a new max_connections value.
        self.scan_semaphore = threading.Semaphore(self.max_connections)

        # A threading.Lock is used to protect 'self.open_ports' when multiple threads
        # try to add data to it simultaneously, preventing race conditions.
        self.open_ports_lock = threading.Lock()

    def resolve_host(self, host: str) -> str:
        """
        Resolves a given hostname to its corresponding IP address.

        :param host: The hostname (e.g., "google.com") or IP address (e.g., "8.8.8.8").
        :return: The resolved IP address as a string, or an empty string if resolution fails.
        """
        try:
            # socket.gethostbyname() performs the DNS lookup.
            ip_address = socket.gethostbyname(host)
            return ip_address
        except socket.gaierror:
            # socket.gaierror is raised for address-related errors (e.g., unknown host).
            print(f"[!] Error: Could not resolve hostname '{host}'.")
            return "" # Return empty string to signal failure.

    def scan_port(self, port: int) -> dict:
        """
        Scans a single TCP port on the target IP address.
        Attempts to establish a connection and grab a banner if the port is open.

        :param port: The port number to scan.
        :return: A dictionary containing 'port', 'status', and 'data' (banner if open).
        """
        # Acquire a semaphore. This decrements the semaphore counter.
        # If the counter is zero (meaning max_connections threads are already running),
        # this call will block until a semaphore is released by another thread.
        self.scan_semaphore.acquire()

        # Create a new socket for each connection attempt.
        # It's crucial to create a new socket because a closed socket cannot be reused for a new connection.
        # AF_INET specifies IPv4, SOCK_STREAM specifies TCP.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Initialize output dictionary with default values.
        output = {"port": port, "status": "closed", "banner": None}

        try:
            # Set a timeout for the connection attempt.
            # This prevents the scanner from hanging indefinitely on filtered or non-responsive ports.
            s.settimeout(1) # 1 second timeout for connection.

            # Attempt to connect to the target IP and port.
            # connect_ex returns 0 if the connection is successful (port is open).
            # It returns an error code (non-zero) if the connection fails (port is closed/filtered).
            result = s.connect_ex((self.target_ip, port))

            if result == 0:
                # Port is open.
                output["status"] = "open"
                
                # --- Banner Grabbing Attempt ---
                try:
                    # Set a shorter timeout specifically for receiving data (banner).
                    # This prevents hanging if a service connects but sends no data.
                    s.settimeout(0.5) # 0.5 seconds timeout for receiving.

                    # Attempt to receive data (banner) from the open port.
                    # 1024 is the buffer size (max bytes to receive).
                    port_data_bytes = s.recv(1024)

                    # Decode the received bytes into a UTF-8 string.
                    # 'errors="ignore"' handles any decoding errors gracefully, preventing crashes.
                    banner = port_data_bytes.decode("utf-8", errors="ignore").strip()

                    # If no banner data was actually received (e.g., an empty string),
                    # assign a default message.
                    if not banner:
                        banner = "No banner received"
                    output["banner"] = banner

                except socket.timeout:
                    # Catch timeout specifically if the service connects but sends no data within the timeout.
                    output["banner"] = "No banner (timeout)"
                except socket.error as e:
                    # Catch other socket errors during banner grabbing (e.g., connection reset).
                    output["banner"] = f"No banner (error: {e})"
                
                # --- Thread-Safe Update of Open Ports List ---
                # Acquire the lock before modifying the shared 'open_ports' list.
                # This ensures that only one thread modifies the list at a time, preventing data corruption.
                self.open_ports_lock.acquire()
                try:
                    # Add the open port information (port number and banner) to the list.
                    self.open_ports.append({"port": port, "banner": output["banner"]})
                finally:
                    # Release the lock after the list modification is complete.
                    # 'finally' ensures the lock is always released, even if an error occurs.
                    self.open_ports_lock.release()

                # Print status for open ports (always printed, regardless of verbose mode).
                print(f"Port {port} is OPEN. Banner: {output['banner']}")

            else:
                # Port is closed or filtered.
                # Only print this status if verbose mode is enabled.
                if self.verbose:
                    print(f"Port {port} is CLOSED (Error Code: {result})")

        except socket.gaierror:
            # This error is typically caught by resolve_host, but included here for robustness.
            # It means the hostname could not be resolved at this stage.
            if self.verbose:
                print(f"[!] Hostname resolution error during scan for port {port}.")
        except socket.error as e:
            # Catches other general socket-related errors (e.g., network unreachable, connection refused).
            if self.verbose:
                print(f"[!] Socket error for port {port}: {e}")
        finally:
            # Always close the socket.
            # This releases the system resources used by the socket.
            s.close()
            # Release the semaphore. This increments the semaphore counter, allowing
            # another waiting thread to acquire it and start its scan.
            self.scan_semaphore.release()
            return output # Return the output dictionary for potential future use.

    def scan_range(self):
        """
        Orchestrates the scanning of a range of ports using multiple threads.
        It starts threads for each port, waits for them to complete,
        then prints and optionally saves the results.
        """
        # Create an iterable range of port numbers.
        # The 'range' function's end is exclusive, so I add 1 to include 'self.end_port'.
        port_range = range(self.start_port, self.end_port + 1)

        print(f"\n[*] Starting scan on {self.target_ip} from port {self.start_port} to {self.end_port}...")

        # List to keep track of all the thread objects created.
        all_threads: list[threading.Thread] = []

        try:
            # Iterate through each port in the defined range.
            for port in port_range:
                # Create a new thread for each port scan.
                # 'target' is the function the thread will execute (self.scan_port).
                # 'args' is a tuple of arguments passed to the target function (the current 'port').
                scan_thread = threading.Thread(target=self.scan_port, args=(port,))
                
                # Start the thread, which will begin executing self.scan_port concurrently.
                scan_thread.start()

                # Add the newly started thread to our list for tracking.
                all_threads.append(scan_thread)

            # Wait for all threads to complete their execution.
            # .join() on a thread blocks the main thread until that specific thread finishes.
            # By joining all threads, I ensure that the main thread doesn't proceed to
            # print results until all scanning is truly done.
            for thread in all_threads:
                thread.join()

        except Exception as e:
            # Catch any unexpected errors that might occur during the thread creation or iteration.
            print(f"[!] Something went wrong during the port range scan: {e}")

        # Sort the list of open ports by their port number for better readability in the output.
        # The 'key=lambda x: x['port']' sorts based on the 'port' key within each dictionary.
        self.open_ports.sort(key=lambda x: x['port'])

        # After all threads have completed, print the final summary of results.
        output_lines = []
        output_lines.append(f"[*] Scan complete on {self.target_ip}. Found {len(self.open_ports)} open ports:")

        if self.open_ports:
            # If open ports were found, format and add each one to output_lines.
            for open_port in self.open_ports:
                line = f"Port {open_port['port']} is open. Banner: {open_port['banner']}"
                print(line) # Print to console regardless of output file option
                output_lines.append(line)
        else:
            # If no open ports were found in the specified range.
            line = f"No open ports found from {self.start_port} to {self.end_port}."
            print(line) # Print to console
            output_lines.append(line)

        # Write to file if an output path was provided.
        # This check determines if the user requested file output.
        if self.output_file_path:
            # Call the helper method to write the collected output lines to a file.
            self.output_file({"host": self.target_host, "content": output_lines})

    def output_file(self, data: dict) -> bool:
        """
        Handles writing the scan results to a file.
        It can use a user-specified path or generate a timestamped one.

        :param data: A dictionary containing 'host' (target hostname) and 'content' (list of output strings).
        :return: True if the file was successfully written, False otherwise.
        """
        def generate_filename(target_host: str) -> str:
            """
            Generates a unique, timestamped filename for scan results.
            """
            now = datetime.now()
            # Format the date and time including seconds for more uniqueness.
            timestamp_part = now.strftime("%Y-%m-%d_%H-%M-%S")
            # Combine with the target host to create a descriptive filename.
            return f"{timestamp_part}_scan_results_for_{target_host}"

        # Determine the final file path for writing.
        file_path = self.output_file_path

        # If the user passed '-o' without a value, or didn't provide `-o` at all,
        # 'file_path' will be 'auto_generate' or None. In these cases, a generate a filename.
        if file_path == 'auto_generate' or file_path is None:
            # Define the base directory where auto-generated files will be stored.
            base_dir = "port-scanner_results"
            file_extension = ".log" # Standard log file extension.

            # Ensure the base directory exists. If it doesn't, create it.
            # 'exist_ok=True' prevents an error if the directory already exists.
            if not os.path.exists(base_dir):
                try:
                    os.makedirs(base_dir, exist_ok=True)
                except Exception as e:
                    print(f"[!] Error creating output directory '{base_dir}': {e}")
                    return False # Indicate failure to create directory.
            # Construct the full file path for the auto-generated file.
            file_path = os.path.join(base_dir, f"{generate_filename(data['host'])}{file_extension}")

        # Attempt to write the content to the determined file_path.
        try:
            # Open the file in write mode ('w'). This will create the file if it doesn't exist,
            # or overwrite it if it does.
            with open(file_path, "w") as f:
                # Write each line of content, ensuring a newline character is added
                # to separate lines correctly in the file.
                for line in data["content"]:
                    f.write(line + "\n")
            print(f"[*] Scan results successfully saved to: {file_path}")
            return True # Indicate success.
        except Exception as e:
            # Catch any errors during file writing (e.g., permission denied, invalid path).
            print(f"[!] Error writing results to file '{file_path}': {e}")
            return False # Indicate failure.