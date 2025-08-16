# Raw Packet Tool

This project demonstrates how to manually construct and send network packets at a low level using raw sockets in Python. It includes a modular design for creating IP, ICMP, and TCP headers separately, making the code clean, organized, and extensible.

## Project Structure

The project is broken down into a few key files to follow a clean, modular design pattern.

  - **`main.py`**: The primary entry point of the application. It orchestrates the creation of different packet headers and sends the final packet over a raw socket.
  - **`PacketHeader.py`**: A base class that contains common functionalities shared across all packet headers, most notably the **checksum calculation** logic.
  - **`IpHeader.py`**: A class dedicated to building and packing the IP header.
  - **`IcmpHeader.py`**: A class dedicated to building and packing the ICMP header.
  - **`TcpHeader.py`**: A class dedicated to building and packing the TCP header.

## How to Run

1.  **Open a terminal** and navigate to the project directory.
2.  **Run the main script** with administrator privileges (required for raw sockets). On most systems, this can be done with `sudo`.
    ```bash
    sudo python main.py
    ```
3.  The script will attempt to send both an ICMP and a TCP packet to the loopback address (`127.0.0.1`).

## How to Test

To verify that your packets are being constructed correctly, you will need a packet analyzer.

1.  **Download and Install Wireshark**: [Wireshark](https://www.wireshark.org/download.html) is a free, open-source tool for network analysis. The installer for Windows includes a necessary driver called Npcap.
2.  **Capture on the Loopback Adapter**: Open Wireshark and select the **"Npcap Loopback Adapter"** to capture packets sent to `127.0.0.1`.
3.  **Run the Script**: Execute `main.py` with administrator privileges.
4.  **Analyze the Packets**: In Wireshark, use the display filters `icmp` or `tcp` to inspect the packets. Verify that the headers and their checksums are correct.

Check out this "[How to Capture Traffic in Wireshark](https://youtu.be/wI2qfO61iFw?si=vMwToGBtrsc2ohOc)" video by [
Plaintext Packets](https://www.youtube.com/@plaintextpackets). This is not an ad :)

## Dos and Don'ts

### Do's

  - **Maintain Modularity**: When adding new protocols (e.g., UDP or ARP), create a new class for each to keep the `main.py` file clean.
  - **Run as Administrator**: Remember that raw sockets require elevated privileges. Always run the script as an administrator or with `sudo`.
  - **Use a Packet Analyzer**: Always use a tool like Wireshark to verify that your manually constructed packets are correct. You can't trust that they're being sent correctly just because the script doesn't throw an error.

### Don'ts

  - **Don't use Relative Imports**: If you run a file directly, Python will throw an `ImportError`. Always use absolute imports like `from .IcmpHeader import IcmpHeader` to avoid this issue.
  - **Don't Forget Checksums**: Checksums are critical for packet integrity. If your checksum calculation is off, the receiving system will likely drop the packet. Always double-check this logic.
  - **Don't Forget Packet Headers**: When constructing a packet, the order is crucial: `IP Header -> Protocol Header -> Payload`. Reversing this order will lead to an unreadable packet.