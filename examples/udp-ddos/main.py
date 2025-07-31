from flooder import Flooder


def main():
    # Target your server's port for testing
    flooder = Flooder(target="localhost", port=12345)

    try:
        flooder.start(message=b"ATTACK!") # Send a specific message
    except KeyboardInterrupt:
        flooder.stop() # Ensure stop is called on Ctrl+C


if __name__ == "__main__":
    main()