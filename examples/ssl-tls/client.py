import socket
import ssl
import time

class Client():
    SERVER_HOST: str = 'localhost'
    SERVER_PORT: int = 9999
    ADDR = (SERVER_HOST, SERVER_PORT)

    def __init__(self, svr_host: str = None, svr_port: int = None):
        print("[i] Initializing SSL/TLS Client...")
        print("[i] Please provide the server's information to connect securely. Press Enter to use defaults.")

        # Prompt the user for server IP and port, allowing them to use defaults if they wish.
        svr_host = input("[i] Enter server ip (default: localhost): ") if svr_host is None else svr_host
        svr_port = input("[i] Enter server port (default: 9999): ") if svr_port is None else svr_port

        # Set the server host and port, using defaults if not provided.
        self.SERVER_HOST = svr_host if svr_host else self.SERVER_HOST
        self.SERVER_PORT = int(svr_port) if svr_port else self.SERVER_PORT
        self.ADDR = (self.SERVER_HOST, self.SERVER_PORT)

        # Initialize the socket and other necessary variables.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_running = False
        self.secure_socket = None

    def start(self):
        try:
            # Create an SSLContext for verifying the server's certificate.
            self.context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            self.context.load_verify_locations(cafile="./id/cert.pem")

            # Wrap the socket with the secure context before connecting.
            self.secure_socket = self.context.wrap_socket(self.socket, server_hostname=self.SERVER_HOST)
            
            # Connect to the server. This performs the TLS handshake.
            self.secure_socket.connect(self.ADDR)
            print(f"[i] Connected securely to {self.SERVER_HOST}:{self.SERVER_PORT}")
            
            self.is_running = True

            while self.is_running:
                message = input("Enter message to send (or '!exit' to quit): ")

                if message == "!exit":
                    self.stop()
                    break

                # Send the encoded message to the server.
                self.secure_socket.sendall(message.encode('utf-8'))

                # Wait for the server's response.
                response = self.secure_socket.recv(1024)

                if not response:
                    print("[!] No response from server. Connection may have been closed or it didn't G.A.F.")
                    self.stop()
                    break
                else:
                    print(f"Received from server: {response.decode('utf-8')}")

        except ssl.SSLError as e:
            print(f"[!] SSL Error during connection: {e}")
        except socket.error as e:
            print(f"[!] Socket Error: {e}")
        finally:
            self.stop()

    def stop(self):
        """Stop the client by closing the secure socket and setting the running state to False."""
        if not self.is_running:
            return

        self.is_running = False

        if self.secure_socket:
            self.secure_socket.close()
            print("[i] Secure connection closed.")

if __name__ == "__main__":
    client = Client()
    client.start()