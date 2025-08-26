import socket

class Main:
    """
    A simple class to demonstrate a non-blocking socket client.
    """
    def __init__(self):
        self.socket = None
        self.running = False

    def start(self):
        """
        Initializes and starts the non-blocking socket connection.
        """
        # Create a new TCP/IP socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Set the socket to non-blocking mode.
        self.socket.setblocking(False)

        print("Socket created and set to non-blocking mode.")
        
        try:            
            # Attempt to receive data. Since there is no data, this will raise a BlockingIOError.
            data = self.socket.recv(1024)
            
            # If we reach this line, it means data was received.
            print(f"Received data: {data.decode('utf-8')}")

        except BlockingIOError as e:
            # When no data is immediately available.
            print(f"No data available, as expected. Error: {e}")

        except Exception as e:
            # A general exception handler for any other unexpected errors.
            print(f"An unexpected error occurred: {e}")
            
        finally:
            # It's important to close the socket to release system resources.
            # This ensures proper cleanup whether an error occurred or not.
            self.socket.close()


if __name__ == '__main__':
    app = Main()
    app.start()