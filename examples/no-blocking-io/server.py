import sys
import socket
import select

class Server():
    """
    A simple non-blocking TCP server that handles multiple clients
    concurrently using the `select` module for I/O multiplexing.
    """
    DEFAULT_HOST = '127.0.0.1'
    DEFAULT_PORT = 65432

    def __init__(self, host: str = None, port: int = None) -> None:
        """
        Initializes the server with a host and port.
        """
        # Main server socket for listening to new connections
        self.socket = None
        
        # Set host and port, using defaults if not provided
        self.host = host if host else self.DEFAULT_HOST
        self.port = port if port else self.DEFAULT_PORT
        
        # A list of all sockets we are monitoring for incoming data
        self.inputs = []

    def start(self):
        """
        Starts the non-blocking server and begins monitoring for connections.
        """
        # Create a new TCP/IP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set the main socket to non-blocking mode.
        self.socket.setblocking(False)

        self.addr = (self.host, self.port)

        try:
            # Bind the socket to the specified host and port
            self.socket.bind(self.addr)
        except socket.error as error:
            # Gracefully handle a bind error (e.g., port already in use)
            print(f"Bind failed. \nError Code: {str(error[0])} \nMessage: {str(error[1])}")
            sys.exit()
        
        # Put the socket in a listening state, with a backlog of 5 pending connections
        self.socket.listen(5)

        # Add the main server socket to the list of inputs to be monitored by `select`
        self.inputs.append(self.socket)

        print(f"Server listening on {self.host}:{self.port}")
        
        # The main event loop
        while self.inputs:
            # `select.select()` polls the list of sockets to see which are "ready"
            # It blocks until one or more sockets are readable, writable, or in an error state.
            # We are only interested in sockets with incoming data, so we use empty lists for write and error.
            readable, _, _ = select.select(self.inputs, [], [])
            
            # Iterate through the list of sockets that are ready to be read from
            for s in readable:
                # If the ready socket is our main server socket, it means a new client is connecting
                if s is self.socket:
                    # Accept the new connection
                    client_socket, client_addr = s.accept()
                    print(f"Accepted connection from {client_addr}")
                    
                    # Set the new client socket to non-blocking and add it to our monitored list
                    client_socket.setblocking(False)
                    self.inputs.append(client_socket)
                
                # If the ready socket is a client socket, it means there is data to be read
                else:
                    try:
                        # Read data from the client
                        data = s.recv(1024)
                        if data:
                            # If data is received, print it and echo it back to the client
                            print(f"Received data: {data.decode('utf-8')}")
                            s.send(data)
                        else:
                            # An empty `recv` result indicates a client has closed the connection
                            print(f"Closing connection from {s.getpeername()}")
                            # Clean up the closed connection from our list and close the socket
                            self.inputs.remove(s)
                            s.close()
                    except BlockingIOError:
                        # This can sometimes occur due to a race condition. It's safe to just pass.
                        pass
                    except Exception as e:
                        # Handle any other unexpected errors on a client socket
                        print(f"Error handling client data: {e}")
                        self.inputs.remove(s)
                        s.close()