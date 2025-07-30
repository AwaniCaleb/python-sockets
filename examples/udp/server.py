import socket


class Server():
    """A simple UDP server that listens for messages and echoes them back."""

    # Server address
    HOST = 'localhost'

    # Server port
    PORT = 12345

    # Buffer size for receiving data
    BUFFER_SIZE = 1024

    def __init__(self):
        # Set up the server address and port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.HOST, self.PORT))

        # Set the server to running state
        self.running = True

    def start(self):
        # Added a print statement for confirmation
        print(f"UDP Server listening on {self.HOST}:{self.PORT}")

        try:
            # Main loop to listen for incoming messages
            while self.running:
                # Receiving data from the client
                data, address = self.socket.recvfrom(self.BUFFER_SIZE)

                # Decoding and printing
                print(f"[i] Received from {address}: {data.decode()}")

                # Decode the received data
                data = data.decode()

                # Check if the received data is a command to stop the server
                if data.lower() in ["!exit", "!quit", "!stop", "!close", "!shutdown"]:
                    self.stop()
                    break

                # Echoing the received message back to the client
                response = f"[i] We received your data: {data}"

                # Sending the response back to the client
                self.send(response, address)
        except Exception as e:
            print(f"[!] Error: {e}")
        finally:
            # Close the socket when done
            self.socket.close()

            print("[i] Server closed.")

    def stop(self):
        """Stop the server."""
        self.running = False
        print("[i] Stopping the server...")

    def send(self, message:str, address:str):
        try:
            # Sending a message to the specified address
            self.socket.sendto(message.encode(), address)

            # Added a print statement for confirmation
            print(f"[i] Sent to {address}: {message}")
        except Exception as e:
            # Print an error message if sending fails
            print(f"[!] Error sending message: {e}")

if __name__ == "__main__":
    # Create a server instance and start it
    server = Server()
    server.start()