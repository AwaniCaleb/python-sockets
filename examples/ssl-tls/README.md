# Secure Echo Server and Client

This project is a simple, secure, and multi-threaded echo server and a corresponding client built in Python using the `socket` and `ssl` modules. The server listens for incoming connections, wraps them in an SSL/TLS layer for security, and echos back any message it receives from a connected client.

## Table of Contents

- [Project Goal](#project-goal)
- [Setup and Dependencies](#setup-and-dependencies)
- [How to Run](#how-to-run)
- [Key Concepts & Reminders](#key-concepts--reminders)
- [Best Practices: Do's and Don'ts](#best-practices-dos-and-donts)
- [Troubleshooting](#troubleshooting)

## Project Goal

The primary goal of this project was to learn the fundamentals of secure, concurrent network programming in Python by building a client-server application that uses SSL/TLS for encrypted communication.

## Setup and Dependencies

The project only requires the Python standard library. No external dependencies are needed.

Before running the server, you **must** generate your own self-signed SSL certificate and private key.

1.  Create a directory named `id` in the same location as your Python files.
2.  Run the following `openssl` command in your terminal to generate the files. When prompted for the **Common Name**, use the address you plan to connect to (e.g., `localhost` for local testing).

    ```bash
    openssl req -x509 -newkey rsa:4096 -keyout ./id/key.pem -out ./id/cert.pem -days 365 -nodes
    ```

## How to Run

1.  Start the server by running the `server.py` script:
    ```bash
    python server.py
    ```

2.  Start the client by running the `client.py` script in a separate terminal:
    ```bash
    python client.py
    ```
    The client will prompt you to enter messages, which will be sent securely to the server and echoed back.

## Key Concepts & Reminders

* **Socket:** The fundamental building block of network communication. We use a TCP socket (`socket.AF_INET`, `socket.SOCK_STREAM`) for a reliable, two-way connection.
* **SSLContext:** A container for all security-related settings, including certificates, keys, and security protocols.
* **SSL/TLS Handshake:** The process where the client and server agree on a secure connection. The server proves its identity with its certificate, which the client verifies.
* **`ssl.Purpose`:** This specifies the role of the `SSLContext`.
    * `ssl.Purpose.CLIENT_AUTH`: Used by the server to authenticate itself to clients.
    * `ssl.Purpose.SERVER_AUTH`: Used by the client to authenticate the server it is connecting to.
* **Threading:** We use a new thread for each client connection on the server. This prevents the server from blocking and allows it to handle multiple clients simultaneously.

## Best Practices: Do's and Don'ts

| Do's                                                                 | Don'ts                                                                           |
| -------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Do** use `try...except...finally` blocks for robust error handling.  | **Don't** hardcode your IP addresses and ports if possible.                      |
| **Do** ensure the `Common Name` in your certificate matches the host.  | **Don't** share your private key (`key.pem`). It's a secret!                     |
| **Do** close your sockets gracefully in a `finally` block.             | **Don't** handle all clients in the main thread

## Troubleshooting

* **`[SSL: CERTIFICATE_VERIFY_FAILED]`:** This almost always means the `Common Name` in your `cert.pem` file doesn't match the host address you're using in your client script (e.g., `localhost` vs. `192.168.56.1`). Regenerate your certificate and ensure the names match.
* **`[SSLV3_ALERT_BAD_CERTIFICATE]`:** This is a server-side error that occurs after a client has rejected its certificate, often due to the `CERTIFICATE_VERIFY_FAILED` error on the client side.
