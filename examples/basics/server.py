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
    _active_connections = [] # Use a list to store connection objects for potential future use (e.g., broadcasting)
    _lock = threading.Lock() # To protect access to _active_connections

    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.ADDR)
        print(f"[S][SERVER INITIALIZED] Server bound to {self.ADDR}")

    def start(self):
        """Starts the server and listens for incoming connections."""

        self.server.listen()
        print(f"[S][SERVER LISTENING] Listening on {self.SERVER}:{self.PORT}")

        while True:
            try:
                connection, address = self.server.accept()

                with self._lock:
                    self._active_connections.append((connection, address)) # Store connection for potential management
                
                print(f"[S][NEW CONNECTION] {address} connected")

                thread = threading.Thread(target=self.handle_client, args=(connection, address))
                thread.daemon = True # Make client threads daemon so they don't block main exit
                thread.start()

                print(f"[S][ACTIVE CONNECTIONS] {threading.active_count() - 1}") # -1 for the server's main thread

            except Exception as e:
                # Handle cases where server.accept() might fail
                print(f"[S][SERVER ACCEPT ERROR] {e}")

                break

    def handle_client(self, connection, address):
        """Handles communication with a connected client."""
        connected = True

        while connected:
            try:
                message_length_header = connection.recv(self.HEADER)
                # If recv returns 0 bytes, the client has closed its side of the connection gracefully

                if not message_length_header:
                    break # Exit loop, client disconnected

                message_length = int(message_length_header.decode(self.FORMAT).strip()) # .strip() removes padding
                message = connection.recv(message_length).decode(self.FORMAT)

                if message == self.DISCONNECT_MESSAGE:
                    connected = False
                
                print(f"[S][{address}] {message}")

                # send a response back to the client (Testing purpose)
                # response = "Message received!"
                # response_encoded = response.encode(self.FORMAT)
                # response_length = str(len(response_encoded)).encode(self.FORMAT)
                # response_length += b' ' * (self.HEADER - len(response_length))
                # connection.send(response_length)
                # connection.send(response_encoded)

            except ConnectionResetError:
                # Client forcefully closes the connection
                print(f"[S][FORCED DISCONNECT] {address} forcefully disconnected.")
                connected = False
            except Exception as e:
                # Catch potential errors
                print(f"[S][ERROR HANDLING {address}] {e}")
                connected = False # Disconnect client on any unhandled error

        connection.close()
        print(f"[S][DISCONNECTED] {address} disconnected")
        
        with self._lock:
            if (connection, address) in self._active_connections:
                self._active_connections.remove((connection, address))

        print(f"[S][ACTIVE CONNECTIONS] {threading.active_count() - 2}")