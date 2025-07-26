# Python Socket Module Learning Journey

Welcome to my public repository dedicated to learning and mastering Python's `socket` module!

This repository serves as a personal learning log and a resource for anyone interested in understanding network programming with Python. As I progress through different socket concepts, I will be adding examples, notes, and utility functions here.

## Table of Contents

* [About This Repository](#about-this-repository)
* [Learning Roadmap](#learning-roadmap)
* [Getting Started](#getting-started)
    * [Prerequisites](#prerequisites)
    * [Setup](#setup)
    * [Running Examples](#running-examples)
* [Repository Structure](#repository-structure)
* [Contributing (Optional)](#contributing-optional)
* [License](#license)

## About This Repository

The goal of this repository is to systematically explore the Python `socket` module. I'll be covering:

* **TCP Sockets**: Connection-oriented communication.
* **UDP Sockets**: Connectionless datagram communication.
* **Blocking vs. Non-blocking Sockets**: Understanding I/O modes.
* **Handling Multiple Clients**: Using `select`, `selectors`, `threading`, and `asyncio`.
* **Error Handling**: Robust network applications.
* **Serialization**: Sending complex data over sockets.
* **Security**: Basic considerations (e.g., SSL/TLS).

Each concept will typically have its own dedicated example(s) within the `examples/` directory, along with accompanying notes in the `notes/` directory.

## Learning Roadmap

Here's a general outline of the topics I plan to cover, not really in any learning order:

1.  **Basic TCP Client-Server**: Establishing a simple connection and sending/receiving text.
2.  **UDP Datagrams**: Sending and receiving connectionless messages.
3.  **Handling Multiple Clients (Blocking)**: Simple server handling one client at a time.
4.  **Handling Multiple Clients (Non-blocking with `select`/`selectors`)**: Managing multiple connections efficiently.
5.  **Handling Multiple Clients (Threading/Multiprocessing)**: Concurrent server designs.
6.  **Asynchronous Sockets (`asyncio`)**: Modern asynchronous network programming.
7.  **Data Serialization**: Using `json`, `pickle`, or custom protocols.
8.  **Socket Options**: Customizing socket behavior.
9.  **Basic Error Handling and Robustness**.
10. **Introduction to SSL/TLS Sockets**: Securing network communication.

*(This roadmap will be updated as I progress.)*

## Getting Started

### Prerequisites

* Python 3.x (recommended 3.8+)

### Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/awanicaleb/python-sockets.git](https://github.com/awanicaleb/python-sockets.git)
    cd python-sockets
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows:
    # .\venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate
    ```
3.  **Install dependencies (if any, though `socket` is built-in):**
    ```bash
    pip install -r requirements.txt # (Create this file if you add external libraries later)
    ```

### Running Examples

Each example directory will typically contain a `client.py` and `server.py` file.

To run an example:

1.  Navigate to the specific example directory:
    ```bash
    cd examples/01_basic_tcp_or_smth/
    ```
2.  Open two separate terminal windows.
3.  In the first terminal, start the server:
    ```bash
    python server.py
    ```
4.  In the second terminal, start the client:
    ```bash
    python client.py
    ```
    Follow any specific instructions provided within the example files themselves.

## Repository Structure

(See the detailed structure diagram at the top of this README.)

## Contributing (Optional)

While this is primarily a personal learning repository, I welcome suggestions, corrections, and constructive feedback!

* **Suggestions**: If you have ideas for topics to cover or improvements to existing examples, feel free to open an issue.
* **Corrections**: If you spot an error in my code or notes, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
