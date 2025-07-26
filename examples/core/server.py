import socket
import threading

class Server:
    HEADER = 64
    PORT = 9999
    SERVER = socket.gethostbyname(socket.gethostname())
    ADDR = (SERVER, PORT)
    FORMAT = 'utf-8'
    DISCONNECT_MESSAGE = "!DISCONNECT"

    # Keep track of active connections
    _active_connections: set[socket.socket] = set()
    _connection_addresses: dict[socket.socket, tuple] = {}
    _lock = threading.Lock() # To protect access to _active_connections

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        
        print(f"[S][SERVER INITIALIZED] Server bound to {self.ADDR}")

    def start(self):
        self.server.listen()
        print(f"[S][SERVER LISTENING] Listening on {self.SERVER}:{self.PORT}")

        while True:
            try:
                connection, address = self.server.accept()
                with self._lock:
                    self._active_connections.add(connection) # Store ONLY the socket
                    self._connection_addresses[connection] = address # Store address mapping
                print(f"[S][NEW CONNECTION] {address} connected")

                thread = threading.Thread(target=self.handle_client, args=(connection, address))
                thread.daemon = True
                thread.start()

                print(f"[S][ACTIVE CONNECTIONS] {len(self._active_connections)}")

            except Exception as e:
                print(f"[S][SERVER ACCEPT ERROR] {e}")
                break

    def handle_client(self, connection, address):
        connected = True

        while connected:
            try:
                message_length_header = connection.recv(self.HEADER)
                if not message_length_header: # Client disconnected gracefully
                    break

                message_length = int(message_length_header.decode(self.FORMAT).strip())
                received_message = connection.recv(message_length).decode(self.FORMAT)

                if received_message == self.DISCONNECT_MESSAGE:
                    connected = False
                
                print(f"[S][{address}] {received_message}")

                # BROADCAST THE MESSAGE
                if received_message != self.DISCONNECT_MESSAGE: # Don't broadcast disconnect messages
                    self.broadcast_message(connection, received_message)

            except ConnectionResetError:
                print(f"[S][FORCED DISCONNECT] {address} forcefully disconnected.")
                connected = False
            except ValueError as ve: # Catch errors if message_length is not a valid int
                print(f"[S][PROTOCOL ERROR {address}] Invalid message length header: {ve}")
                connected = False
            except Exception as e:
                print(f"[S][ERROR HANDLING {address}] {e}")
                connected = False

        # Client disconnected, clean up
        print(f"[S][DISCONNECTED] {address} disconnected")
        
        with self._lock:
            if connection in self._active_connections:
                self._active_connections.remove(connection)
            if connection in self._connection_addresses:
                del self._connection_addresses[connection]
        try:
            connection.shutdown(socket.SHUT_RDWR) # Attempt graceful shutdown before close
            connection.close()
        except OSError as e:
            print(f"[S][CLOSE ERROR] Error closing socket for {address}: {e}")
        
        print(f"[S][ACTIVE CONNECTIONS] {len(self._active_connections)}")

    def _send_to_single_client(self, client_socket: socket.socket, message: str) -> bool:
        """Helper to send a message following the protocol to a single client."""
        try:
            encoded_message = message.encode(self.FORMAT)
            message_length = len(encoded_message)
            send_length = str(message_length).encode(self.FORMAT)
            send_length += b' ' * (self.HEADER - len(send_length))

            client_socket.sendall(send_length) # Use sendall for reliability
            client_socket.sendall(encoded_message)  # Use sendall for reliability
        except Exception as e:
            # This client is likely disconnected, handle it
            address_for_log = self._connection_addresses.get(client_socket, "UNKNOWN_ADDR")
            print(f"[S][BROADCAST ERROR] Failed to send to client {address_for_log}: {e}")
            
            # Remove the problematic socket from the active connections
            with self._lock:
                if client_socket in self._active_connections:
                    self._active_connections.remove(client_socket)
                if client_socket in self._connection_addresses:
                    del self._connection_addresses[client_socket]
            try:
                client_socket.shutdown(socket.SHUT_RDWR) # Attempt graceful shutdown before close
                client_socket.close() # Ensure the socket is closed
            except OSError as close_err:
                print(f"[S][CLOSE ERROR] Error closing socket for {address_for_log}: {close_err}")
            return False # Indicate failure to send
        return True # Indicate success

    def broadcast_message(self, sender_socket: socket.socket, message: str):
        """Broadcasts a message to all clients except the sender."""
        with self._lock:
            # Create a copy of the set to iterate over
            connections_to_broadcast = list(self._active_connections)

        for client_socket in connections_to_broadcast:
            if client_socket != sender_socket: # Don't send back to the sender
                # _send_to_single_client will handle removal if sending fails
                self._send_to_single_client(client_socket, message)

Server().start()  # Example instantiation, can be removed if not needed or you want to use this class in another script.
