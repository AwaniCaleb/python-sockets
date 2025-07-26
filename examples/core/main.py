import random
import time
import threading

from .client import Client
from .server import Server
from utils.common import Intervals


# Function to encapsulate server startup
def start_server_thread():
    """Initializes and starts the server in a separate thread."""
    server_instance = Server()
    # The server.start() method has an infinite loop (while True). It will block the thread it's running in.
    server_instance.start()

def main():
    # Start the Server
    # Start it in a daemon thread so it runs in the background and doesn't prevent the main program from exiting.
    server_thread = threading.Thread(target=start_server_thread, daemon=True)
    server_thread.start()
    print("[MAIN] Server thread started.")

    # A moment to bind to the port and start listening
    time.sleep(1)

    # Initialize the Client
    cli = Client()

    # Set up the Message Sending Interval
    messages = [
        "Hello, how are you?",
        "What's the weather like today?",
        "Did you finish the report?",
        "Let's meet at 3 PM.",
        "Don't forget the meeting tomorrow.",
        "Happy Birthday!",
        "Good luck with your presentation!",
        "Can you send me the file?",
        "See you later!",
        "Have a great day!",
        "!DISCONNECT"  # Trigger the client to disconnect
    ]

    interval_manager = Intervals()
    send_messages_thread_name = interval_manager.set(
        lambda: cli.send(random.choice(messages)), 3
    )
    print(f"[MAIN] Message sending interval started (thread: {send_messages_thread_name}).")

    # Let the client run for a duration
    print("\n[MAIN] Client sending messages for 15 seconds...")
    time.sleep(15) # Allows multiple messages to be sent over time

    # Clean up
    print(f"\n[MAIN] Stopping message sending interval: {send_messages_thread_name}")
    interval_manager.stop(send_messages_thread_name) # Stop the interval thread first

    # Give the interval thread a moment to finish its last iteration and exit
    time.sleep(1)

    print("[MAIN] Disconnecting client.")
    cli.disconnect() # Disconnect the client's socket gracefully

    # Give a brief moment for all daemon threads to terminate before the main program exits
    time.sleep(2)
    print("[MAIN] Main program finished.")

if __name__ == "__main__":
    main()