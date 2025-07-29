import socket, random, threading, os


class Client:
    HEADER = 64
    PORT =  os.environ.get("NGROK_PUBLIC_PORT")

    # Use the local machine's IP address for the server by default
    # SERVER = socket.gethostbyname(socket.gethostname())
    SERVER = os.environ.get("NGROK_PUBLIC_HOSTNAME")

    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!DISCONNECT"

    def __init__(self, server_ip=None, port=None, name=None):
        # Initialize client attributes
        self.HEADER = Client.HEADER
        self.SERVER = server_ip if server_ip else Client.SERVER
        self.PORT = port if port else Client.PORT
        self.DISCONNECT_MESSAGE = Client.DISCONNECT_MESSAGE
        self.FORMAT = Client.FORMAT
        self.name = name if name else f"Client_{random.randint(10000, 99999)}"

        # Create a TCP/IP socket for the client
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False # Flag to track client connection status

        try:
            # Connect the client to the server
            self.client.connect((self.SERVER, self.PORT))
            self.connected = True
            print(f"[C][CLIENT CONNECTED] Connected to the server {self.SERVER}:{self.PORT}")

            # --- Start a separate thread to receive messages ---
            # This thread will continuously listen for data from the server
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()

        except Exception as e:
            print(f"[C][ERROR] Could not connect to server {self.SERVER}:{self.PORT}: {e}")
            self.connected = False # Connection failed

    def _receive_messages(self):
        """Internal method for the client to continuously receive messages from the server."""
        while self.connected:
            try:
                # Receive the message length header
                message_length_header = self.client.recv(self.HEADER)
                
                # If recv returns 0 bytes, the server has closed its side of the connection gracefully
                if not message_length_header:
                    print("[C][SERVER DISCONNECTED] Server closed connection or sent no data.")
                    self.connected = False # Mark as disconnected
                    break # Exit the loop

                # Decode and parse the message length
                message_length = int(message_length_header.decode(self.FORMAT).strip())
                
                # Receive the actual message data
                received_message = self.client.recv(message_length).decode(self.FORMAT)
                
                # Print the received message to the client's console
                print(f"{received_message}")
                # Use sys.stdout.write and sys.stdout.flush for clean output when using input()
                # import sys
                # sys.stdout.write(f"\n[RECEIVED] {received_message}\n{self.name}: ")
                # sys.stdout.flush()

            except ConnectionResetError:
                # This error occurs if the server forcefully closes the connection
                print("[C][DISCONNECTED] Server forcefully closed connection.")
                self.connected = False
                break # Exit the loop
            except ValueError as ve:
                # Error if the received header is not a valid integer
                print(f"[C][RECEIVE ERROR] Invalid message length header: {ve}")
                self.connected = False
                break
            except Exception as e:
                # Catch any other unexpected errors during reception
                print(f"[C][RECEIVE ERROR] An unexpected error occurred during reception: {e}")
                self.connected = False
                break
        
        # Cleanup when the receive loop exits (due to disconnect or error)
        try:
            # Ensure the socket is closed if it wasn't already
            if self.client: # Check if client socket exists
                self.client.shutdown(socket.SHUT_RDWR) # Attempt graceful shutdown
                self.client.close()
                print("[C][CLIENT RECEIVE LOOP END] Socket closed.")
        except OSError as e:
            # Socket might already be closed or in an uncloseable state
            print(f"[C][CLEANUP ERROR] Error closing socket in receive loop: {e}")


    def send(self, message:str) -> bool:
        """Send a message to the server."""
        # Check if the client is currently connected before attempting to send
        if not self.connected:
            print("[C][SEND ERROR] Not connected to server. Cannot send message.")
            return False

        # Corrected condition: check for empty or whitespace-only message
        if not message or not message.strip():
            # print("Warning: Attempted to send empty or whitespace message.")
            return False
        
        # Prepend the client's name to the message for identification on the server/other clients
        message_with_name = f"[{self.name}] {message}" 

        # Encode the message and calculate its length
        encoded_message = message_with_name.encode(self.FORMAT)
        message_length = len(encoded_message)
        
        # Prepare the header: pad the length with spaces to match HEADER size
        send_length = str(message_length).encode(self.FORMAT)
        send_length += b' ' * (self.HEADER - len(send_length)) # Pad with spaces

        try:
            # Use sendall for reliability to ensure all bytes are sent
            self.client.sendall(send_length)      # First, send the length header
            self.client.sendall(encoded_message)  # Then, send the actual message
            print(f"{self.name}: {message}") # Print original string as typed by user/application
            return True # Indicate successful send
        except Exception as e:
            print(f"[C][SEND ERROR] Failed to send message '{message}': {e}")
            self.connected = False # Mark client as disconnected on send failure
            try:
                self.client.close() # Close socket to clean up connection
            except OSError:
                pass # Already closed
            return False

    def disconnect(self):
        """Send a disconnect message to the server and close the client socket."""
        if not self.connected:
            print("[C][DISCONNECT] Already disconnected. No need to close.")
            return

        try:
            # Attempt to send the disconnect message
            # The 'send' method will internally set self.connected=False and close the socket if it fails.
            if self.send(self.DISCONNECT_MESSAGE):
                print("[C][CLIENT DISCONNECTED] Disconnect message sent.")
            else:
                print("[C][CLIENT DISCONNECTED] Could not send disconnect message (already disconnected?).")
        except Exception as e:
            print(f"[C][DISCONNECT ERROR] Problem during disconnect sequence: {e}")
        finally:
            # Ensure connected flag is false and socket is closed, regardless of send success
            self.connected = False
            try:
                if self.client: # Ensure self.client exists before attempting to close
                    self.client.shutdown(socket.SHUT_RDWR) # Attempt graceful shutdown
                    self.client.close()
            except OSError:
                pass # Socket might already be closed
            print("[C][CLIENT DISCONNECTED] Connection closed.")


# Removed the default main() function, as the primary use case will be from your project's main.py
# If you want to run this client interactively, uncomment the main block below.

def interactive_main():
    # Example instantiation, can be removed if not needed or you want to use this class in another script.

    print("[CONFIG] Enter server IP and port to connect to the server.\n")

    inputted_ip = input("IP (default local machine): ").strip()
    inputted_port_str = input("Port (default 9999): ").strip()
    
    # Use default values if input is empty
    server_ip = inputted_ip if inputted_ip else Client.SERVER
    port = int(inputted_port_str) if inputted_port_str else Client.PORT
    
    client_name = input("Enter a name for this client (enter to skip): ").strip()

    cli = Client(server_ip=server_ip, port=port, name=client_name)

    # Check if connection was successful
    if not cli.connected:
        print("[CLIENT INITIALIZATION FAILED] Exiting.")
        return

    print(f"\n[CLIENT INITIALIZED] Client ready to send messages as '{cli.name}'. Type '!DISCONNECT' to exit\n")

    # Accept message input from user
    while cli.connected: # Loop as long as client is connected
        try:
            # message = input(f"{cli.name}: ")
            message = input()
            if message == "!DISCONNECT":
                # cli.send("Left the connection.") # Optional: notify server before disconnecting
                cli.disconnect()
                break
            cli.send(message)
        except EOFError: # Handles Ctrl+D/Ctrl+Z (end of input)
            print("\n[CLIENT] End of input detected. Disconnecting.")
            cli.disconnect()
            break
        except Exception as e:
            print(f"[CLIENT INTERACTIVE ERROR] {e}")
            cli.disconnect()
            break

    print("[CLIENT] Interactive session ended.")

if __name__ == "__main__":
    interactive_main() # Uncomment to run the client directly for testing

