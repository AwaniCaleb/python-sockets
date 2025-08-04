import ssl
import socket
import threading # Hopefully I'd use this later

class Server():
    # Define constants for the server's host and port
    HOST = socket.gethostbyname(socket.gethostname())
    PORT = 9999
    ADDR = (HOST, PORT)

    def __init__(self):
        # Initialize an insecure socket using IPv4 and TCP
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_running = False

        # The secure socket will be stored here after wrapping later
        self.secure_socket = None

    def start(self):
        # Bind the insecure socket to the specified address and port
        self.socket.bind(self.ADDR)

        # Create an SSLContext object with the purpose of serving clients.
        # This will hold security settings and files.
        self.context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # Load our self-signed certificate and private key into the context.
        # These are the files we generated with the 'openssl' command... Remember?
        self.context.load_cert_chain(certfile="./id/cert.pem", keyfile="./id/key.pem")

        # Wrap our insecure socket with the secure SSL context.
        # The 'server_side=True' parameter indicates that this is a server socket.
        self.secure_socket = self.context.wrap_socket(self.socket, server_side=True)
        
        # We only need to call listen() once to prepare the socket to accept connections.
        self.secure_socket.listen()
        
        print(f"Secure server is listening on {self.HOST}:{self.PORT}")

        self.is_running = True

        # Continuously accept new client connections as long as we are running.
        while self.is_running:
            # Accept incoming connections
            connection, connection_addr = self.secure_socket.accept()

            print(f"Accepted connection from {connection_addr}")

            # Use a 'with' statement to automatically close the connection when we are done.
            with connection:
                # This inner loop handles communication with a single client.
                while True:
                    # Receive up to 1024 bytes of data from the client.
                    # This will block until data is received.
                    data = connection.recv(1024)

                    # If no data is received, it means the client has disconnected.
                    if not data:
                        print(f"Client {connection_addr} disconnected.")
                        break

                    # Decode the data and print it for our server's logs.
                    print(f"Received data from {connection_addr}: {data.decode('utf-8')}")

                    # Echo the exact same data back to the client.
                    connection.sendall(data)


if __name__ == "__main__":
    server = Server()
    server.start()