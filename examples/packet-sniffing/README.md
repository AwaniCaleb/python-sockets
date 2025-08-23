### 📝 Project Documentation & Notes

This repository contains two simple Python networking tools built using the **Scapy** library: a **Packet Sniffer** and a **Port Scanner**.

#### 📂 File Structure

  * `PacketSniffer.py`: Contains the code for the Packet Sniffer.
  * `PortScanner.py`: Contains the code for the Port Scanner.

#### 🛠️ Dependencies

You'll need the `scapy` library to run these scripts. You can install it using `pip`:

```bash
pip install scapy
```

You may also need to run the scripts with `sudo` to have the necessary permissions for raw socket access.

-----

### Packet Sniffer (`PacketSniffer.py`)

This script is a basic network packet analyzer. It captures live network traffic and prints information about each packet, such as its source and destination IP addresses and ports. It can also be configured to filter for specific types of traffic, like DNS queries.

#### Key Features

  * **Packet Capture**: Uses `scapy.sniff()` to capture packets from a specified network interface.
  * **Packet Analysis**: The `process_packet()` method acts as a callback to analyze each packet in real-time. It checks for the presence of different layers (`IP`, `TCP`, `UDP`, `DNSQR`) to extract relevant information.
  * **Protocol Identification**: Identifies and prints specific details for common protocols, including DNS queries.
  * **Filtering**: Supports Berkeley Packet Filter (BPF) strings to capture only specific types of traffic (e.g., `"udp port 53"`) for more efficient analysis.

#### Usage

To run the sniffer, simply execute the `PacketSniffer.py` script. You may need `sudo` for permissions.

```bash
sudo python3 PacketSniffer.py
```

The script is currently configured to sniff for 10 DNS packets by default.

-----

### Port Scanner (`PortScanner.py`)

This script is a simple port scanner that uses a **TCP SYN scan** to determine if a specific port on a target machine is open, closed, or filtered.

#### How It Works

1.  **Packet Crafting**: It builds a TCP SYN packet, which is the first step of a TCP three-way handshake, by combining `IP` and `TCP` layers with the `/` operator.
2.  **Packet Sending**: It uses `scapy.sr1()` to send the crafted packet to the target and wait for a single response. A timeout is used to prevent the script from waiting indefinitely for a response.
3.  **Response Analysis**: It analyzes the flags in the response packet to determine the port's status:
      * **Open Port**: The target responds with a **SYN/ACK** (`SA`) packet.
      * **Closed Port**: The target responds with a **RST/ACK** (`RA`) packet.
      * **Filtered Port**: No response is received within the timeout period. This is often due to a firewall silently dropping the packet.

#### Usage

The `PortScanner` class needs to be initialized with a target IP and a port. An example of how to use it would look like this:

```python
if __name__ == "__main__":
    scanner = PortScanner(target="scanme.nmap.org", port=80)
    scanner.scan_port()
```