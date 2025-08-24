### 📝 Scapy Examples: Packet Sniffer & Port Scanner

This directory contains simple Python networking tools built using the **Scapy** library. These examples are intended to demonstrate the power and simplicity of Scapy for crafting and manipulating network packets.

**Note on Port Scanners:** This directory contains a very basic port scanner (`PortScanner.py`) written with Scapy. It is designed as a simple proof-of-concept. For a more powerful, multi-threaded, and feature-rich port scanner, please see the example in the `../port-scanner/` directory.

#### 📂 File Structure

  * `main.py`: An interactive runner to execute the examples.
  * `PacketSniffer.py`: Contains the code for the Packet Sniffer.
  * `PortScanner.py`: Contains the code for the Scapy-based Port Scanner.

#### 🛠️ Dependencies

You'll need the `scapy` library to run these scripts. You can install it using `pip`:

```bash
pip install scapy
```

You may also need to run the scripts with `sudo` to have the necessary permissions for raw socket access.

-----

### Packet Sniffer (`PacketSniffer.py`)

This script is a basic network packet analyzer. It captures live network traffic and prints information about each packet.

#### Key Features

  * **Packet Capture**: Uses `scapy.sniff()` to capture packets.
  * **Packet Analysis**: The `process_packet()` method acts as a callback to analyze each packet in real-time.
  * **Filtering**: Supports BPF strings to capture specific traffic (e.g., `"udp port 53"`).

-----

### Port Scanner (`PortScanner.py`)

This script is a simple port scanner that uses a **TCP SYN scan** with Scapy to determine if a port is open, closed, or filtered.

#### How It Works

1.  **Packet Crafting**: Builds a TCP SYN packet using Scapy's `IP` and `TCP` layers.
2.  **Packet Sending**: Uses `scapy.sr1()` to send the packet and wait for a single response.
3.  **Response Analysis**: Analyzes the flags in the response to determine the port's status.

---

### Usage

To run the examples, execute the interactive `main.py` script. You may need `sudo` for permissions.

```bash
sudo python3 main.py
```

The script will prompt you to choose which example you want to run.